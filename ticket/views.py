from io import BytesIO
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from .models import Ticket
from .forms import TicketForm, AssignationForm
from utilisateurs.models import Utilisateur


class TicketPermissionMixin(UserPassesTestMixin):
    """Permission par role pour tickets"""
    
    def test_func(self):
        role = getattr(self.request.user, "role", "").strip()
        return role in ("admin", "technicien", "utilisateur")


class TicketListView(LoginRequiredMixin, TicketPermissionMixin, ListView):
    model = Ticket
    template_name = "ticket/liste.html"
    context_object_name = "tickets"
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, "role", "").strip()
        
        if role == "admin":
            return Ticket.objects.all()
        elif role == "technicien":
            # Les tickets sans technicien ne doivent plus être visibles :
            # l'assignation est réservée à l'administrateur.
            return Ticket.objects.filter(technicien=user)
        else:  # utilisateur
            return Ticket.objects.filter(utilisateur=user)


class TicketCreateView(LoginRequiredMixin, TicketPermissionMixin, CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = "ticket/creation.html"
    success_url = reverse_lazy("liste_tickets")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["utilisateur"] = self.request.user
        return kwargs

    def form_valid(self, form):
        ticket = form.save(commit=False)
        ticket.utilisateur = self.request.user
        departement = getattr(self.request.user, "departement", None)
        if departement:
            ticket.departement = departement.nom
        ticket.statut = "ouvert"
        
        from django.utils import timezone
        today = timezone.now().strftime('%Y%m%d')
        count = Ticket.objects.filter(date_creation__date=timezone.now().date()).count() + 1
        ticket.numero_ticket = f"TICKET-{today}-{count:03d}"
        ticket.save()

        # Notifier uniquement les admins
        from notifications.utils import creer_notification
        admins = Utilisateur.objects.filter(role='admin')
        for admin in admins:
            creer_notification(
                destinataire=admin,
                message=f"Nouveau ticket #{ticket.numero_ticket} — {ticket.titre}",
                type='ticket',
                lien=f"/ticket/assigner/{ticket.id}/",
            )

        messages.success(self.request, f"Ticket créé avec succès. Numéro: {ticket.numero_ticket}")
        return super().form_valid(form)


class TicketAssignView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Ticket
    form_class = AssignationForm
    template_name = "ticket/assigner_ticket.html"
    pk_url_kwarg = "pk"
    success_url = reverse_lazy("liste_tickets")

    def test_func(self):
        role = getattr(self.request.user, "role", "").strip()
        return role == "admin"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ticket"] = self.object
        return context

    def form_valid(self, form):
        ticket = form.save(commit=False)
        ancien_technicien = Ticket.objects.get(pk=ticket.pk).technicien

        ticket.save()

        # Notifier le technicien uniquement s'il vient d'être assigné
        from notifications.utils import creer_notification
        if ticket.technicien and ticket.technicien != ancien_technicien:
            creer_notification(
                destinataire=ticket.technicien,
                message=f"Ticket #{ticket.numero_ticket} — {ticket.titre} vous a été assigné",
                type='ticket',
                lien=f"ticket/assigner_ticket.html",  
            )

        messages.success(self.request, "Ticket assigné / mis à jour avec succès.")
        return super().form_valid(form)


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
def export_tickets_pdf(request):
    role = getattr(request.user, "role", "").strip()
    tickets = Ticket.objects.select_related("utilisateur", "equipement", "type_demande")
    if role == "admin":
        pass
    elif role == "technicien":
        tickets = tickets.filter(technicien=request.user)
    else:
        tickets = tickets.filter(utilisateur=request.user)

    headers = [
        "Numéro",
        "Titre",
        "Utilisateur",
        "Département",
        "Statut",
        "Priorité",
        "Date création",
        "Technicien",
    ]
    rows = [
        [
            ticket.numero_ticket or str(ticket.id),
            ticket.titre,
            ticket.utilisateur.username,
            ticket.departement or "-",
            ticket.get_statut_display() if hasattr(ticket, "get_statut_display") else ticket.statut,
            ticket.get_priorite_display() if hasattr(ticket, "get_priorite_display") else ticket.priorite,
            ticket.date_creation.strftime("%d/%m/%Y %H:%M"),
            ticket.technicien.username if ticket.technicien else "-",
        ]
        for ticket in tickets
    ]
    return build_pdf_response("tickets.pdf", "Liste des tickets", headers, rows, request.user)