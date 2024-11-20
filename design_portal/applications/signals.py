from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Application


@receiver(pre_save, sender=Application)
def set_default_status(sender, instance, **kwargs):
    if not instance.status:
        instance.status = 'new'
