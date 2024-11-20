from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Application, Category
from .forms import ApplicationForm, CategoryForm


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


class ApplicationUpdateView(LoginRequiredMixin, UpdateView):
    model = Application
    form_class = ApplicationForm
    template_name = 'application_form.html'


class ApplicationDeleteView(LoginRequiredMixin, DeleteView):
    model = Application
    template_name = 'application_confirm_delete.html'
    success_url = reverse_lazy('application-list')


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
    permission_required = 'catalog.add_category'


class CategoryUpdateView(PermissionRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category_form.html'
    permission_required = 'catalog.change_category'


class CategoryDeleteView(PermissionRequiredMixin, DeleteView):
    model = Category
    template_name = 'category_confirm_delete.html'
    success_url = reverse_lazy('category-list')
    permission_required = 'catalog.delete_category'


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('login'))
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def user_dashboard(request):
    return render(request, 'dashboard.html', {'user': request.user})
