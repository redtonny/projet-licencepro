from django.apps import AppConfig
import os
from django.apps import apps
from django.core.checks import Error
from django.conf import settings



class TicketConfig(AppConfig):
    name = 'ticket'
    
    def ready(self):
        import ticket.signals
