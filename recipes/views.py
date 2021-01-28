from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.generic.list import MultipleObjectMixin

from .models import Recipe, User, Follow, Favorites
from django.views.generic import ListView, DetailView


class RecipesListView(ListView):
    model = Recipe
    template_name = 'index.html'
    paginate_by = 6
    context_object_name = 'page'


class RecipeView(DetailView):
    model = Recipe
    template_name = 'recipe_detail.html'
    context_object_name = 'recipe'


class ProfileView(DetailView, MultipleObjectMixin):
    model = User
    template_name = 'profile.html'
    slug_field = "username"
    slug_url_kwarg = 'username'
    context_object_name = 'page'
    paginate_by = 6

    def get_context_data(self, **kwargs):
        object_list = Recipe.objects.filter(author=self.get_object())
        return super().get_context_data(object_list=object_list, **kwargs)


@login_required
def follow_index(request):
    posts = Follow.objects.all().filter(author__following__user=request.user)
    paginator = Paginator(posts, 6)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request,
                  "follow.html",
                  {"page": page,
                   "paginator": paginator,
                   "page_number": page_number})


def favorites(request):
    posts = Favorites.objects.all().filter(user=request.user)
    paginator = Paginator(posts, 6)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request,
                  "123.html",
                  {"page": page,
                   "paginator": paginator,
                   "page_number": page_number})


