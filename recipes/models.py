from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    title = models.CharField(max_length=50, verbose_name='Название тега')
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.title


class Products(models.Model):
    title = models.CharField(max_length=50, verbose_name='Название продукта')
    unit = models.CharField(max_length=10, verbose_name='Единицы измерения')

    class Meta:
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.title}, {self.unit}'


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Подписчик',
                             help_text='Подписчик')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Автор',
                               help_text='Автор')

    class Meta:
        db_table = 'posts_follow'
        unique_together = ['user', 'author']
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.author}'


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipe',
                               verbose_name='Автор')
    title = models.CharField(max_length=50, verbose_name='Название рецепта')
    image = models.ImageField(upload_to='recipes/', blank=True, null=True)
    description = models.TextField(verbose_name='Текст')
    ingredients = models.ManyToManyField(Products, through='Ingredient',
                                         related_name='recipe',
                                         verbose_name='ингредиенты')
    tags = models.ManyToManyField(Tag, blank=True, related_name='recipe',
                                  verbose_name='Теги')
    time = models.PositiveIntegerField(verbose_name='Время приготовления')
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    favorite_by = models.ManyToManyField(User, through='Favorites',
                                         related_name='favorite_recipes',
                                         null=True, blank=True)
    purchase_by = models.ManyToManyField(User, through='ShopList',
                                         related_name='shop_list',
                                         null=True, blank=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.title}'


class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Products, on_delete=models.CASCADE)
    amount = models.FloatField(verbose_name='Количество ингредиента')

    class Meta:
        unique_together = ('ingredient', 'amount', 'recipe')
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return f'{self.amount}'


class Favorites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipes = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                                verbose_name='Избранное')
    created = models.DateTimeField("date published", auto_now_add=True)

    class Meta:
        ordering = ['-created']
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.recipes}'


class ShopList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipes = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                                verbose_name='Список покупок')
    created = models.DateTimeField("date of creation", auto_now_add=True)

    class Meta:
        ordering = ['-created']
        verbose_name_plural = 'Список покупок'

    def __str__(self):
        return f'{self.recipes}'
