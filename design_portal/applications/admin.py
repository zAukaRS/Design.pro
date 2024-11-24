from django.contrib import admin
from .models import Application, Category, Manager


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ('user', 'priority_application')
    search_fields = ('user__username',)