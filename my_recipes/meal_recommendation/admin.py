from django.contrib import admin
from .models import Recipe, Ingredient

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'calories')
    filter_horizontal = ('ingredients',)

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name',)
