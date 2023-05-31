from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Название тега"
    )
    color = models.CharField(
        max_length=7,
        unique=True, blank=True,
        validators=[
            RegexValidator(
                regex=r"^#(?:[0-9a-fA-F]{3}){1,2}$",
                message='Color must be in HEX format starting with "#"',
                code="Color format is invalid"
            )
        ],
        verbose_name="Цветовой HEX-код"
    )
    slug = models.SlugField(
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[-a-zA-Z0-9_]+$",
                message=(
                    "Only latin letters, digits and underscores are allowed."
                ),
                code="invalid slug name"
            )
        ],
        verbose_name="Слаг тега"
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название ингредиента"
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name="Единица измерения"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='name - measurement unit unique constraint'
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название рецепта"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта"
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации"
    )
    text = models.TextField(verbose_name="Описание рецепта")
    image = models.ImageField(
        upload_to="recipes/images/",
        verbose_name="Изображение блюда"
    )
    tags = models.ManyToManyField(
        Tag, through="RecipeTag",
        verbose_name="Теги"
    )
    ingredients = models.ManyToManyField(
        Ingredient, through="RecipeIngredient",
        verbose_name="Ингредиенты"
    )
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Время приготовления (в минутах)"
    )

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name="tag_list",
        verbose_name="Рецепты"
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE,
        related_name="attached_to",
        verbose_name="Теги"
    )

    class Meta:
        verbose_name_plural = "Recipe tags"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "tag"],
                name="recipe - tag unique constraint"
            )
        ]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name="ingredient_list",
        verbose_name="Рецепты"
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Ингредиенты"
    )
    amount = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Число единиц"
    )

    class Meta:
        verbose_name_plural = "Recipe ingredients"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="recipe - ingredient unique constraint"
            )
        ]


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name="fans",
        verbose_name="Любимый рецепт"
    )

    class Meta:
        verbose_name = "Favorite recipes"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="favorite recipe unique constraint"
            )
        ]


class ShoplistRecipe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="shoplist_recipes",
        verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name="shoplist_users",
        verbose_name="Рецепт в списке покупок"
    )

    class Meta:
        verbose_name = "Shoplist recipes"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="shoplist - recipe unique constraint"
            )
        ]
