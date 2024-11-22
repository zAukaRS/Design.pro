from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Application, ApplicationHistory


@receiver(pre_save, sender=Application)
def set_default_status(sender, instance, **kwargs):
    if not instance.status:
        instance.status = 'new'


@receiver(pre_save, sender=Application)
def track_application_changes(sender, instance, **kwargs):
    if instance.pk:
        previous = Application.objects.get(pk=instance.pk)
        if previous.status != instance.status:
            action = f'Статус изменен с {previous.get_status_display()} на {instance.get_status_display()}'
            ApplicationHistory.objects.create(
                application=instance,
                user=instance.user,
                action=action
            )
