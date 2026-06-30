from django.urls import path
from . import views

urlpatterns = [
    path("interventions/", views.liste_interventions, name="liste_interventions"),
    path("interventions/export-pdf/", views.export_interventions_pdf, name="export_interventions_pdf"),
    path("interventions/nouvelle/", views.creer_intervention, name="creer_intervention"),
    path("interventions/<int:pk>/modifier/", views.editer_intervention, name="editer_intervention"),

    path("types-intervention/nouveau/", views.creer_type_intervention, name="creer_type_intervention"),
]