from django.contrib.auth.decorators import login_required
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .decorators import manager_required
from .views import application_list_api, application_detail_api, application_create_api, application_update_api, \
    application_delete_api, category_list_api, category_create_api, register_api, login_api, check_email_api, \
    create_priority_application

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
    path('applications/user/', views.UserApplicationListView.as_view(), name='user-application-list'),
    path('applications/user/<int:pk>/delete/', views.delete_user_application, name='delete-user-application'),
    path('applications/', views.application_list, name='application-list'),
    path('applications/<int:pk>/', views.ApplicationDetailView.as_view(), name='application-detail'),

    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/new/', views.CategoryCreateView.as_view(), name='category-create'),
    path('categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category-update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category-delete'),

    path('check-email/', views.check_email, name='check_email'),
    path('history/<int:pk>/', views.ApplicationHistoryDetailView.as_view(), name='application_history_detail'),

    path('priority/create/', views.create_priority_application, name='create_priority_application'),
    path('priority/<int:application_id>/assign/', views.assign_priority_application, name='assign_priority'),






    path('api/applications/', application_list_api, name='application-list-api'),
    path('api/applications/<int:pk>/', application_detail_api, name='application-detail-api'),
    path('api/applications/create/', application_create_api, name='application-create-api'),
    path('api/applications/<int:pk>/update/', application_update_api, name='application-update-api'),
    path('api/applications/<int:pk>/delete/', application_delete_api, name='application-delete-api'),

    path('api/categories/', category_list_api, name='category-list-api'),
    path('api/categories/create/', category_create_api, name='category-create-api'),

    path('api/register/', register_api, name='register-api'),
    path('api/login/', login_api, name='login-api'),
    path('api/check-email/', check_email_api, name='check-email-api'),
]
