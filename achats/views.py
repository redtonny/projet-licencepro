from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Commande, Fournisseur, LigneCommande
from .forms import FournisseurForm, CommandeForm, LigneCommandeForm
from django.core.exceptions import PermissionDenied


@login_required
def liste_fournisseurs(request):
    if getattr(request.user, "role", "").strip() != "admin":
        raise PermissionDenied("Vous n'êtes pas autorisé à accéder aux achats.")
    fournisseurs = Fournisseur.objects.all()
    return render(request, "achats/liste_fournisseurs.html", {"fournisseurs": fournisseurs})


@login_required
def creer_fournisseur(request):
    if getattr(request.user, "role", "").strip() != "admin":
        raise PermissionDenied("Vous n'êtes pas autorisé à créer des fournisseurs.")
    if request.method == "POST":
        form = FournisseurForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Fournisseur créé avec succès.")
            return redirect("liste_fournisseurs")
    else:
        form = FournisseurForm()
    return render(request, "achats/form_fournisseur.html", {"form": form})


@login_required
def liste_commandes(request):
    if getattr(request.user, "role", "").strip() != "admin":
        raise PermissionDenied("Vous n'êtes pas autorisé à accéder aux commandes.")
    commandes = Commande.objects.select_related("fournisseur", "ticket")
    return render(request, "achats/liste_commandes.html", {"commandes": commandes})


@login_required
def creer_commande(request):
    if getattr(request.user, "role", "").strip() != "admin":
        raise PermissionDenied("Vous n'êtes pas autorisé à créer des commandes.")
    if request.method == "POST":
        form = CommandeForm(request.POST)
        if form.is_valid():
            commande = form.save()
            messages.success(request, "Commande créée avec succès.")
            return redirect("liste_commandes")
    else:
        form = CommandeForm()
    return render(request, "achats/form_commande.html", {"form": form})

