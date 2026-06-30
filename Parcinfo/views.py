from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from .models import Equipement, TypeEquipement, Etat
from .forms import EquipementForm, TypeEquipementForm, EtatForm


@login_required
def liste_equipements(request):
    if getattr(request.user, "role", "").strip() != "admin":
        return redirect("liste_tickets")
    equipements = Equipement.objects.select_related("type_equipement", "etat", "departement", "utilisateur")
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


def build_pdf_response(filename, title, headers, rows, user):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(title, styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"Exporté par : {user.username}", styles["Normal"]),
        Paragraph(f"Date d'export : {timezone.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]),
        Spacer(1, 12),
    ]
    data = [headers] + rows
    table = Table(data, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
    ]))
    story.append(table)
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@login_required
def export_equipements_pdf(request):
    if getattr(request.user, "role", "").strip() != "admin":
        return redirect("liste_tickets")

    equipements = Equipement.objects.select_related(
        "type_equipement",
        "etat",
        "departement",
        "utilisateur",
    )
    headers = ["Nom", "Numéro de série", "Type", "État", "Département", "Utilisateur", "Date d'achat", "Description"]
    rows = [
        [
            equipement.nom,
            equipement.numero_serie,
            equipement.type_equipement.nom,
            equipement.etat.nom if equipement.etat else "-",
            equipement.departement.nom if equipement.departement else "-",
            equipement.utilisateur.username if equipement.utilisateur else "-",
            equipement.date_achat.strftime("%d/%m/%Y") if equipement.date_achat else "-",
            equipement.description,
        ]
        for equipement in equipements
    ]
    return build_pdf_response("equipements.pdf", "Liste des équipements", headers, rows, request.user)
