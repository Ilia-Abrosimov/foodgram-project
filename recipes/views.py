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
    context['purchase_list'] = Recipe.objects.filter(purchase_by=user)
    context['favorites'] = Recipe.objects.filter(favorite_by=user)
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


@login_required(login_url='auth/login/')
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


@login_required(login_url='auth/login/')
def favorite_index(request):
    tags = request.GET.getlist('tag')
    user = request.user
    recipe_lists = user.favorite_recipes.all()
    if tags:
        recipe_list = recipe_lists.prefetch_related(
                'author', 'tags'
            ).filter(
                tags__slug__in=tags
            ).distinct()
    else:
        recipe_list = recipe_lists.prefetch_related(
                'author', 'tags'
            ).all()
    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'tags': Tag.objects.all(),
        'page': page,
        'paginator': paginator
    }
    if user.is_authenticated:
        _extend_context(context, user)
    return render(request, 'favorites.html', context)


@login_required(login_url='auth/login/')
@require_POST
def add_favorite(request):
    json_data = json.loads(request.body.decode())
    recipe_id = json_data['id']
    recipe = get_object_or_404(Recipe, id=recipe_id)
    data = {'success': 'true'}
    favorite = Favorites.objects.filter(user=request.user, recipes=recipe)
    is_favorite = favorite.exists()
    if is_favorite:
        data['success'] = 'false'
    else:
        Favorites.objects.create(user=request.user, recipes=recipe)
    return JsonResponse(data)


@login_required(login_url='auth/login/')
@require_http_methods('DELETE')
def delete_favorite(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    data = {'success': 'true'}
    try:
        favorite = Favorites.objects.filter(user=request.user, recipes=recipe)
    except ObjectDoesNotExist:
        data['success'] = 'false'
    if not favorite.exists():
        data['success'] = 'false'
    favorite.delete()
    return JsonResponse(data)


@login_required(login_url='auth/login/')
def shoplistview(request):
    user = request.user
    recipes = user.shop_list.all()
    return render(request, "shoplist.html", {"page": recipes})


@login_required(login_url='auth/login/')
@require_POST
def add_purchase(request):
    json_data = json.loads(request.body.decode())
    recipe_id = json_data['id']
    recipe = get_object_or_404(Recipe, id=recipe_id)
    data = {'success': 'true'}
    purchase = ShopList.objects.filter(user=request.user, recipes=recipe)
    is_favorite = purchase.exists()
    if is_favorite:
        data['success'] = 'false'
    else:
        ShopList.objects.create(user=request.user, recipes=recipe)
    return JsonResponse(data)


@login_required(login_url='auth/login/')
@require_http_methods('DELETE')
def delete_purchase(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    data = {'success': 'true'}
    try:
        purchase = ShopList.objects.filter(user=request.user, recipes=recipe)
    except ObjectDoesNotExist:
        data['success'] = 'false'
    if not purchase.exists():
        data['success'] = 'false'
    purchase.delete()
    return JsonResponse(data)


@login_required
def new_recipe(request):
    form = RecipeForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        recipe = form.save(commit=False)
        recipe.author = request.user
        recipe.save()
        return redirect('index')
    return render(request, '123.html', {'form': form})
