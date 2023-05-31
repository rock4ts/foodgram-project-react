from django.conf import settings
from django.db.models import Exists, OuterRef, Prefetch
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.pdfgen import canvas
from reportlab.rl_config import TTFSearchPath

from recipes.models import FavoriteRecipe, RecipeIngredient, ShoplistRecipe
from users.models import Follow, User


def add_ingredients_to_recipe(recipe, ingredients):
    '''
    Bulk creates RecipeIngredient objects when recipe is created or updated.
    '''
    RecipeIngredient.objects.bulk_create(
        [
            RecipeIngredient(
                recipe=recipe,
                ingredient=dict(ingredient)['id'],
                amount=dict(ingredient)['amount']
            ) for ingredient in ingredients
        ]
    )


def annotate_subscribe_status(authors_queryset, follower_object):
    '''Annotates author queryset with authorised user subscribe status.'''
    is_subscribed = Follow.objects.filter(
        follower=follower_object.pk,
        author=OuterRef('pk')
    )
    return authors_queryset.annotate(is_subscribed=Exists(is_subscribed))


def annotate_favorites_and_shoplist(recipes_qset, user_object):
    '''
    Annotates recipe queryset with favorites and shoplist status
    for authorised user.
    '''
    is_favorited = FavoriteRecipe.objects.filter(
        user=user_object.pk,
        recipe=OuterRef('pk')
    )
    is_in_shoplist_cart = ShoplistRecipe.objects.filter(
        user=user_object.pk,
        recipe=OuterRef('pk')
    )
    return recipes_qset.annotate(
        is_favorited=Exists(is_favorited)
    ).annotate(is_in_shopping_cart=Exists(is_in_shoplist_cart))


def annotated_recipes(recipes, current_user, authors_num=None):
    '''
    Annotates recipes with is_favorited and is_in_shoplist markers.
    Also annotates recipe author with authorised user subscribe status.
    '''
    if authors_num == 1:
        authors_annotated = Prefetch(
            'author', queryset=annotate_subscribe_status(
                User.objects.filter(pk=current_user.pk), current_user
            )
        )
    else:
        authors_annotated = Prefetch(
            'author', queryset=annotate_subscribe_status(
                User.objects.all(), current_user
            )
        )
    recipes_with_prefetche = recipes.prefetch_related(
        authors_annotated, 'tags', 'ingredients'
    )
    return annotate_favorites_and_shoplist(
        recipes_with_prefetche, current_user
    )


def shoplist_to_pdf(shoplist_ingredients):
    '''
    Renders pdf file that contains
    authorised user shoplist ingredients in human-readable format.
    '''
    begin_position_x, begin_position_y = 30, 730
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        'attachment; filename="shopping_list.pdf"'
    )
    plane = canvas.Canvas(response, pagesize=A4)
    TTFSearchPath.append(str(settings.BASE_DIR) + '/reportlabs/fonts')
    pdfmetrics.registerFont(ttfonts.TTFont('FreeSans', 'FreeSans.ttf'))
    plane.setFont('FreeSans', 25)
    plane.setTitle('Список покупок')
    plane.drawString(
        begin_position_x, begin_position_y + 40, 'Список покупок: '
    )
    plane.setFont('FreeSans', 18)
    for number, item in enumerate(shoplist_ingredients, start=1):
        if begin_position_y < 100:
            begin_position_y = 730
            plane.showPage()
            plane.setFont('FreeSans', 18)
        plane.drawString(
            begin_position_x,
            begin_position_y,
            f'{number}: {item["ingredient__name"]} - '
            f'{item["ingredient_total"]} '
            f'{item["ingredient__measurement_unit"]}'
        )
        begin_position_y -= 30
    plane.showPage()
    plane.save()
    return response
