from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = 'Теги'
        verbose_name = 'Теги'

    def __str__(self):
        return self.title


class Products(models.Model):
    title = models.CharField(max_length=100)
    unit = models.CharField(max_length=10)

    class Meta:
        verbose_name_plural = 'Ингредиенты'
        verbose_name = 'Ингредиенты'

    def __str__(self):
        return f'{self.title}, {self.unit}'


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower',
                             help_text='Подписчик')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following',
                               help_text='Автор')

    class Meta:
        db_table = 'posts_follow'
        unique_together = ['user', 'author']
        verbose_name_plural = 'Подписки'
        verbose_name = 'Подписки'

    def __str__(self):
        return f'{self.author}'


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipe')
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to='recipes/', blank=True, null=True)
    description = models.TextField()
    ingredients = models.ManyToManyField(Products, through='Ingredient',
                                         related_name='recipe')
    tags = models.ManyToManyField(Tag, blank=True, related_name='recipe')
    time = models.PositiveIntegerField()
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    favorite_by = models.ManyToManyField(User, through='Favorites',
                                         related_name='favorite_recipes',
                                         blank=True)
    purchase_by = models.ManyToManyField(User, through='ShopList',
                                         related_name='shop_list',
                                         blank=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name_plural = 'Рецепты'
        verbose_name = 'Рецепты'

    def __str__(self):
        return f'{self.title}'


class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Products, on_delete=models.CASCADE)
    amount = models.FloatField()

    class Meta:
        unique_together = ('ingredient', 'amount', 'recipe')
        verbose_name_plural = 'Продукты'
        verbose_name = 'Продукты'

    def __str__(self):
        return f'{self.amount}'


class Favorites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    created = models.DateTimeField('date published', auto_now_add=True)

    class Meta:
        ordering = ['-created']
        verbose_name_plural = 'Избранное'
        verbose_name = 'Избранное'

    def __str__(self):
        return f'{self.recipes}'


class ShopList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipes = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    created = models.DateTimeField('date of creation', auto_now_add=True)

    class Meta:
        ordering = ['-created']
        verbose_name_plural = 'Список покупок'
        verbose_name = 'Список покупок'

    def __str__(self):
        return f'{self.recipes}'
