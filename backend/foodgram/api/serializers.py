from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, RecipeTag, ShoplistRecipe, Tag)
from users.models import Follow
from .fields import Base64ImageField
from .utils import add_ingredients_to_recipe, annotated_recipes

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


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class GetRecipeIngredientSerializer(serializers.ModelSerializer):
    '''
    Ingredient serialiser used as a nested field in GetRecipeSerializer.
    Uses RecipeIngredient intermediary model
    to include amount field to representation.
    '''
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
    '''
    Ingredients serializer used as a child
    to validate ingredients data in PostRecipeSerializer.
    '''
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
        '''
        Validates that recipes with identical names can not be created
        by the same user.
        '''
        check_name_not_updated = (
            self.context['request'].method == 'PATCH'
            and self.instance.name == data
        )
        if check_name_not_updated:
            return data
        user = self.context['request'].user
        check_recipe_name_exists = (
            Recipe.objects.filter(name=data, author=user).exists()
        )
        if check_recipe_name_exists:
            raise serializers.ValidationError(
                f'У вас уже есть рецепт с названием {data}.'
            )
        return data

    def validate_ingredients(self, data):
        '''
        Validates that there is no duplicate ingredient in the recipe.
        '''
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
        '''
        Validates that there is no duplicate tag attached to the recipe.
        '''
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
        '''
        Annotates represenatation of newly created recipe
        with is_favorited and is_in_shoplist markers.
        Also annotates recipe author with current user subscribe status.
        '''
        if self.context['request'].method == 'POST':
            new_recipe = Recipe.objects.filter(pk=recipe_obj.pk)
            current_user = self.context.get('request').user
            new_recipe_annotated = annotated_recipes(
                new_recipe, current_user, authors_num=1
            ).first()
            return GetRecipeSerializer(new_recipe_annotated).data
        return GetRecipeSerializer(recipe_obj).data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context['request'].user
        )
        add_ingredients_to_recipe(recipe, ingredients)
        RecipeTag.objects.bulk_create(
            [RecipeTag(recipe=recipe, tag=tag) for tag in tags]
        )
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        super().update(instance, validated_data)
        instance.ingredients.clear()
        add_ingredients_to_recipe(instance, ingredients)
        return instance


class ShortRecipeSerializer(serializers.ModelSerializer):
    '''
    Short version of get GetRecipeSerializer, used as parent class for
    FavoriteRecipeSerializer and ShoplistRecipeSerializer
    to indicate fields required for adding or removing recipe objects from
    favorites and shoplist catalogs.
    Also used to represent recipes on subscriptions page.
    '''
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields


class FavoriteRecipeSerializer(ShortRecipeSerializer):

    def validate(self, data):
        '''
        Validate that recipe is not in favorites when added to
        or recipe is in favorites when deleted from it.
        '''
        user = self.context['request'].user
        check_favorite = FavoriteRecipe.objects.filter(
            user=user, recipe=self.instance
        ).exists()
        if self.context['request'].method == 'POST' and check_favorite:
            raise serializers.ValidationError(
                {'detail':
                    'Данный рецепт уже добавлен в раздел любимых рецептов.'}
            )
        elif self.context['request'].method == 'DELETE' and not check_favorite:
            raise serializers.ValidationError(
                {'detail':
                    'Данного рецепта нет в разделе любимых рецептов.'}
            )
        return data

    def add_to_favorites(self, *args, **kwargs):
        user = self.context['request'].user
        FavoriteRecipe.objects.create(
            user=user, recipe=self.instance
        )

    def remove_from_favorites(self):
        user = self.context.get('request').user
        get_object_or_404(
            FavoriteRecipe, user=user, recipe=self.instance
        ).delete()


class ShoplistRecipeSerializer(ShortRecipeSerializer):

    def validate(self, data):
        '''
        Validate that recipe is not in shoplist when added to
        or recipe is in favorites when deleted from it.
        '''
        user = self.context['request'].user
        check_object = ShoplistRecipe.objects.filter(
            user=user, recipe=self.instance
        ).exists()
        if self.context['request'].method == 'POST' and check_object:
            raise serializers.ValidationError(
                {'detail': 'Вы уже добавляли данный рецепт в список покупок.'}
            )
        elif self.context['request'].method == 'DELETE' and not check_object:
            raise serializers.ValidationError(
                {'detail': 'Данного рецепта нет в списке покупок.'}
            )
        return data

    def add_to_shoplist(self, *args, **kwargs):
        user = self.context['request'].user
        ShoplistRecipe.objects.create(
            user=user, recipe=self.instance
        )

    def remove_from_shoplist(self, *args, **kwargs):
        user = self.context['request'].user
        get_object_or_404(
            ShoplistRecipe, user=user, recipe=self.instance
        ).delete()


class SubscribeSerializer(GetFoodgramUserSerializer):

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed',
            'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        '''
        Limits returned recipes to three items for each followed user.
        '''
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit', 3
        )
        recipes_to_show = obj.recipes.all()[:int(recipes_limit)]
        serializer = ShortRecipeSerializer(recipes_to_show, many=True)
        return serializer.data

    def subscribe(self, *args, **kwargs):
        current_user = self.context['request'].user
        followed_user = self.instance
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
        unfollowed_user = self.instance
        try:
            follow_object = Follow.objects.get(
                follower=current_user, author=unfollowed_user
            )
        except Follow.DoesNotExist:
            raise serializers.ValidationError(
                {'detail': 'Вы не подписаны на данного автора.'}
            )
        else:
            follow_object.delete()
