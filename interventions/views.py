from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
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
def export_interventions_pdf(request):
    role = getattr(request.user, "role", "").strip()
    interventions = Intervention.objects.select_related("ticket", "technicien")

    if role == "admin":
        pass
    elif role == "technicien":
        interventions = interventions.filter(technicien=request.user)
    else:
        return redirect("liste_tickets")

    headers = ["ID", "Ticket", "Technicien", "Date intervention", "Terminé"]
    rows = [
        [
            str(intervention.id),
            intervention.ticket.titre,
            intervention.technicien.username if intervention.technicien else "-",
            intervention.date_intervention.strftime("%d/%m/%Y %H:%M"),
            "Oui" if intervention.est_termine else "Non",
        ]
        for intervention in interventions
    ]
    return build_pdf_response("interventions.pdf", "Liste des interventions", headers, rows, request.user)
