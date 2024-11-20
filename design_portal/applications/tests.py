from django.test import TestCase
from django.urls import reverse
from .models import Application, Category
from django.contrib.auth.models import User


class ApplicationModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Категория 1', description='Описание категории')
        self.application = Application.objects.create(
            title='Тестовая заявка',
            description='Описание заявки',
            category=self.category,
            status='new'
        )

    def test_application_creation(self):
        self.assertEqual(self.application.title, 'Тестовая заявка')
        self.assertEqual(self.application.category.name, 'Категория 1')


class ApplicationListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/applications/')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('application-list'))
        self.assertTemplateUsed(response, 'application_list.html')
