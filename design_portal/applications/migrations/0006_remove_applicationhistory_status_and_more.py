# Generated by Django 5.1.1 on 2024-11-22 02:40

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0005_applicationhistory'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='applicationhistory',
            name='status',
        ),
        migrations.RemoveField(
            model_name='applicationhistory',
            name='updated_by',
        ),
        migrations.AddField(
            model_name='applicationhistory',
            name='action',
            field=models.CharField(default='Изменение', max_length=255),
        ),
        migrations.AddField(
            model_name='applicationhistory',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='applicationhistory',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='applicationhistory',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
