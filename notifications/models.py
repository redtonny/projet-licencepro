from django.db import models
from django.db import models
from django.contrib.auth import get_user_model

Utilisateur = get_user_model()

class Notification(models.Model):
    TYPES = [
        ('ticket', 'Nouveau ticket'),
        ('intervention', 'Intervention'),
        ('equipement', 'Équipement'),
        ('achat', 'Achat'),
    ]

    destinataire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPES, default='ticket')
    lien = models.CharField(max_length=200, blank=True)
    lu = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.destinataire} — {self.message[:50]}"
