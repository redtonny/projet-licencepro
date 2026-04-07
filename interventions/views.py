from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Intervention, TypeIntervention
from .forms import InterventionForm, TypeInterventionForm
from ticket.models import Ticket


@login_required
def liste_interventions(request):
    # Un admin voit tout, un technicien voit ses interventions, un utilisateur voit celles liées à ses tickets
    qs = Intervention.objects.select_related("ticket", "technicien")
    role = getattr(request.user, "role", "").strip()

    if role == "admin":
        pass
    elif role == "technicien":
        qs = qs.filter(technicien=request.user)
    else:
        # Les utilisateurs standard n'ont pas accès au menu interventions
        return redirect("liste_tickets")

    context = {"interventions": qs}
    return render(request, "interventions/liste_interventions.html", context)


@login_required
def creer_intervention(request):
    # Seul le technicien assigné peut créer une intervention
    role = getattr(request.user, "role", "").strip()
    if role != "technicien":
        raise PermissionDenied("Vous n'êtes pas autorisé à créer des interventions.")

    if request.method == "POST":
        form = InterventionForm(
            request.POST,
            technicien_user=request.user,
            exclude_existing=True,
        )
        if form.is_valid():
            intervention = form.save(commit=False)
            intervention.technicien = request.user
            intervention.save()
            messages.success(request, "Intervention créée avec succès.")
            return redirect("liste_interventions")
    else:
        form = InterventionForm(
            technicien_user=request.user,
            exclude_existing=True,
        )
    return render(request, "interventions/form_intervention.html", {"form": form})


@login_required
def editer_intervention(request, pk):
    intervention = get_object_or_404(Intervention, pk=pk)

    role = getattr(request.user, "role", "").strip()
    if role != "technicien":
        raise PermissionDenied("Vous n'êtes pas autorisé à modifier des interventions.")
    if intervention.technicien != request.user:
        raise PermissionDenied("Vous ne pouvez modifier que vos interventions.")

    if request.method == "POST":
        form = InterventionForm(
            request.POST,
            instance=intervention,
            technicien_user=request.user,
            exclude_existing=False,
        )
        # Le technicien ne peut pas changer le ticket.
        form.fields["ticket"].disabled = True
        form.fields["ticket"].required = False
        if form.is_valid():
            form.save()
            messages.success(request, "Intervention mise à jour avec succès.")
            return redirect("liste_interventions")
    else:
        form = InterventionForm(
            instance=intervention,
            technicien_user=request.user,
            exclude_existing=False,
        )
        form.fields["ticket"].disabled = True
        form.fields["ticket"].required = False
    return render(
        request,
        "interventions/form_intervention.html",
        {"form": form, "intervention": intervention},
    )


@login_required
def creer_type_intervention(request):
    # réservé aux admins
    role = getattr(request.user, "role", "").strip()
    if role not in ("technicien", "admin"):
        raise PermissionDenied("Vous n'êtes pas autorisé à créer des types d'intervention.")

    if request.method == "POST":
        form = TypeInterventionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Type d'intervention créé avec succès.")
            return redirect("creer_intervention")
    else:
        form = TypeInterventionForm()
    return render(request, "interventions/form_type_intervention.html", {"form": form})
