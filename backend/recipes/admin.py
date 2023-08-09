from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.forms import BaseInlineFormSet

from .models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag,
)


class IngredientRecipeForm(BaseInlineFormSet):

    def clean(self):
        super(IngredientRecipeForm, self).clean()

        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue
            data = form.cleaned_data
            if (data.get('DELETE')):
                raise ValidationError('Нельзя удалять все ингредиенты')


class IngredientRecipeInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1
    formset = IngredientRecipeForm


class TagInline(admin.TabularInline):
    model = Recipe.tags.through
    extra = 3
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author', 'name', 'cooking_time', 'get_favorites', 'get_ingredients',
        'get_tags',
    )
    search_fields = ('name', 'author__username', 'tags__name')
    list_filter = ('author__username', 'tags__name')
    inlines = (IngredientRecipeInline, TagInline)
    empty_value_display = '-пусто-'

    def get_queryset(self, request):
        queryset = (
            super().get_queryset(request)
            .select_related('author')
            .prefetch_related('ingredients', 'tags')
            .annotate(favorites_count=Count('favorites'))
        )
        return queryset

    def get_favorites(self, obj):
        return obj.favorites_count
    get_favorites.short_description = 'Избранное'

    def get_ingredients(self, obj):
        return ', '.join(
            [ingredient.name for ingredient in obj.ingredients.all()]
        )
    get_ingredients.short_description = 'Ингредиенты'

    def get_tags(self, obj):
        return ', '.join(
            [tag.name for tag in obj.tags.all()]
        )
    get_tags.short_description = 'Теги'


@admin.register(Recipe)
class RecipeAdmin(RecipeAdmin):
    pass


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """ Админ панель управление ингридиентами. """

    list_display = ('name', 'measurement_unit')
    search_fields = ('name', )
    empty_value_display = '-пусто-'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """ Админ панель управление рецепты и инредиенты. """

    list_display = ('recipe', 'ingredient', 'amount',)
    search_fields = ('recipe', )
    empty_value_display = '-пусто-'

    def get_queryset(self, request):
        queryset = (
            super().get_queryset(request)
            .select_related('recipe')
            .prefetch_related('ingredient')
        )
        return queryset


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """ Админ панель управление тегами. """

    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """ Админ панель управление подписками. """

    list_display = ('user', 'recipe')
    list_filter = ('user',)
    search_fields = ('user', 'recipe')
    empty_value_display = '-пусто-'

    def get_queryset(self, request):
        queryset = (
            super().get_queryset(request)
            .select_related('user', 'recipe')
        )
        return queryset


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """ Админ панель списка покупок. """

    list_display = ('recipe', 'user')
    search_fields = ('user', )
    empty_value_display = '-пусто-'

    def get_queryset(self, request):
        queryset = (
            super().get_queryset(request)
            .select_related('user', 'recipe')
        )
        return queryset
