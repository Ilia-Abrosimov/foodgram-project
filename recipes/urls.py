from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (index, recipe_detail, profile, follow_index,
                    favorite_index, shoplistview, new_recipe, subscription,
                    delete_subscription, add_favorite, delete_favorite,
                    add_purchase, delete_purchase, get_ingredients, edit_recipe,
                    delete_recipe, download_pdf)

urlpatterns = [
    path('', index, name='index'),
    path('recipes/<int:recipe_id>/', recipe_detail, name='recipe'),
    path('recipes/<int:recipe_id>/edit/', edit_recipe, name='edit_recipe'),
    path('recipes/<int:recipe_id>/delete', delete_recipe, name='delete_recipe'),
    path('users/<int:user_id>', profile, name='profile'),
    path('follows', follow_index, name='follows'),
    path('subscriptions', subscription, name='subscription'),
    path('subscriptions/<int:author_id>', delete_subscription,
         name='delete_subscription'),
    path('favorites/', favorite_index, name='favorite'),
    path('add-favorite', add_favorite, name='add_favorite'),
    path('del-favorite/<int:recipe_id>', delete_favorite, name='del-favorite'),
    path('purchases/', shoplistview, name='purchases'),
    path('add-purchase', add_purchase, name='add-purchase'),
    path('del-purchase/<int:recipe_id>', delete_purchase, name='del-purchase'),
    path('ingredients', get_ingredients, name='ingredients'),
    path('new/', new_recipe, name='new'),
    path('download_shoplist', download_pdf, name='download_shoplist'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)