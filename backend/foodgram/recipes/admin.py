from django.contrib import admin
from django.template.defaultfilters import truncatechars

from .models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag


class AdminTag(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')


class AdminIngredient(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient


class AdminRecipe(admin.ModelAdmin):
    list_display = (
        'pk', 'name', 'get_author_username',
        'get_short_text', 'cooking_time', 'get_number_of_fans'
    )
    readonly_fields = ('pub_date', 'get_number_of_fans',)
    inlines = [
        RecipeIngredientInline,
        RecipeTagInline
    ]
    search_fields = (
        'author__username', 'ingredients__name',
        'tags__name', 'tags__slug'
    )

    def get_author_username(self, obj):
        return obj.author.username
    get_author_username.short_description = "Автор"

    def get_short_text(self, obj):
        return truncatechars(obj.text, 100)
    get_short_text.short_description = "Описание рецепта"

    def get_number_of_fans(self, obj):
        return obj.fans.count()
    get_number_of_fans.short_description = "Число добавлений в Избранное"


admin.site.register(Tag, AdminTag)
admin.site.register(Ingredient, AdminIngredient)
admin.site.register(Recipe, AdminRecipe)
