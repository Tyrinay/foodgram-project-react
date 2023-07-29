from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField

from django.shortcuts import get_object_or_404

from users.models import User

from ..serializers import RecipeShortSerializer
from .validators import validate_username_me


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя."""

    username = serializers.RegexField(
        max_length=150,
        required=True,
        regex=r'^[\w.@+-]'
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password'
        )

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'Пользователь с таким USERNAME уже существует'
            )
        return validate_username_me(value)


class CustomUserSerializer(UserSerializer):
    """Сериализатор кастомной модели пользователя."""

    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        abstract = True
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context['request']
        return not request.user.is_authenticated or obj.following.filter(
            user=request.user).exists()


class SubscribeListSerializer(CustomUserSerializer):
    """Сериализатор подписок."""

    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )
        read_only_fields = (
            'email', 'username', 'first_name', 'last_name'
        )

    def validate(self, data):
        author_id = self.context['request'].parser_context['kwargs']['id']
        author = get_object_or_404(User, id=author_id)
        user = self.context['request'].user
        if user.follower.filter(author=author_id).exists():
            raise ValidationError(
                detail='Подписка уже существует',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise ValidationError(
                detail='Нельзя подписаться на самого себя',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context['request']
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeShortSerializer(recipes, many=True, read_only=True)
        return serializer.data
