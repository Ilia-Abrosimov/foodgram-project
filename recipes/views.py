import json
from urllib.parse import unquote

import reportlab
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import (require_GET, require_http_methods,
                                          require_POST)
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from foodgram.settings import PAGINATE_BY

from .forms import RecipeForm
from .models import (Favourite, Follow, Ingredient, Product, Recipe, ShopList,
                     Tag, User)
from .utils import add_subscription_status, extend_context, tag_filter


@require_GET
def index(request):
    tags = request.GET.getlist('tag')
    recipe_list = tag_filter(Recipe, tags)
    paginator = Paginator(recipe_list, PAGINATE_BY)
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
        extend_context(context, user)
    return render(request, 'index.html', context)


@require_GET
def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    context = {
        'recipe': recipe,
    }
    user = request.user
    if user.is_authenticated:
        add_subscription_status(context, user, recipe.author)
        extend_context(context, user)
    return render(request, 'recipes/recipe_detail.html', context)


@require_GET
def profile(request, user_id):
    author = get_object_or_404(User, id=user_id)
    tags = request.GET.getlist('tag')
    recipe_list = tag_filter(Recipe, tags)
    paginator = Paginator(recipe_list.filter(author=author), PAGINATE_BY)
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
        add_subscription_status(context, user, author)
        extend_context(context, user)
    return render(request, 'recipes/profile.html', context)


@login_required(login_url='/auth/login/')
def follow_index(request):
    queryset = request.user.follower.all()
    paginator = Paginator(queryset, PAGINATE_BY)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request,
                  "recipes/follow.html",
                  {"page": page,
                   "paginator": paginator,
                   "page_number": page_number})


@login_required(login_url='auth/login/')
@require_POST
def add_subscription(request):
    json_data = json.loads(request.body.decode())
    author_id = json_data.get('id')
    if not author_id:
        return JsonResponse({'success': 'false', 'massage': 'id not found'},
                            status=400)
    author = get_object_or_404(User, id=author_id)
    follow = Follow.objects.filter(user=request.user, author=author)
    data = {'success': 'true'}
    if follow.exists():
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
    if not follow.exists():
        data['success'] = 'false'
    follow.delete()
    return JsonResponse(data)


@login_required(login_url='/auth/login/')
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
    paginator = Paginator(recipe_list, PAGINATE_BY)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'tags': Tag.objects.all(),
        'page': page,
        'paginator': paginator
    }
    if user.is_authenticated:
        extend_context(context, user)
    return render(request, 'recipes/favorites.html', context)


@login_required(login_url='auth/login/')
@require_POST
def add_favorite(request):
    json_data = json.loads(request.body.decode())
    recipe_id = json_data.get('id')
    if not recipe_id:
        return JsonResponse({'success': 'false', 'massage': 'id not found'},
                            status=400)
    recipe = get_object_or_404(Recipe, id=recipe_id)
    data = {'success': 'true'}
    favorite = Favourite.objects.filter(user=request.user, recipe=recipe)
    if favorite.exists():
        data['success'] = 'false'
    else:
        Favourite.objects.create(user=request.user, recipe=recipe)
    return JsonResponse(data)


@login_required(login_url='auth/login/')
@require_http_methods('DELETE')
def delete_favorite(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    data = {'success': 'true'}
    favorite = Favourite.objects.filter(user=request.user, recipe=recipe)
    if not favorite.exists():
        data['success'] = 'false'
    favorite.delete()
    return JsonResponse(data)


@login_required(login_url='/auth/login/')
def purchases(request):
    user = request.user
    recipes = user.shop_list.all()
    return render(request, "recipes/purchases.html", {"page": recipes})


@login_required(login_url='auth/login/')
@require_POST
def add_purchase(request):
    json_data = json.loads(request.body.decode())
    recipe_id = json_data.get('id')
    if not recipe_id:
        return JsonResponse({'success': 'false', 'massage': 'id not found'},
                            status=400)
    recipe = get_object_or_404(Recipe, id=recipe_id)
    data = {'success': 'true'}
    purchase = ShopList.objects.filter(user=request.user, recipe=recipe)
    if purchase.exists():
        data['success'] = 'false'
    else:
        ShopList.objects.create(user=request.user, recipe=recipe)
    return JsonResponse(data)


@login_required(login_url='auth/login/')
@require_http_methods('DELETE')
def delete_purchase(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    data = {'success': 'true'}
    purchase = ShopList.objects.filter(user=request.user, recipe=recipe)
    if not purchase.exists():
        data['success'] = 'false'
    purchase.delete()
    return JsonResponse(data)


@login_required(login_url='auth/login/')
@require_GET
def get_ingredients(request):
    query = unquote(request.GET.get('query'))
    data = list(Product.objects.filter(
        title__startswith=query
    ).values(
        'title', 'unit'))
    return JsonResponse(data, safe=False)


@login_required(login_url='/auth/login/')
@require_http_methods(['GET', 'POST'])
def new_recipe(request):
    form = RecipeForm(request.POST or None, files=request.FILES or None,
                      initial={'author': request.user})
    if form.is_valid():
        form.save()
        return redirect('index')
    return render(request, 'recipes/recipe_new.html', {'form': form})


@login_required(login_url='/auth/login/')
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if recipe.author != request.user:
        return redirect('recipe', id=recipe_id)
    form = RecipeForm(request.POST or None, files=request.FILES or None,
                      instance=recipe, initial={'author': request.user})
    tags = recipe.tags.all()
    ingredients = Ingredient.objects.filter(recipe=recipe).all()
    context = {'form': form,
               'is_created': True,
               'recipe_id': recipe.id,
               'tags': tags,
               'ingredients': ingredients}
    if form.is_valid():
        form.save()
        return redirect('recipe', recipe.id)
    return render(request, 'recipes/recipe_new.html', context)


@login_required(login_url='/auth/login/')
@require_GET
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if recipe.author == request.user:
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
    if shop_list.count() == 0:
        return redirect('purchases')
    for el in shop_list:
        ingredients = Ingredient.objects.filter(recipe=el.recipe.id)
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
