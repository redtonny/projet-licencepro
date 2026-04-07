from django.urls import path
from . import views


urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('after-login/', views.after_login, name='after_login'),
    path('utilisateurs/nouveau/', views.creer_utilisateur, name='creer_utilisateur'),
    path('utilisateurs/gerer/', views.gerer_utilisateurs, name='gerer_utilisateurs'),
    path('utilisateurs/<int:pk>/editer/', views.editer_utilisateur, name='editer_utilisateur'),
    path('utilisateurs/<int:pk>/supprimer/', views.supprimer_utilisateur, name='supprimer_utilisateur'),
    path('departements/nouveau/', views.creer_departement, name='creer_departement'),
    path('logout/', views.custom_logout, name='custom_logout'),
]