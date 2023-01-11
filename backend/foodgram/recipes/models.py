from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=200, verbose_name="Название тега", unique=True
    )
    color = models.CharField(
        max_length=7, verbose_name="Цветовой HEX-код",
        unique=True, blank=True,
        validators=[
            RegexValidator(
                regex=r"^#(?:[0-9a-fA-F]{3}){1,2}$",
                message='Color must be in HEX format starting with "#"',
                code="Color format is invalid"
            )
        ]
    )
    slug = models.SlugField(
        verbose_name="Слаг тега",
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[-a-zA-Z0-9_]+$",
                message=(
                    "Only latin letters, digits and underscores are allowed."
                ),
                code="invalid slug name"
            ),
        ]
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200, verbose_name="Название ингредиента"
    )
    measurement_unit = models.CharField(
        max_length=200, verbose_name="Единица измерения"
    )

    class Meta:
        unique_together = ("name", "measurement_unit")

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=200, verbose_name="Название рецепта"
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
        upload_to="recipes/images/", verbose_name="Изображение блюда"
    )
    tags = models.ManyToManyField(
        Tag, through="RecipeTag", verbose_name="Теги"
    )
    ingredients = models.ManyToManyField(
        Ingredient, through="RecipeIngredient", verbose_name="Ингредиенты"
    )
    cooking_time = models.IntegerField(
        verbose_name="Время приготовления (в минутах)",
        validators=[MinValueValidator(1), ]
    )

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name="tag_list", verbose_name="Рецепты"
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE,
        related_name="attached_to", verbose_name="Теги"
    )

    class Meta:
        verbose_name_plural = "Recipe tags"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "tag"],
                name="recipe_tag_unique_constraint"
            )
        ]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name="ingredient_list", verbose_name="Рецепты"
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name="used_in", verbose_name="Ингредиенты"
    )
    amount = models.IntegerField(
        verbose_name="Число единиц",
        validators=[MinValueValidator(1), ]
    )

    class Meta:
        verbose_name_plural = "Recipe ingredients"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="recipe_ingredient_unique_constraint"
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
        related_name="fans", verbose_name="Любимый рецепт"
    )

    class Meta:
        verbose_name = "Favorite recipes"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="favorite_recipe_unique_constraint"
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
                name="shoplist_recipe_unique_constraint"
            )
        ]
