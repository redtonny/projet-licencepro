from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Ticket, Notification
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(pre_save, sender=Ticket)
def store_old_technicien(sender, instance, **kwargs):
    """Sauvegarde l'ancien technicien avant la mise à jour"""
    if instance.pk:
        try:
            old = sender.objects.get(pk=instance.pk)
            instance._old_technicien = old.technicien
        except sender.DoesNotExist:
            instance._old_technicien = None
    else:
        instance._old_technicien = None

@receiver(post_save, sender=Ticket)
def ticket_notification(sender, instance, created, **kwargs):
    if created:
        # Notifier tous les admins à la création
        admins = User.objects.filter(role='admin')
        Notification.objects.bulk_create([
            Notification(
                user=admin,
                ticket=instance,
                message=f"Nouveau ticket créé: {instance.numero_ticket} - {instance.titre}"
            )
            for admin in admins
        ])
    else:
        # Détecter le changement de technicien grâce à pre_save
        old_technicien = getattr(instance, '_old_technicien', None)
        if old_technicien != instance.technicien and instance.technicien:
            Notification.objects.create(
                user=instance.technicien,
                ticket=instance,
                message=f"Ticket {instance.numero_ticket} vous a été assigné: {instance.titre}"
            )