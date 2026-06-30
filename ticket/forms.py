from django import forms
from .models import Ticket
from utilisateurs.models import Utilisateur


BASE_INPUT_CLASS = "border rounded px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500"


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = [
            "titre",
            "description",
            "equipement",
            "type_demande",
            "departement",
            "priorite",
        ]

    def __init__(self, *args, **kwargs):
        # On passe éventuellement l'utilisateur pour la logique métier
        self.utilisateur = kwargs.pop("utilisateur", None)
        super().__init__(*args, **kwargs)

        # Styliser les champs
        for name, field in self.fields.items():
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_classes} {BASE_INPUT_CLASS}".strip()

        # Placeholders plus explicites
        self.fields["titre"].widget.attrs.setdefault("placeholder", "Sujet de votre demande")
        self.fields["description"].widget.attrs.setdefault("placeholder", "Décrivez le problème ou la demande…")

    def clean(self):
        cleaned_data = super().clean()
        equipement = cleaned_data.get("equipement")
        type_demande = cleaned_data.get("type_demande")

        # Règles métier : on force la présence de ces champs
        errors = {}
        if equipement is None:
            errors["equipement"] = "Veuillez sélectionner un équipement concerné."
        if type_demande is None:
            errors["type_demande"] = "Veuillez préciser le type de demande."

        if errors:
            for field, message in errors.items():
                self.add_error(field, message)

        return cleaned_data


class AssignationForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["technicien", "statut"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer ici au lieu de limit_choices_to
        self.fields["technicien"].queryset = Utilisateur.objects.filter(role="technicien")

        for name, field in self.fields.items():
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_classes} {BASE_INPUT_CLASS}".strip()
