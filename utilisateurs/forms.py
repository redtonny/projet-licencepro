from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Utilisateur, Departement


BASE_INPUT_CLASS = "border rounded px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-900"


class UtilisateurCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Utilisateur
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "departement",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_classes} {BASE_INPUT_CLASS}".strip()


class DepartementForm(forms.ModelForm):
    class Meta:
        model = Departement
        fields = ["nom"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_classes} {BASE_INPUT_CLASS}".strip()


class UtilisateurAdminEditForm(forms.ModelForm):
    """
    Formulaire utilisé par l'admin pour gérer les comptes utilisateur/technicien.
    """

    class Meta:
        model = Utilisateur
        fields = ["username", "first_name", "last_name", "email", "role", "departement", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_classes} {BASE_INPUT_CLASS}".strip()
