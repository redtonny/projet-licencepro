from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Equipement, TypeEquipement, Etat
from .forms import EquipementForm, TypeEquipementForm, EtatForm


@login_required
def liste_equipements(request):
    if getattr(request.user, "role", "").strip() != "admin":
        return redirect("liste_tickets")
    equipements = Equipement.objects.select_related("type_equipement", "etat")
    context = {"equipements": equipements}
    return render(request, "Parcinfo/liste_equipements.html", context)


@login_required
def creer_equipement(request):
    if getattr(request.user, "role", "").strip() != "admin":
        raise PermissionDenied("Vous n'êtes pas autorisé à créer des équipements.")
    if request.method == "POST":
        form = EquipementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Équipement créé avec succès.")
            return redirect("liste_equipements")
    else:
        form = EquipementForm()
    return render(request, "Parcinfo/form_equipement.html", {"form": form})


@login_required
def editer_equipement(request, pk):
    if getattr(request.user, "role", "").strip() != "admin":
        raise PermissionDenied("Vous n'êtes pas autorisé à modifier des équipements.")
    equipement = get_object_or_404(Equipement, pk=pk)
    if request.method == "POST":
        form = EquipementForm(request.POST, instance=equipement)
        if form.is_valid():
            form.save()
            messages.success(request, "Équipement mis à jour avec succès.")
            return redirect("liste_equipements")
    else:
        form = EquipementForm(instance=equipement)
    return render(request, "Parcinfo/form_equipement.html", {"form": form, "equipement": equipement})


@login_required
def creer_type_equipement(request):
    if getattr(request.user, "role", "").strip() != "admin":
        raise PermissionDenied("Vous n'êtes pas autorisé à créer des types d'équipement.")
    if request.method == "POST":
        form = TypeEquipementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Type d'équipement créé avec succès.")
            return redirect("creer_equipement")
    else:
        form = TypeEquipementForm()
    return render(request, "Parcinfo/form_type_equipement.html", {"form": form})


@login_required
def creer_etat(request):
    if getattr(request.user, "role", "").strip() != "admin":
        raise PermissionDenied("Vous n'êtes pas autorisé à créer des états d'équipement.")
    if request.method == "POST":
        form = EtatForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "État d'équipement créé avec succès.")
            return redirect("creer_equipement")
    else:
        form = EtatForm()
    return render(request, "Parcinfo/form_etat.html", {"form": form})


@login_required
def supprimer_equipement(request, pk):
    if getattr(request.user, "role", "").strip() != "admin":
        raise PermissionDenied("Vous n'êtes pas autorisé à supprimer des équipements.")

    equipement = get_object_or_404(Equipement, pk=pk)

    if request.method == "POST":
        equipement.delete()
        messages.success(request, "Équipement supprimé avec succès.")
        return redirect("liste_equipements")

    return render(
        request,
        "Parcinfo/confirmer_supprimer_equipement.html",
        {"equipement": equipement},
    )
