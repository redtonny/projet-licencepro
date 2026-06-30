from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.get_notifications, name='liste'),
    path('<int:notif_id>/lu/', views.marquer_lu, name='marquer_lu'),
    path('tout-lu/', views.marquer_tout_lu, name='tout_lu'),
]