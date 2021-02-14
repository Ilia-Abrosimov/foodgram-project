from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (index, recipe_detail, profile, follow_index,
                    favorite_index, shoplistview, new_recipe, subscription,
                    delete_subscription, add_favorite, delete_favorite,
                    add_purchase, delete_purchase)

urlpatterns = [
    path('', index, name='index'),
    path('recipes/<int:recipe_id>/', recipe_detail, name='recipe'),
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
    path('new/', new_recipe, name='new'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)