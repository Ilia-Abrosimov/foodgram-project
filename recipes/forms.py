from django import forms
from .models import Recipe, Tag


class RecipeForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'tags__checkbox'}),
        to_field_name='slug',
        required=False
    )

    class Meta:
        model = Recipe
        fields = ('title', 'tags', 'ingredients', 'time', 'description', 'image')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form__input'}),
            'time': forms.NumberInput(
                attrs={'class': 'form__input',
                       'id': 'id_time',
                       'time': 'time'}),
            'description': forms.Textarea(attrs={'class': 'form__textarea',
                                                 'rows': '6'}),
        }
        labels = {
            'image': 'Загрузить фото'
        }