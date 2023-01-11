from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, RecipeTag, ShoplistRecipe, Tag)
from users.models import Follow

from .fields import Base64ImageField

User = get_user_model()


class GetFoodgramUserSerializer(UserSerializer):

    is_subscribed = serializers.BooleanField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed',
        )


class PostFoodgramUserSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(GetFoodgramUserSerializer):

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField()

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit', 3
        )
        recipes_to_show = obj.recipes.all()[:int(recipes_limit)]
        serializer = ShortRecipeSerializer(recipes_to_show, many=True)
        return serializer.data

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed',
            'recipes', 'recipes_count'
        )

    def subscribe(self, *args, **kwargs):
        current_user = self.context['request'].user
        followed_user = get_object_or_404(
            User, pk=self.context['view'].kwargs.get('id')
        )
        if current_user == followed_user:
            raise serializers.ValidationError(
                {'detail': 'Вы не можете подписаться сами на себя.'}
            )
        elif Follow.objects.filter(
            follower=current_user, author=followed_user
        ).exists():
            raise serializers.ValidationError(
                {'detail': 'Вы уже подписаны на данного автора.'}
            )
        Follow.objects.create(
            follower=current_user, author=followed_user
        )

    def unsubscribe(self, *args, **kwargs):
        current_user = self.context['request'].user
        unfollowed_user = get_object_or_404(
            User, pk=self.context['view'].kwargs.get('id')
        )
        try:
            follow_object = Follow.objects.get(
                follower=current_user, author=unfollowed_user
            )
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                {'detail': 'Вы не подписаны на данного автора.'}
            )
        else:
            follow_object.delete()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class GetRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.pk')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class GetRecipeSerializer(serializers.ModelSerializer):

    tags = TagSerializer(many=True)
    author = GetFoodgramUserSerializer()
    ingredients = GetRecipeIngredientSerializer(
        source='ingredient_list', many=True
    )
    is_favorited = serializers.BooleanField()
    is_in_shopping_cart = serializers.BooleanField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )


class PostRecipeIngredientSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)


class PostRecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.ListField(
        child=PostRecipeIngredientSerializer(),
        allow_empty=False
    )
    tags = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all()),
        allow_empty=False
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
        )

    def validate_name(self, data):
        if (self.context['request'].method == 'PATCH' and
                self.instance.name == data):
            return data
        user = self.context['request'].user
        check_recipe_name = \
            Recipe.objects.filter(name=data, author=user).exists()
        if check_recipe_name:
            raise serializers.ValidationError(
                f'У вас уже есть рецепт с названием {data}.'
            )
        return data

    def validate_ingredients(self, data):
        unique_ingredients = set()
        duplication_errors = set()
        for item in data:
            if item['id'] in unique_ingredients:
                duplication_errors.add(
                    f'В рецепте повторяется ингредиент c номером '
                    f'{item["id"]}.'
                )
            unique_ingredients.add(item['id'])
        if len(duplication_errors) > 0:
            raise serializers.ValidationError(list(duplication_errors))
        return data

    def validate_tags(self, data):
        unique_tags = set()
        duplication_errors = set()
        for item in data:
            if item in unique_tags:
                duplication_errors.add(
                    f'В рецепте повторяется тэг c номером '
                    f'{item}.'
                )
            unique_tags.add(item)
        if len(duplication_errors) > 0:
            raise serializers.ValidationError(list(duplication_errors))
        return data

    def to_representation(self, recipe_obj):
        serializer = GetRecipeSerializer(recipe_obj)
        return serializer.data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context['request'].user
        )
        for ingredient in ingredients:
            ingredient_data = dict(ingredient)
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient_data['amount']
            )

        for tag in tags:
            RecipeTag.objects.create(
                recipe=recipe, tag=tag
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        super().update(instance, validated_data)

        instance.ingredients.clear()
        for ingredient in ingredients_data:
            ingredient_data = dict(ingredient)
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount']
            )

        tag_list = []
        for tag in tags_data:
            current_tag = get_object_or_404(Tag, pk=tag.pk)
            tag_list.append(current_tag)
        instance.tags.set(tag_list)

        instance.save()
        return instance


class FavoriteRecipeSerializer(ShortRecipeSerializer):

    def validate(self):
        user = self.context['request'].user
        recipe = self.context['view'].kwargs.get('pk')
        check_object = FavoriteRecipe.objects.filter(
            user=user, recipe=recipe
        ).exists()
        if self.context['request'].method == 'POST' and check_object:
            raise serializers.ValidationError(
                {'detail':
                    'Данный рецепт уже добавлен в раздел любимых рецептов.'}
            )
        elif self.context['request'].method == 'DELETE' and not check_object:
            raise serializers.ValidationError(
                {'detail':
                    'Данного рецепта нет в разделе любимых рецептов.'}
            )

    def add_to_favorites(self, *args, **kwargs):
        user = self.context['request'].user
        recipe = get_object_or_404(
            Recipe, pk=self.context['view'].kwargs.get('pk')
        )
        FavoriteRecipe.objects.create(
            user=user, recipe=recipe
        )

    def remove_from_favorites(self):
        user = self.context.get('request').user
        recipe = get_object_or_404(
            Recipe, pk=self.context['view'].kwargs.get('pk')
        )
        get_object_or_404(
            FavoriteRecipe, user=user, recipe=recipe
        ).delete()


class ShoplistRecipeSerializer(ShortRecipeSerializer):

    def validate(self):
        user = self.context['request'].user
        recipe = self.context['view'].kwargs.get('pk')
        check_object = ShoplistRecipe.objects.filter(
            user=user, recipe=recipe
        ).exists()
        if self.context['request'].method == 'POST' and check_object:
            raise serializers.ValidationError(
                {'detail': 'Вы уже добавляли данный рецепт в список покупок.'}
            )
        elif self.context['request'].method == 'DELETE' and not check_object:
            raise serializers.ValidationError(
                {'detail': 'Данного рецепта нет в списке покупок.'}
            )

    def add_to_shoplist(self, *args, **kwargs):
        user = self.context['request'].user
        recipe = get_object_or_404(
            Recipe, pk=self.context['view'].kwargs.get('pk')
        )
        ShoplistRecipe.objects.create(
            user=user, recipe=recipe
        )

    def remove_from_shoplist(self, *args, **kwargs):
        user = self.context['request'].user
        recipe = get_object_or_404(
            Recipe, pk=self.context['view'].kwargs.get('pk')
        )
        get_object_or_404(
            ShoplistRecipe, user=user, recipe=recipe
        ).delete()
