from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import RecipesListView, RecipeView, ProfileView, follow_index, favorites

urlpatterns = [
    path('', RecipesListView.as_view(), name='index'),
    path('recipes/<int:pk>/', RecipeView.as_view(), name='recipe'),
    path('users/<str:username>/', ProfileView.as_view(), name='profile'),
    path('subscriptions/', follow_index, name='subscription'),
    path('favorites/', favorites, name='favorite'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)