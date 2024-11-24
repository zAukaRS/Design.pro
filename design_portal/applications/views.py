from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test

from .decorators import manager_required
from .models import Application, Category, ApplicationHistory, Manager
from .forms import ApplicationForm, CategoryForm, EmailAuthenticationForm, UserRegistrationForm
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.models import User

LAST_SEEN_LAST_ADDED = None
LAST_SEEN_LAST_COMPLETED = None


def is_moderator(user):
    return user.is_staff and not user.is_superuser


def index(request):
    global LAST_SEEN_LAST_ADDED, LAST_SEEN_LAST_COMPLETED
    context = {
        'is_authenticated': request.user.is_authenticated,
        'is_moderator': is_moderator(request.user),
    }
    if request.user.is_authenticated:
        num_applications = Application.objects.count()
        num_categories = Category.objects.count()
        user_applications = Application.objects.filter(user=request.user)
        last_added_application = Application.objects.order_by('-created_at').first()
        last_completed_application = Application.objects.filter(status='completed').order_by('-updated_at').first()

        should_notify = (
                request.user.is_staff and (
                last_added_application != LAST_SEEN_LAST_ADDED or
                last_completed_application != LAST_SEEN_LAST_COMPLETED
        )
        )
        if request.method == "POST" and "clear_notification" in request.POST:
            LAST_SEEN_LAST_ADDED = last_added_application
            LAST_SEEN_LAST_COMPLETED = last_completed_application
            should_notify = False

        context.update({
            'num_applications': num_applications,
            'num_categories': num_categories,
            'user_applications': user_applications,
            'last_added_application': last_added_application,
            'last_completed_application': last_completed_application,
            'should_notify': should_notify,
        })

    return render(request, 'index.html', context)


class ApplicationListView(LoginRequiredMixin, ListView):
    model = Application
    template_name = 'applications/application_list.html'
    context_object_name = 'applications'
    paginate_by = 4

    def get_queryset(self):
        queryset = Application.objects.all() if self.request.user.is_staff else Application.objects.filter(
            user=self.request.user)
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')

        return context


class ApplicationDetailView(LoginRequiredMixin, DetailView):
    model = Application
    template_name = 'applications/application_detail.html'
    context_object_name = 'application'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['history'] = ApplicationHistory.objects.filter(application=self.object).order_by('-timestamp')
        return context


class ApplicationCreateView(LoginRequiredMixin, CreateView):
    model = Application
    form_class = ApplicationForm
    template_name = 'application_form.html'

    def form_valid(self, form):
        form.instance.status = 'new'
        form.instance.user = self.request.user
        response = super().form_valid(form)
        ApplicationHistory.objects.create(
            application=self.object,
        )
        return response

    def get_success_url(self):
        return reverse('application-list')


class ApplicationUpdateView(LoginRequiredMixin, UpdateView):
    model = Application
    form_class = ApplicationForm
    template_name = 'application_form.html'

    def form_valid(self, form):
        application = form.instance
        previous_data = Application.objects.get(id=application.id)
        details = []
        user = self.request.user
        if application.title != previous_data.title:
            details.append(f"Название заявки изменено с '{previous_data.title}' на '{application.title}'")
        if application.description != previous_data.description:
            details.append(f"Описание изменено с '{previous_data.description}' на '{application.description}'")
        if application.category != previous_data.category:
            details.append(f"Категория изменена с '{previous_data.category}' на '{application.category}'")
        if application.image != previous_data.image:
            details.append(f"Изображение изменено")
        if application.status != previous_data.status:
            details.append(f"Статус изменен с '{previous_data.status}' на '{application.status}'")
        if not details:
            details.append("Нет изменений")
        details_str = "\n".join(details)
        if details_str != "Нет изменений":
            ApplicationHistory.objects.create(
                application=application,
                action="Изменение заявки",
                user=user,
                details=details_str,
                timestamp=now(),
            )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('application-list')


class ApplicationHistoryDetailView(DetailView):
    model = ApplicationHistory
    template_name = 'applications/application_history_detail.html'
    context_object_name = 'history_item'


class ApplicationDeleteView(LoginRequiredMixin, DeleteView):
    model = Application
    template_name = 'applications/application_confirm_delete.html'
    success_url = reverse_lazy('application-list')

    def get_queryset(self):
        if self.request.user.is_staff:
            return Application.objects.all()
        else:
            return Application.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('application-list')


class UserApplicationListView(LoginRequiredMixin, ListView):
    model = Application
    template_name = 'applications/user_application_list.html'
    context_object_name = 'applications'
    paginate_by = 10

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)


class UserApplicationDeleteView(LoginRequiredMixin, DeleteView):
    model = Application
    template_name = 'applications/application_confirm_delete.html'

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('user-application-list')


@staff_member_required
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category-list')
    else:
        form = CategoryForm()
    return render(request, 'category_form.html', {'form': form})


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'
    paginate_by = 10


class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = 'category_detail.html'
    context_object_name = 'category'


class CategoryCreateView(PermissionRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category_form.html'
    permission_required = 'applications.add_category'


class CategoryUpdateView(PermissionRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category_form.html'
    permission_required = 'applications.change_category'


class CategoryDeleteView(PermissionRequiredMixin, DeleteView):
    model = Category
    template_name = 'category_confirm_delete.html'
    success_url = reverse_lazy('category-list')
    permission_required = 'applications.delete_category'


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            nickname = form.cleaned_data.get('nickname')
            if nickname:
                user.nickname = nickname
            user.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


def custom_login(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                form.add_error(None, "Неверный email или пароль.")
        else:
            form.add_error(None, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = EmailAuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


def check_email(request):
    email = request.GET.get('email', '')
    exists = User.objects.filter(email=email).exists()
    return JsonResponse({'exists': exists})


def application_list(request):
    applications = Application.objects.all()
    for app in applications:
        app.is_priority = app.assigned_admin == request.user and app.priority == True
    context = {
        'applications': applications,
    }
    return render(request, 'applications/application_list.html', context)


@login_required
def user_dashboard(request):
    return render(request, 'dashboard.html', {'user': request.user})


@login_required
def update_status(request, application_id, new_status):
    application = get_object_or_404(Application, id=application_id)
    if not request.user.is_staff and application.user != request.user:
        return HttpResponseForbidden("Вы не можете изменять статус этой заявки.")
    if new_status in dict(Application.STATUS_CHOICES):
        application.status = new_status
        application.save()
        ApplicationHistory.objects.create(
            application=application,
            action="Изменение статуса",
            user=request.user,
            details=f"Статус изменен на {new_status}",
            timestamp=now(),
        )
        next_url = request.POST.get('next','application-list')
        return redirect(next_url)
    return redirect('user-application-list')


@login_required
def delete_user_application(request, pk):
    application = get_object_or_404(Application, pk=pk, user=request.user)
    if application.status in ['in_progress', 'completed']:
        return HttpResponseForbidden("Вы не можете удалить заявку со статусом 'Принято в работу' или 'Завершена'.")
    if request.method == 'POST':
        application.delete()
        return redirect('user-application-list')
    return render(request, 'applications/application_confirm_delete.html', {'application': application})


@login_required
def application_list(request):
    status_filter = request.GET.get('status', None)
    applications = Application.objects.filter(user=request.user)

    if status_filter:
        applications = applications.filter(status=status_filter)

    applications = applications.order_by('-created_at')

    context = {
        'applications': applications,
        'status_filter': status_filter
    }

    return render(request, 'applications/application_list.html', context)


@login_required
@user_passes_test(is_moderator)
def assign_priority_application(request, application_id):
    application = get_object_or_404(Application, id=application_id, is_priority=True)
    admins = User.objects.filter(is_superuser=True)
    if request.method == 'POST':
        admin_id = request.POST.get('admin_id')
        selected_admin = get_object_or_404(User, id=admin_id, is_superuser=True)
        application.assigned_to = selected_admin
        application.save()
        manager = request.user.manager_profile
        manager.is_priority_assigned = True
        manager.save()
        return redirect('index')
    return render(request, 'assign_priority.html', {'application': application, 'admins': admins})


@login_required
@user_passes_test(is_moderator)
def create_priority_application(request):
    try:
        manager_profile = request.user.manager_profile
        if manager_profile.priority_application and not manager_profile.is_priority_assigned:
            return redirect('assign_priority', application_id=manager_profile.priority_application.id)
    except Manager.DoesNotExist:
        return redirect('index')

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.is_priority = True
            application.user = request.user
            application.save()
            manager_profile.priority_application = application
            manager_profile.is_priority_assigned = False
            manager_profile.save()
            return redirect('assign_priority', application_id=application.id)
    else:
        form = ApplicationForm()

    return render(request, 'create_priority_application.html', {'form': form})


@login_required
@user_passes_test(is_moderator)
def priority_list(request):
    try:
        manager_profile = request.user.manager_profile
        if manager_profile.priority_application and not manager_profile.is_priority_assigned:
            return render(request, 'priority_not_assigned.html')
    except Manager.DoesNotExist:
        return redirect('index')
    applications = Application.objects.filter(is_priority=True)
    return render(request, 'priority_list.html', {'applications': applications})


@csrf_exempt
def application_list_api(request):
    if request.method == 'GET':
        applications = Application.objects.all()
        applications_data = [{"id": app.id, "title": app.title, "description": app.description, "status": app.status}
                             for app in applications]
        return JsonResponse({"applications": applications_data})


@csrf_exempt
def application_detail_api(request, pk):
    if request.method == 'GET':
        application = Application.objects.get(id=pk)
        application_data = {
            "id": application.id,
            "title": application.title,
            "description": application.description,
            "status": application.status
        }
        return JsonResponse(application_data)


@csrf_exempt
def application_create_api(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save()
            return JsonResponse({"message": "Заявка успешно создана", "application_id": application.id})
        else:
            return JsonResponse({"error": "Ошибка при создании заявки"}, status=400)


@csrf_exempt
def application_update_api(request, pk):
    if request.method == 'PUT':
        application = Application.objects.get(id=pk)
        form = ApplicationForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            return JsonResponse({"message": "Заявка успешно обновлена"})
        else:
            return JsonResponse({"error": "Ошибка при обновлении заявки"}, status=400)


@csrf_exempt
def application_delete_api(request, pk):
    if request.method == 'DELETE':
        application = Application.objects.get(id=pk)
        application.delete()
        return JsonResponse({"message": "Заявка успешно удалена"})


@csrf_exempt
def category_list_api(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        categories_data = [{"id": category.id, "name": category.name} for category in categories]
        return JsonResponse({"categories": categories_data})


@csrf_exempt
def category_create_api(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            return JsonResponse({"message": "Категория успешно создана", "category_id": category.id})
        else:
            return JsonResponse({"error": "Ошибка при создании категории"}, status=400)


@csrf_exempt
def register_api(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return JsonResponse({"message": "Пользователь успешно зарегистрирован"})
        else:
            return JsonResponse({"error": "Ошибка при регистрации"}, status=400)


@csrf_exempt
def login_api(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({"message": "Пользователь успешно авторизован"})
        else:
            return JsonResponse({"error": "Неверный email или пароль"}, status=400)


@csrf_exempt
def check_email_api(request):
    email = request.GET.get('email')
    exists = User.objects.filter(email=email).exists()
    return JsonResponse({'exists': exists})
