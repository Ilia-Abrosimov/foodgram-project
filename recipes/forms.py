from django import forms

from .models import Ingredient, Product, Recipe, Tag
from .utils import get_ingredients_from_form


class RecipeForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'tags__checkbox'}),
        to_field_name='slug',
        required=False
    )

    class Meta:
        model = Recipe
        fields = ('title', 'tags', 'ingredients', 'time', 'description',
                  'image')

    def clean_ingredients(self):
        ingredient_names = self.data.getlist('nameIngredient')
        ingredient_units = self.data.getlist('unitsIngredient')
        ingredient_amounts = self.data.getlist('valueIngredient')
        ingredients_clean = []
        for ingredient in zip(ingredient_names, ingredient_units,
                              ingredient_amounts):
            if int(ingredient[2]) < 0:
                raise forms.ValidationError('Количество ингредиентов должно '
                                            'быть больше нуля')
            elif not Product.objects.filter(title=ingredient[0]).exists():
                raise forms.ValidationError(
                    'Ингредиенты должны быть из списка')
            else:
                ingredients_clean.append({'title': ingredient[0],
                                          'unit': ingredient[1],
                                          'amount': ingredient[2]})
        if not ingredients_clean:
            raise forms.ValidationError('Добавьте ингредиент')
        return ingredients_clean

    def clean_title(self):
        data = self.cleaned_data['title']
        if not data:
            raise forms.ValidationError('Добавьте название рецепта')
        return data

    def clean_description(self):
        data = self.cleaned_data['description']
        if not data:
            raise forms.ValidationError('Добавьте описание рецепта')
        return data

    def clean_tags(self):
        data = self.cleaned_data['tags']
        if not data:
            raise forms.ValidationError('Добавьте тег')
        return data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.author = self.initial['author']
        instance.save()
        ingredients = self.cleaned_data['ingredients']
        self.cleaned_data['ingredients'] = []
        self.save_m2m()
        Ingredient.objects.bulk_create(
            get_ingredients_from_form(ingredients, instance))
        return instance
