from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', include('applications.urls')),
    path('admin/', admin.site.urls),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
]
