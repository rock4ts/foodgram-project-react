from django.conf import settings
from django.db.models import Exists, OuterRef
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.pdfgen import canvas
from reportlab.rl_config import TTFSearchPath

from recipes.models import FavoriteRecipe, ShoplistRecipe
from users.models import Follow


def annotate_subscribe_status(authors_queryset, follower_object):
    is_subscribed = Follow.objects.filter(
        follower=follower_object.pk,
        author=OuterRef('pk')
    )
    return authors_queryset.annotate(is_subscribed=Exists(is_subscribed))


def annotate_favorites_and_shoplist(recipes_qset, user_object):
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


def shoplist_to_pdf(shoplist_queryset):
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
    for number, item in enumerate(shoplist_queryset, start=1):
        if begin_position_y < 100:
            begin_position_y = 730
            plane.showpage()
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
