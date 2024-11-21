from django.contrib.auth import authenticate, login
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import Application, Category
from .forms import ApplicationForm, CategoryForm, EmailAuthenticationForm, UserRegistrationForm
from django.http import JsonResponse
from django.contrib.auth.models import User


def index(request):
    if request.user.is_authenticated:
        num_applications = Application.objects.count()
        num_categories = Category.objects.count()
        user_applications = Application.objects.filter(user=request.user)

        context = {
            'num_applications': num_applications,
            'num_categories': num_categories,
            'user_applications': user_applications,
        }

        return render(request, 'index.html', context)
    else:
        return render(request, 'index.html', {'is_authenticated': False})


class ApplicationListView(LoginRequiredMixin, ListView):
    model = Application
    template_name = 'applications/application_list.html'
    context_object_name = 'applications'
    paginate_by = 10


class ApplicationDetailView(LoginRequiredMixin, DetailView):
    model = Application
    template_name = 'application_detail.html'
    context_object_name = 'application'


class ApplicationCreateView(LoginRequiredMixin, CreateView):
    model = Application
    form_class = ApplicationForm
    template_name = 'application_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('application-list')


class ApplicationUpdateView(LoginRequiredMixin, UpdateView):
    model = Application
    form_class = ApplicationForm
    template_name = 'application_form.html'


class ApplicationDeleteView(LoginRequiredMixin, DeleteView):
    model = Application
    template_name = 'applications/application_confirm_delete.html'
    success_url = reverse_lazy('application-list')


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


@login_required
def user_dashboard(request):
    return render(request, 'dashboard.html', {'user': request.user})


@login_required
def update_status(request, application_id, new_status):
    if not request.user.is_staff and new_status in ['in_progress', 'completed']:
        return redirect('index')
    application = get_object_or_404(Application, id=application_id)
    if new_status in dict(Application.STATUS_CHOICES):
        application.status = new_status
        application.save()
    return redirect('application-list')
