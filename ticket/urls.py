from django.urls import path
from . import views

urlpatterns = [
    path('', views.TicketListView.as_view(), name='liste_tickets'),
    path('export-pdf/', views.export_tickets_pdf, name='export_tickets_pdf'),
    path('creer/', views.TicketCreateView.as_view(), name='creer_ticket'),
    path('assigner/<int:pk>/', views.TicketAssignView.as_view(), name='assigner_ticket'),
]
