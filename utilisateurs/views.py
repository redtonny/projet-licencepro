from ticket.models import Ticket
from interventions.models import Intervention
from django.db.models import Count
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.views.decorators.http import require_POST
from .forms import UtilisateurCreationForm, DepartementForm, UtilisateurAdminEditForm
from .models import Utilisateur
from django.core.exceptions import PermissionDenied



@login_required
def dashboard(request):
    # Le dashboard est réservé aux administrateurs.
    if not (getattr(request.user, "role", "").strip() == "admin"):
        return redirect("liste_tickets")

    total_tickets = Ticket.objects.count()
    tickets_ouverts = Ticket.objects.filter(statut="ouvert").count()
    tickets_en_cours = Ticket.objects.filter(statut="en_cours").count()
    tickets_fermes = Ticket.objects.filter(statut="ferme").count()

    interventions_terminees = Intervention.objects.filter(est_termine=True).count()
    interventions_en_cours = Intervention.objects.filter(est_termine=False).count()

    # Top techniciens
    techniciens = (
        Intervention.objects.values("technicien__username")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )

    # Vues récentes (au moins 2)
    recent_tickets = Ticket.objects.select_related("utilisateur", "equipement") \
        .order_by("-date_creation")[:2]
    recent_interventions = Intervention.objects.select_related("ticket", "technicien") \
        .order_by("-date_intervention")[:2]

    # Aperçu utilisateurs
    users_utilisateur = Utilisateur.objects.filter(role="utilisateur").count()
    users_technicien = Utilisateur.objects.filter(role="technicien").count()
    users_utilisateur_actifs = Utilisateur.objects.filter(role="utilisateur", is_active=True).count()
    users_technicien_actifs = Utilisateur.objects.filter(role="technicien", is_active=True).count()
    users_total = users_utilisateur + users_technicien

    # Popup / notification de bienvenue une seule fois par session
    if not request.session.get("has_seen_welcome", False):
        messages.success(request, f"Bienvenue {request.user.username} !")
        request.session["has_seen_welcome"] = True

    context = {
        "total_tickets": total_tickets,
        "tickets_ouverts": tickets_ouverts,
        "tickets_en_cours": tickets_en_cours,
        "tickets_fermes": tickets_fermes,
        "interventions_terminees": interventions_terminees,
        "interventions_en_cours": interventions_en_cours,
        "techniciens": techniciens,
        "recent_tickets": recent_tickets,
        "recent_interventions": recent_interventions,
        "users_utilisateur": users_utilisateur,
        "users_technicien": users_technicien,
        "users_total": users_total,
        "users_utilisateur_actifs": users_utilisateur_actifs,
        "users_technicien_actifs": users_technicien_actifs,
    }

    return render(request, "registration/dashboard.html", context)

def connexion(request):

    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"]
        )

        if user is not None:
            login(request, user)

            messages.success(
                request,
                f"Bienvenue {request.user.username}, connexion réussie!"
            )

            return redirect("dashboard")

@login_required
def after_login(request):
    """
    Redirection automatique après login :
    - admin -> dashboard
    - technicien/utilisateur -> menu tickets
    """
    if getattr(request.user, "role", "").strip() == "admin":
        return redirect("dashboard")
    
    return redirect("liste_tickets")


@login_required
def creer_utilisateur(request):
    # Réservé aux admins
    if not (request.user.is_superuser or getattr(request.user, "role", "").strip() == "admin"):
        messages.error(request, "Vous n'êtes pas autorisé à créer des utilisateurs.")
        return redirect("dashboard")

    if request.method == "POST":
        form = UtilisateurCreationForm(request.POST)
        if form.is_valid():
            # L'admin ne crée que des comptes "utilisateur" ou "technicien"
            created_role = form.cleaned_data.get("role")
            if created_role not in ("utilisateur", "technicien"):
                messages.error(request, "Le rôle créé doit être 'utilisateur' ou 'technicien'.")
                return render(request, "utilisateurs/creer_utilisateur.html", {"form": form})
            form.save()
            messages.success(request, "Utilisateur créé avec succès.")
            return redirect("gerer_utilisateurs")
    else:
        form = UtilisateurCreationForm()

    return render(request, "utilisateurs/creer_utilisateur.html", {"form": form})


@login_required
def gerer_utilisateurs(request):
    if getattr(request.user, "role", "").strip() != "admin":
        raise PermissionDenied("Vous n'êtes pas autorisé à gérer les utilisateurs.")

    utilisateurs = Utilisateur.objects.filter(role__in=("utilisateur", "technicien")).select_related("departement").order_by("username")
    context = {"utilisateurs": utilisateurs}
    return render(request, "utilisateurs/gerer_utilisateurs.html", context)


@login_required
def editer_utilisateur(request, pk):
    if getattr(request.user, "role", "").strip() != "admin":
        raise PermissionDenied("Vous n'êtes pas autorisé à modifier des utilisateurs.")

    user_to_edit = Utilisateur.objects.filter(pk=pk, role__in=("utilisateur", "technicien")).first()
    if not user_to_edit:
        raise PermissionDenied("Utilisateur introuvable ou non autorisé.")

    if request.method == "POST":
        form = UtilisateurAdminEditForm(request.POST, instance=user_to_edit)
        if form.is_valid():
            form.save()
            messages.success(request, "Utilisateur modifié avec succès.")
            return redirect("gerer_utilisateurs")
    else:
        form = UtilisateurAdminEditForm(instance=user_to_edit)

    return render(request, "utilisateurs/form_utilisateur_admin.html", {"form": form, "user_to_edit": user_to_edit})


@login_required
def supprimer_utilisateur(request, pk):
    if getattr(request.user, "role", "").strip() != "admin":
        raise PermissionDenied("Vous n'êtes pas autorisé à supprimer des utilisateurs.")

    user_to_delete = Utilisateur.objects.filter(pk=pk, role__in=("utilisateur", "technicien")).first()
    if not user_to_delete:
        raise PermissionDenied("Utilisateur introuvable ou non autorisé.")

    if request.method == "POST":
        user_to_delete.delete()
        messages.success(request, "Utilisateur supprimé avec succès.")
        return redirect("gerer_utilisateurs")

    return render(
        request,
        "utilisateurs/confirmer_supprimer_utilisateur.html",
        {"user_to_delete": user_to_delete},
    )


@login_required
def creer_departement(request):
    # Réservé aux admins
    if not (request.user.is_superuser or getattr(request.user, "role", "").strip() == "admin"):
        messages.error(request, "Vous n'êtes pas autorisé à créer des départements.")
        return redirect("dashboard")

    if request.method == "POST":
        form = DepartementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Département créé avec succès.")
            return redirect("creer_utilisateur")
    else:
        form = DepartementForm()

    return render(request, "utilisateurs/creer_departement.html", {"form": form})


@require_POST
@login_required
def custom_logout(request):
    """
    Déconnexion (protégée par CSRF : la requête doit être POST).
    """
    logout(request)
    messages.success(request, "Bonjour et bienvenue sur votre plateforme.")
    return redirect("login")
