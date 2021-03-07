from django.urls import path

from .views import (add_favorite, add_purchase, add_subscription,
                    delete_favorite, delete_purchase, delete_recipe,
                    delete_subscription, download_pdf, edit_recipe,
                    favorite_index, follow_index, get_ingredients, index,
                    new_recipe, profile, purchases, recipe_detail)

urlpatterns = [
    path('', index, name='index'),
    path('recipes/<int:recipe_id>/', recipe_detail, name='recipe'),
    path('recipes/<int:recipe_id>/edit/', edit_recipe, name='edit_recipe'),
    path('recipes/<int:recipe_id>/delete/', delete_recipe, name='delete_recipe'),
    path('users/<int:user_id>/', profile, name='profile'),
    path('follows/', follow_index, name='follows'),
    path('subscriptions/', add_subscription, name='subscription'),
    path('subscriptions/<int:author_id>/', delete_subscription,
         name='delete_subscription'),
    path('favorites/', favorite_index, name='favorite'),
    path('add-favorite/', add_favorite, name='add_favorite'),
    path('del-favorite/<int:recipe_id>/', delete_favorite, name='del-favorite'),
    path('purchases/', purchases, name='purchases'),
    path('add-purchase/', add_purchase, name='add-purchase'),
    path('del-purchase/<int:recipe_id>/', delete_purchase, name='del-purchase'),
    path('ingredients', get_ingredients, name='ingredients'),
    path('new/', new_recipe, name='new'),
    path('download_shoplist/', download_pdf, name='download_purchases'),
]
