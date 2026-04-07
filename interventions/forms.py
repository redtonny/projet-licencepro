from django import forms
from .models import Intervention, TypeIntervention
from ticket.models import Ticket

BASE_INPUT_CLASS = "border rounded px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500"


class InterventionForm(forms.ModelForm):
    class Meta:
        model = Intervention
        fields = ["ticket", "description", "est_termine"]

    def __init__(self, *args, **kwargs):
        technicien_user = kwargs.pop("technicien_user", None)
        exclude_existing = kwargs.pop("exclude_existing", False)
        super().__init__(*args, **kwargs)

        # Limiter le choix du ticket au technicien assigné
        if technicien_user:
            qs = Ticket.objects.filter(technicien=technicien_user)
            if exclude_existing:
                qs = qs.filter(intervention__isnull=True)
            self.fields["ticket"].queryset = qs
        else:
            self.fields["ticket"].queryset = Ticket.objects.none()

        # Styliser les champs
        for _, field in self.fields.items():
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_classes} {BASE_INPUT_CLASS}".strip()

        self.fields["description"].widget.attrs.setdefault("placeholder", "Décrivez le travail effectué…")


class TypeInterventionForm(forms.ModelForm):
    class Meta:
        model = TypeIntervention
        fields = ["nom"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_classes} {BASE_INPUT_CLASS}".strip()
