from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def get_notifications(request):
    notifications = Notification.objects.filter(
        destinataire=request.user
    )[:10]

    data = [{
        'id': n.id,
        'message': n.message,
        'type': n.type,
        'lien': n.lien,
        'lu': n.lu,
        'date': n.date_creation.strftime('%d/%m/%Y %H:%M'),
    } for n in notifications]

    nb_non_lues = Notification.objects.filter(
        destinataire=request.user, lu=False
    ).count()

    return JsonResponse({'notifications': data, 'nb_non_lues': nb_non_lues})


@login_required
def marquer_lu(request, notif_id):
    Notification.objects.filter(
        id=notif_id, destinataire=request.user
    ).update(lu=True)
    return JsonResponse({'status': 'ok'})


@login_required
def marquer_tout_lu(request):
    Notification.objects.filter(
        destinataire=request.user, lu=False
    ).update(lu=True)
    return JsonResponse({'status': 'ok'})