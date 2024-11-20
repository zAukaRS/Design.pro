from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class CustomUser(User):
    full_name = models.CharField(max_length=100)
    is_admin = models.BooleanField(default=False)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание категории")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

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
