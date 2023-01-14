from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from recipes.models import FavoriteRecipe, ShoplistRecipe
from .models import Follow, User


class FollowersInline(admin.TabularInline):
    model = Follow
    fk_name = "follower"


class FollowingInline(admin.TabularInline):
    model = Follow
    fk_name = "author"


class FavoritesInline(admin.TabularInline):
    model = FavoriteRecipe


class ShoplistInline(admin.TabularInline):
    model = ShoplistRecipe


class AdminUser(UserAdmin):
    list_display = (
        "pk", "username", "email", "first_name", "last_name"
    )
    list_filter = ("groups",)
    search_fields = ("username", "email")
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {
            'fields': ('email', 'first_name', 'last_name'),
        }),
    )

    inlines = [
        FollowersInline,
        FollowingInline,
        FavoritesInline,
        ShoplistInline
    ]


admin.site.register(User, AdminUser)
