from django.db import models

class Ingredient(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(
        max_length=50,
        choices=[
            ('Healthy', 'Healthy'),
            ('Vegetarian', 'Vegetarian'),
            ('Low Carb', 'Low Carb'),
            ('High Protein', 'High Protein'),
            ('Vegan', 'Vegan'),
            ('Snacks', 'Snacks'),
        ]
    )
    total_time = models.CharField(max_length=50, null=True, blank=True)
    prep_time = models.CharField(max_length=50, null=True, blank=True)
    cook_time = models.CharField(max_length=50, null=True, blank=True)
    calories = models.FloatField(null=True, blank=True)
    fat = models.FloatField(null=True, blank=True)
    protein = models.FloatField(null=True, blank=True)
    carbs = models.FloatField(null=True, blank=True)
    fiber = models.FloatField(null=True, blank=True)
    sugar = models.FloatField(null=True, blank=True)
    ingredients = models.ManyToManyField(Ingredient)
    preparation_steps = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
