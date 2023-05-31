from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe, Tag
from users.models import User


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):

    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tag_list__tag__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        field_name='fans__user',
        method='filter_by_favorites'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='shoplist_users__user',
        method='filter_by_shoplist'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def filter_by_favorites(self, queryset, field_name, value):
        current_user = self.request.user
        if current_user.is_authenticated and value:
            lookup = field_name
            return queryset.filter(**{lookup: current_user})
        return queryset

    def filter_by_shoplist(self, queryset, field_name, value):
        current_user = self.request.user
        if current_user.is_authenticated and value:
            lookup = field_name
            return queryset.filter(**{lookup: current_user})
        return queryset
