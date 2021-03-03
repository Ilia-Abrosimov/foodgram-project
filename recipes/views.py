import json
from urllib.parse import unquote

import reportlab
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import (require_GET, require_http_methods,
                                          require_POST)
from django.views.generic import TemplateView
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from .forms import RecipeForm
from .models import (
    Favorites, Follow, Ingredient, Products, Recipe, ShopList, Tag, User)


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
    return render(request, 'recipes/recipe_detail.html', context)


@require_GET
def profile(request, user_id):
    author = get_object_or_404(User, id=user_id)
    tags = request.GET.getlist('tag')
    recipe_list = tag_filter(Recipe, tags)
    paginator = Paginator(recipe_list.filter(author=author), 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'tags': Tag.objects.all(),
        'author': author,
        'page': page,
        'paginator': paginator
    }
    user = request.user
    if user.is_authenticated:
        _add_subscription_status(context, user, author)
        _extend_context(context, user)
    return render(request, 'recipes/profile.html', context)


@login_required(login_url='auth/login/')
def follow_index(request):
    queryset = Follow.objects.filter(user=request.user)
    paginator = Paginator(queryset, 6)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request,
                  "recipes/follow.html",
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
    return render(request, 'recipes/favorites.html', context)


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
def purchases(request):
    user = request.user
    recipes = user.shop_list.all()
    return render(request, "recipes/purchases.html", {"page": recipes})


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


@login_required(login_url='auth/login/')
@require_GET
def get_ingredients(request):
    query = unquote(request.GET.get('query'))
    data = list(Products.objects.filter(
        title__startswith=query
    ).values(
        'title', 'unit'))
    a = JsonResponse(data, safe=False)
    return a


@login_required(login_url='auth/login/')
def new_recipe(request):
    form = RecipeForm(request.POST or None, files=request.FILES or None)
    if request.method == "POST":
        tags = request.POST.getlist('tags')
        ingredients = request.POST.getlist('nameIngredient')
        value_ing = request.POST.getlist('valueIngredient')
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            for tag in tags:
                recipe.tags.add(Tag.objects.get(slug=tag))
            ing = []
            for ingredient, value in zip(ingredients, value_ing):
                product = Products.objects.get(title=ingredient)
                ing.append(Ingredient(ingredient=product, recipe=recipe,
                                      amount=value))
            Ingredient.objects.bulk_create(ing)
            return redirect('index')
        return render(request, 'recipes/recipe_new.html', {'form': form})
    return render(request, 'recipes/recipe_new.html', {'form': form})


@login_required(login_url='auth/login/')
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if recipe.author != request.user:
        return redirect('recipe', id=recipe_id)
    if recipe.author == request.user:
        form = RecipeForm(request.POST or None, files=request.FILES or None,
                          instance=recipe)
        recipe_tags = Tag.objects.filter(recipe=recipe_id)
        tags = [el.slug for el in recipe_tags]
        recipe_ingredients = Ingredient.objects.filter(recipe=recipe_id)
        context = {'form': form,
                   'tags': tags,
                   "ing_list": recipe_ingredients,
                   'is_created': True,
                   'recipe_id': recipe.id}
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            tags = request.POST.getlist('tags')
            ingredients = request.POST.getlist('nameIngredient')
            value_ing = request.POST.getlist('valueIngredient')
            recipe.tags.clear()
            recipe.ingredients.clear()
            for tag in tags:
                recipe.tags.add(Tag.objects.get(slug=tag))
            ing = []
            for ingredient, value in zip(ingredients, value_ing):
                product = Products.objects.get(title=ingredient)
                ing.append(Ingredient(ingredient=product, recipe=recipe,
                                      amount=value.replace(',', '.')))
            Ingredient.objects.bulk_create(ing)
            return redirect('index')
        return render(request, 'recipes/recipe_new.html', context)


@login_required(login_url='auth/login/')
@require_GET
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if recipe.author != request.user:
        return redirect("index")
    recipe.delete()
    return redirect('index')


@login_required
def download_pdf(request):
    reportlab.rl_config.TTFSearchPath.append(
        str(settings.BASE_DIR) + "/Library/Fonts/"
    )
    user = get_object_or_404(User, username=request.user)
    ing_dict = {}
    shop_list = ShopList.objects.filter(user=user)
    if len(shop_list) == 0:
        return redirect('purchases')
    for el in shop_list:
        ingredients = Ingredient.objects.filter(recipe=el.recipes.id)
        for ingredient in ingredients:
            name = ingredient.ingredient.title
            count = ingredient.amount
            dimension = ingredient.ingredient.unit
            if name not in ing_dict:
                ing_dict[name] = [count, dimension]
            else:
                ing_dict[name][0] += count
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="shopList.pdf"'
    p = canvas.Canvas(response, pagesize=A4)
    pdfmetrics.registerFont(TTFont("Arial", "arial.ttf"))
    p.setFont("Arial", 20)
    x = 50
    y = 750
    for num, el in enumerate(ing_dict):
        if y <= 100:
            y = 700
            p.showPage()
            p.setFont("Arial", 20)
        p.drawString(
            x, y, f"№{num + 1}: {el} - {ing_dict[el][0]} {ing_dict[el][1]}"
        )
        y -= 30
    p.showPage()
    p.save()
    return response


class AboutAuthorView(TemplateView):
    template_name = 'static_templates/about-author.html'


class AboutTechView(TemplateView):
    template_name = 'static_templates/about-tech.html'
