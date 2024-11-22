from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now

from .managers import CustomUserManager


class CustomUser(User):
    full_name = models.CharField(max_length=100)
    is_admin = models.BooleanField(default=False)
    nickname = models.CharField(max_length=50, blank=True, null=True)
    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание категории")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('category-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name


class Application(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершена'),
    ]

    title = models.CharField(max_length=200, verbose_name="Название заявки")
    description = models.TextField(verbose_name="Описание заявки")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="applications",
        verbose_name="Категория заявки"
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name="Статус заявки"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="applications",
        verbose_name="Пользователь"
    )
    image = models.ImageField(
        upload_to='applications/images/',
        blank=True,
        null=True,
        verbose_name="Изображение"
    )

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def can_user_delete(self, user):
        if self.user != user:
            return False
        if self.status in ['in_progress', 'completed']:
            return False
        return True

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if not is_new:
            ApplicationHistory.objects.create(
                application=self,
                action="Изменение заявки",
                user=kwargs.get('user'),
                timestamp=now(),
            )


class ApplicationHistory(models.Model):
    application = models.ForeignKey(Application, related_name='history', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    role_and_nickname = models.CharField(max_length=255, blank=True, null=True)
    details = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_by')

    def save(self, *args, **kwargs):
        if self.user:
            self.role_and_nickname = f"{self.user.username} ({'Администратор' if self.user.is_staff else 'Пользователь'})"
        else:
            self.role_and_nickname = "Администратор"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.application.title} - {self.action} ({self.timestamp})"
