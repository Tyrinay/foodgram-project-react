from django.db.models import Sum
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly,
)

from api.v1.utils import (
    create_model_instance, create_shopping_cart, delete_model_instance,
)
from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag,
)

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import AuthorPermission
from .serializers import (
    CreateRecipeSerializer, FavoriteSerializer, IngredientsSerializer,
    RecipeReadSerializer, ShoppingCartSerializer, TagsSerializer,
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вывод ингредиентов."""

    serializer_class = IngredientsSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny, )
    filter_backends = (IngredientFilter, )
    search_fields = ('^name', )
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    """Вывод тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Работа с рецептами."""

    queryset = Recipe.objects.select_related(
        'author').prefetch_related('tags', 'ingredients')
    serializer_class = CreateRecipeSerializer
    permission_classes = (AuthorPermission, )
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return CreateRecipeSerializer

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        return create_shopping_cart(ingredients)

    @action(
        detail=True,
        methods=('POST',),
        permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return create_model_instance(request, recipe,
                                         ShoppingCartSerializer)

    @shopping_cart.mapping.delete
    def destroy_shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        error_message = 'У вас нет этого рецепта в списке покупок'
        return delete_model_instance(request, ShoppingCart,
                                     recipe, error_message)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def favorite(self, request, pk):
        """Работа с избранными рецептами.
        Удаление/добавление в избранное.
        """
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return create_model_instance(request, recipe, FavoriteSerializer)

        error_message = 'У вас нет этого рецепта в избранном'
        return delete_model_instance(request, Favorite,
                                     recipe, error_message)
