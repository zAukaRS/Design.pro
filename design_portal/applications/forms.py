from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.transaction import commit

from .models import Application, CustomUser, Category


class UserRegistrationForm(UserCreationForm):
    nickname = forms.CharField(
        max_length=30,
        required=False,
        label="Никнейм",
        widget=forms.TextInput(attrs={'placeholder': 'Введите ваш никнейм'})
    )
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={'placeholder': 'Введите ваш email'})
    )

    class Meta:
        model = User
        fields = ['nickname', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Этот email уже зарегистрирован.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        user.email = self.cleaned_data.get('email')

        if commit:
            user.save()
        return user



class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError("Неверный email или пароль.")

        if not user.check_password(password):
            raise forms.ValidationError("Неверный email или пароль.")

        self.user = user
        return self.cleaned_data


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['title', 'description', 'category', 'image']
        labels = {
            'title': 'Название заявки',
            'description': 'Описание',
            'category': 'Категория',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        application = super().save(commit=False)
        if not application.status:
            application.status = 'new'
        if commit:
            application.save()
        return application


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        labels = {
            'name': 'Название категории',
            'description': 'Описание',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


