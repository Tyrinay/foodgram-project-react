from django.db import transaction
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag,
)
from users.models import User

from .utils import create_ingredients


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', )


# Serializer for adding ingredients
class IngredientPostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


# Serializer for recipe ingredients
class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


# Custom serializer for user model
class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        abstract = True
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if self.context.get('request').user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()


# Serializer for recipe read
class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagsSerializer(read_only=False, many=True)
    author = CustomUserSerializer(read_only=True, many=False)
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='recipeingredients')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_recipe(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_user_data(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return {'is_favorited': False, 'is_in_shopping_cart': False}
        is_favorited = obj.favorites.filter(user=request.user).exists()
        is_in_shopping_cart = (
            obj.shopping_cart.filter(user=request.user).exists()
        )
        return {'is_favorited': is_favorited,
                'is_in_shopping_cart': is_in_shopping_cart}

    def get_is_favorited(self, obj):
        user_data = self.get_user_data(obj)
        return user_data['is_favorited']

    def get_is_in_shopping_cart(self, obj):
        user_data = self.get_user_data(obj)
        return user_data['is_in_shopping_cart']


# Serializer for creating a recipe
class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientPostSerializer(many=True,
                                           source='recipeingredients')
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(),
        error_messages={'does_not_exist': 'Указанного тега не существует'})
    image = Base64ImageField(max_length=None)
    author = CustomUserSerializer(read_only=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'ingredients', 'name',
                  'image', 'text', 'cooking_time',)

    def validate_tags(self, tags):
        for tag in tags:
            if not Tag.objects.filter(id=tag.id).exists():
                raise serializers.ValidationError(
                    'Указанного тега не существует')
        return tags

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Время готовки должно быть не меньше одной минуты')
        return cooking_time

    def validate(self, data):
        ingredients_list = []
        for ingredient in data.get('recipeingredients'):
            if ingredient.get('amount') <= 0:
                raise serializers.ValidationError(
                    'Количество не может быть меньше 1')
            ingredients_list.append(ingredient.get('id'))
        if len(set(ingredients_list)) != len(ingredients_list):
            raise serializers.ValidationError(
                'Вы пытаетесь добавить в рецепт два одинаковых ингредиента')
        return data

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('recipeingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        create_ingredients(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipeingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        create_ingredients(ingredients, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeReadSerializer(
            instance, context={'request': request}).data


# Serializer for short recipe
class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class BaseRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError('Рецепт уже добавлен.')
        return data

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe, context={'request': self.context.get('request')}
        ).data


class FavoriteSerializer(BaseRecipeSerializer):
    class Meta(BaseRecipeSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(BaseRecipeSerializer):
    class Meta(BaseRecipeSerializer.Meta):
        model = ShoppingCart
