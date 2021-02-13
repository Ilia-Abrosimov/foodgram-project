from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from django.views.generic.list import MultipleObjectMixin
from .models import Recipe, User, Follow, Favorites, ShopList, Tag
from django.views.generic import ListView, DetailView
from .forms import RecipeForm
from django.views.decorators.http import (require_GET, require_http_methods,
                                          require_POST)
import json
from django.http import HttpResponse, JsonResponse


def _extend_context(context, user):
    # context['purchase_list'] = ShopList.purchase.get_purchases_list(user)
    context['favorites'] = Favorites.objects.filter(user=user)
    return context


def _add_subscription_status(context, user, author):
    context['is_subscribed'] = Follow.objects.filter(
        user=user, author=author
    ).exists()
    return context


def tag_filter(model, tags):
    if tags:
        return model.objects.prefetch_related(
                'author', 'tags'
            ).filter(
                tags__slug__in=tags
            ).distinct()
    else:
        return model.objects.prefetch_related(
                'author', 'tags'
            ).all()


@require_GET
def index(request):
    tags = request.GET.getlist('tag')
    recipe_list = tag_filter(Recipe, tags)
    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'tags': Tag.objects.all(),
        'page': page,
        'paginator': paginator
    }
    user = request.user
    if user.is_authenticated:
        context['active'] = 'recipe'
        _extend_context(context, user)
    return render(request, 'index.html', context)


@require_GET
def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    context = {
        'recipe': recipe,
    }
    user = request.user
    if user.is_authenticated:
        _add_subscription_status(context, user, recipe.author)
        _extend_context(context, user)
    return render(request, 'recipe_detail.html', context)


@require_GET
def profile(request, user_id):
    profile = get_object_or_404(User, id=user_id)
    tags = request.GET.getlist('tag')
    recipe_list = tag_filter(Recipe, tags)
    paginator = Paginator(recipe_list.filter(author=profile), 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'tags': Tag.objects.all(),
        'profile': profile,
        'page': page,
        'paginator': paginator
    }
    user = request.user
    if user.is_authenticated:
        _add_subscription_status(context, user, profile)
        _extend_context(context, user)
    return render(request, 'profile.html', context)


@login_required
def follow_index(request):
    queryset = Follow.objects.filter(user=request.user)
    paginator = Paginator(queryset, 6)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request,
                  "follow.html",
                  {"page": page,
                   "paginator": paginator,
                   "page_number": page_number})


@login_required(login_url='auth/login/')
@require_POST
def subscription(request):
    json_data = json.loads(request.body.decode())
    author = get_object_or_404(User, id=json_data['id'])
    is_exist = Follow.objects.filter(
        user=request.user, author=author).exists()
    data = {'success': 'true'}
    if is_exist:
        data['success'] = 'false'
    else:
        Follow.objects.create(user=request.user, author=author)
    return JsonResponse(data)


@login_required(login_url='auth/login/')
@require_http_methods('DELETE')
def delete_subscription(request, author_id):
    author = get_object_or_404(User, id=author_id)
    data = {'success': 'true'}
    follow = Follow.objects.filter(
        user=request.user, author=author)
    if not follow:
        data['success'] = 'false'
    follow.delete()
    return JsonResponse(data)


def favorite_index(request):
    tags = request.GET.getlist('tag')
    queryset = Favorites.objects.filter(user=request.user)
    recipe_list = [i.recipes for i in queryset]
    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'tags': Tag.objects.all(),
        'page': page,
        'paginator': paginator
    }
    # user = request.user
    # if user.is_authenticated:
    #     context['active'] = 'recipe'
    #     _extend_context(context, user)
    print(recipe_list)
    return render(request, 'favorites.html', context)


@login_required(login_url='auth/login/')
@require_http_methods('DELETE')
def delete_favorite(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    data = {'success': 'true'}
    try:
        favorite = Favorites.favorite.get(user=request.user)
    except ObjectDoesNotExist:
        data['success'] = 'false'
    if not favorite.recipes.filter(id=recipe_id).exists():
        data['success'] = 'false'
    favorite.recipes.remove(recipe)
    return JsonResponse(data)


@login_required
def shoplistview(request):
    queryset = ShopList.objects.all().filter(user=request.user)
    recipes = [i.recipe for i in queryset]
    return render(request,
                  "shoplist.html",
                  {"page": recipes})


@login_required
def new_recipe(request):
    form = RecipeForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        recipe = form.save(commit=False)
        recipe.author = request.user
        recipe.save()
        return redirect('index')
    return render(request, '123.html', {'form': form})
