from django.contrib.auth.models import User
from rest_framework import serializers
from .models import CustomUser, Category, Application, ApplicationHistory, Manager


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'is_admin', 'nickname']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']


class ApplicationSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    category = serializers.CharField(required=False)  # Поле теперь необязательное
    assigned_to = CustomUserSerializer(read_only=True)

    class Meta:
        model = Application
        fields = [
            'id',
            'title',
            'description',
            'category',
            'status',
            'comment',
            'created_at',
            'updated_at',
            'user',
            'image',
            'is_priority_assigned',
            'is_priority',
            'assigned_to',
        ]

    def create(self, validated_data):
        category_name = validated_data.pop('category', None)
        if category_name:
            try:
                category = Category.objects.get(name=category_name)
            except Category.DoesNotExist:
                raise serializers.ValidationError(f"Категория с названием '{category_name}' не найдена.")
        else:
            category = None

        application = Application.objects.create(category=category, **validated_data)
        return application

    def update(self, instance, validated_data):
        category_name = validated_data.pop('category', None)
        if category_name:
            try:
                category = Category.objects.get(name=category_name)
                instance.category = category
            except Category.DoesNotExist:
                raise serializers.ValidationError(f"Категория с названием '{category_name}' не найдена.")

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance


class ApplicationHistorySerializer(serializers.ModelSerializer):
    application = serializers.StringRelatedField()
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = ApplicationHistory
        fields = [
            'id',
            'application',
            'user',
            'action',
            'timestamp',
            'updated_at',
            'role_and_nickname',
            'details',
            'status',
            'updated_by',
        ]


class ManagerSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    priority_application = ApplicationSerializer(read_only=True)

    class Meta:
        model = Manager
        fields = ['id', 'user', 'is_priority_assigned', 'priority_application']


class ApplicationUpdateSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(required=False)

    class Meta:
        model = Application
        fields = ['status', 'comment']

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        comment = validated_data.get('comment', None)
        if comment:
            print(f"Добавлен комментарий: {comment}")
            instance.description += f"\nКомментарий: {comment}"
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
