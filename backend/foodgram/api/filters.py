from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe
from users.models import User


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):

    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='get_is_in_shoplist')

    def get_is_favorited(self, queryset, name, value):
        current_user = self.request.user
        if current_user.is_authenticated and value:
            return queryset.filter(fans__user=current_user)
        return queryset

    def get_is_in_shoplist(self, queryset, name, value):
        current_user = self.request.user
        if current_user.is_authenticated and value:
            return queryset.filter(shoplist_users__user=current_user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags')
