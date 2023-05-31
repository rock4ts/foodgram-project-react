from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Follow
from .filters import IngredientFilter, RecipeFilter
from .mixins import IsAdminOrOwnerMixin
from .serializers import (FavoriteRecipeSerializer, GetFoodgramUserSerializer,
                          GetRecipeSerializer, IngredientSerializer,
                          PostFoodgramUserSerializer, PostRecipeSerializer,
                          ShoplistRecipeSerializer, SubscribeSerializer,
                          TagSerializer)
from .utils import (annotate_subscribe_status, annotated_recipes,
                    shoplist_to_pdf)

User = get_user_model()


class FoodgramUserViewSet(UserViewSet):
    serializer_class = GetFoodgramUserSerializer
    queryset = User.objects.all().prefetch_related('recipes')

    def get_serializer_class(self):
        if self.action == 'create':
            return PostFoodgramUserSerializer
        if self.action == 'me':
            return GetFoodgramUserSerializer
        if self.action in ("subscriptions", "subscribe", "unsubscribe"):
            return SubscribeSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in (
            'me', 'retrieve', 'subscribe', 'unsubscribe', 'subscriptions'
        ):
            return [IsAuthenticated(), ]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if self.action == "subscriptions":
            subscriptions = Follow.objects.filter(follower=user.pk)
            queryset = queryset.filter(
                pk__in=subscriptions.values_list('author')
            ).annotate(recipes_count=Count('recipes'))
        elif self.action in ("subscribe", "unsubscribe"):
            queryset = queryset.filter(
                pk=self.kwargs["id"]
            ).annotate(recipes_count=Count('recipes'))
        return annotate_subscribe_status(queryset, user)

    @action(['GET'], detail=False)
    def me(self, request):
        user = request.user
        profile_obj = get_object_or_404(self.get_queryset(), pk=user.pk)
        serializer = self.get_serializer(instance=profile_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(['GET'], detail=False)
    def subscriptions(self, *args, **kwargs):
        subscriptions = self.get_queryset()
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(subscriptions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(['POST'], detail=True)
    def subscribe(self, *args, **kwargs):
        followed_user = self.get_object()
        serializer = self.get_serializer(instance=followed_user)
        serializer.subscribe()
        updated_data = serializer.data
        updated_data['is_subscribed'] = True
        return Response(updated_data, status=status.HTTP_200_OK)

    @subscribe.mapping.delete
    def unsubscribe(self, *args, **kwargs):
        unfollowed_user = self.get_object()
        serializer = self.get_serializer(instance=unfollowed_user)
        serializer.unsubscribe()
        return Response(serializer.data, status.HTTP_204_NO_CONTENT)


class TagViewSet(IsAdminOrOwnerMixin, viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(TagViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(IsAdminOrOwnerMixin, viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = PostRecipeSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = RecipeFilter
    ordering = ('-pub_date',)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return GetRecipeSerializer
        if self.action in ('favorite', 'remove_favorite'):
            return FavoriteRecipeSerializer
        if self.action in ('shopping_cart', 'remove_from_shopping_cart'):
            return ShoplistRecipeSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = super().get_queryset()
        current_user = self.request.user
        return annotated_recipes(queryset, current_user)

    @action(['POST'], detail=True)
    def favorite(self, *args, **kwargs):
        favorite_recipe = self.get_object()
        serializer = self.get_serializer(
            instance=favorite_recipe,
            data=self.request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.add_to_favorites()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @favorite.mapping.delete
    def remove_favorite(self, *args, **kwargs):
        unfavorite_recipe = self.get_object()
        serializer = self.get_serializer(
            instance=unfavorite_recipe,
            data=self.request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.remove_from_favorites()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

    @action(['POST'], detail=True)
    def shopping_cart(self, *args, **kwargs):
        shoplist_recipe = self.get_object()
        serializer = self.get_serializer(
            instance=shoplist_recipe,
            data=self.request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.add_to_shoplist()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, *args, **kwargs):
        removed_recipe = self.get_object()
        serializer = self.get_serializer(
            instance=removed_recipe,
            data=self.request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.remove_from_shoplist()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

    @action(['GET'], detail=False)
    def download_shopping_cart(self, request):
        '''
        Builds recipe shoplist ingredients dictionary
        with accumulated measurement unit values and calls
        pdf file renderer which return a human-friendly representation
        of shoplist ingredients.
        '''
        user = request.user
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoplist_users__user=user.pk
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(ingredient_total=Sum('amount'))
        return shoplist_to_pdf(ingredients)
