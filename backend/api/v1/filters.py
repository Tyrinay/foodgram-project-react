from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(SearchFilter):
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart',)

    def filter_favorites_and_shopping_cart(self, queryset, name, value,
                                           related_field):
        if value and self.request.user.is_authenticated:
            filter_parameters = {f"{related_field}__user": self.request.user}
            return queryset.filter(**filter_parameters)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        return self.filter_favorites_and_shopping_cart(queryset, name, value,
                                                       "favorites")

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return self.filter_favorites_and_shopping_cart(queryset, name, value,
                                                       "shopping_cart")
