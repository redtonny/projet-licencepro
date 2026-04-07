from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Ticket
from .forms import TicketForm, AssignationForm
from utilisateurs.models import Utilisateur
from django.db.models import Q


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
        ticket.save()
        messages.success(self.request, "Ticket créé avec succès.")
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
        messages.success(self.request, "Ticket assigné / mis à jour avec succès.")
        return super().form_valid(form)
