from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import UniqueConstraint

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name="название ингредиента",
        max_length=100,
    )
    measurement_unit = models.CharField(
        verbose_name='единица измерения',
        max_length=20
    )

    class Meta:
        ordering = ['name']
        verbose_name = "ингредиент"
        verbose_name_plural = "ингредиенты"

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="автор"
    )
    name = models.CharField(
        verbose_name="название рецепта",
        max_length=200,
    )
    image = models.ImageField(
        verbose_name="картинка",
        upload_to='recipes/images/',
        null=True,
        default=None
    )
    text = models.TextField(
        verbose_name="описание"
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name="ингредиенты"
    )
    tags = models.ManyToManyField(
        "Tag",
        related_name="recipes",
        verbose_name="теги"
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='время приготовления',
        validators=[
            MinValueValidator(1, message="Минимальное значение 1")
        ]
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipeingredients',
        verbose_name='рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipeingredients',
        verbose_name='ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='количество',
        validators=[
            MinValueValidator(1, message='Минимальное количество 1')
        ]
    )

    class Meta:
        verbose_name = "ингредиент в рецепте"
        verbose_name_plural = "ингредиенты в рецептах"
        unique_together = ('recipe', 'ingredient')

    def str(self):
        return (
            f'{self.ingredient.name} :: {self.ingredient.measurement_unit}'
            f' - {self.amount} '
        )


class Tag(models.Model):
    name = models.CharField(
        verbose_name="название тега",
        max_length=100,
        unique=True,
    )
    color = models.CharField(
        verbose_name='цветовой HEX-код',
        unique=True,
        max_length=7,
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Введенное значение не является цветом в формате HEX!'
            )
        ]
    )
    slug = models.SlugField(
        verbose_name="уникальный слаг",
        unique=True,
        max_length=200
    )

    class Meta:
        verbose_name = "тег"
        verbose_name_plural = "теги"

    def __str__(self):
        return self.name


class FavoriteShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s_unique'
            )
        ]

    def __str__(self):
        return f'{self.user} :: {self.recipe}'


class Favorite(FavoriteShoppingCart):
    class Meta(FavoriteShoppingCart.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(FavoriteShoppingCart):
    class Meta(FavoriteShoppingCart.Meta):
        default_related_name = 'shopping_cart'
        verbose_name = 'cписок покупок'
        verbose_name_plural = 'cписки покупок'
