from django.urls import path
from . import views

urlpatterns = [
    path("equipements/", views.liste_equipements, name="liste_equipements"),
    path("equipements/export-pdf/", views.export_equipements_pdf, name="export_equipements_pdf"),
    path("equipements/nouveau/", views.creer_equipement, name="creer_equipement"),
    path("equipements/<int:pk>/modifier/", views.editer_equipement, name="editer_equipement"),

    path("types-equipement/nouveau/", views.creer_type_equipement, name="creer_type_equipement"),
    path("etats/nouveau/", views.creer_etat, name="creer_etat"),

    path("equipements/<int:pk>/supprimer/", views.supprimer_equipement, name="supprimer_equipement"),
]