from django.contrib import admin
from .models import Products, Recipe, Ingredient, Tag, Follow, Favorites


class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 3


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("title", "pub_date", "author")
    search_fields = ("description",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"
    inlines = (IngredientInline,)


class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "unit")
    search_fields = ("description",)


class TagAdmin(admin.ModelAdmin):
    list_display = ("title", "slug")


class FollowAdmin(admin.ModelAdmin):
    list_display = ("user", 'author')


class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('user', 'created')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Products, ProductAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Favorites, FavoritesAdmin)
