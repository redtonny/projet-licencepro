from .models import Notification

def creer_notification(destinataire, message, type='ticket', lien=''):
    Notification.objects.create(
        destinataire=destinataire,
        message=message,
        type=type,
        lien=lien,
    )