from django import forms
from .models import Equipement, TypeEquipement, Etat
from utilisateurs.models import Departement, Utilisateur

BASE_INPUT_CLASS = "border rounded px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500"


class EquipementForm(forms.ModelForm):
    class Meta:
        model = Equipement
        fields = ["nom", "numero_serie", "type_equipement", "etat", "departement", "utilisateur", "date_achat", "description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['departement'].queryset = Departement.objects.all()
        self.fields['utilisateur'].queryset = Utilisateur.objects.filter(role__in=['utilisateur', 'technicien'])
        for name, field in self.fields.items():
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_classes} {BASE_INPUT_CLASS}".strip()


class TypeEquipementForm(forms.ModelForm):
    class Meta:
        model = TypeEquipement
        fields = ["nom"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_classes} {BASE_INPUT_CLASS}".strip()


class EtatForm(forms.ModelForm):
    class Meta:
        model = Etat
        fields = ["nom"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_classes} {BASE_INPUT_CLASS}".strip()

