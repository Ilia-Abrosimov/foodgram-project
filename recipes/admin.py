from django.contrib import admin
from .models import (Products, Recipe, Ingredient, Tag, Follow, Favorites,
                     ShopList)


class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 3


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("title", "author")
    list_filter = ("author", "title", "tags")
    empty_value_display = "-пусто-"
    inlines = (IngredientInline,)


class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "unit")
    list_filter = ("title",)


class TagAdmin(admin.ModelAdmin):
    list_display = ("title", "slug")


class FollowAdmin(admin.ModelAdmin):
    list_display = ("user", 'author')


class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipes', 'created')

    # def show_recipes(self, obj):
    #     recipes = obj.recipes.all()
    #     return '\n'.join([recipe.title for recipe in recipes])


class ShoplistAdmin(admin.ModelAdmin):
    list_display = ('user', 'show_recipes', 'created')

    def show_recipes(self, obj):
        recipes = obj.recipes.all()
        return '\n'.join([recipe.title for recipe in recipes])


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Products, ProductAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Favorites, FavoritesAdmin)
admin.site.register(ShopList, ShoplistAdmin)
admin.site.register(Ingredient, IngredientAdmin)
