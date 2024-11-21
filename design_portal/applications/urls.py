from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/',  views.custom_login, name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('dashboard/', views.user_dashboard, name='dashboard'),

    path('applications/', views.ApplicationListView.as_view(), name='application-list'),
    path('applications/new/', views.ApplicationCreateView.as_view(), name='application-create'),
    path('applications/<int:pk>/update/', views.ApplicationUpdateView.as_view(), name='application-update'),
    path('applications/<int:pk>/delete/', views.ApplicationDeleteView.as_view(), name='application-delete'),
    path('application/<int:application_id>/status/<str:new_status>/', views.update_status, name='update-status'),

    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/new/', views.CategoryCreateView.as_view(), name='category-create'),
    path('categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category-update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category-delete'),

    path('check-email/', views.check_email, name='check_email'),
]
