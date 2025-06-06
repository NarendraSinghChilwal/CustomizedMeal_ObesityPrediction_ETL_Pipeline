from django.core.management.base import BaseCommand
from meal_recommendation.models import Recipe, Ingredient
import psycopg2

class Command(BaseCommand):
    help = "Sync recipes from PostgreSQL to Django models"

    def handle(self, *args, **kwargs):
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            database="Recipe",
            user="postgres",
            password="Performance@99",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()

        # Fetch data from the recipes table
        cursor.execute("SELECT * FROM recipes")
        rows = cursor.fetchall()

        # Get column names for reference
        columns = [desc[0] for desc in cursor.description]

        for row in rows:
            data = dict(zip(columns, row))

            # Create or update Recipe in Django
            recipe, created = Recipe.objects.update_or_create(
                name=data['name'],
                defaults={
                    'category': data['category'],
                    'total_time': data.get('total_time'),
                    'prep_time': data.get('prep_time'),
                    'cook_time': data.get('cook_time'),
                    'calories': data.get('calories'),
                    'fat': data.get('fat'),
                    'protein': data.get('protein'),
                    'carbs': data.get('carbs'),
                    'fiber': data.get('fiber'),
                    'sugar': data.get('sugar'),
                    'preparation_steps': data.get('preparation_steps'),
                }
            )

            # Sync ingredients
            ingredient_names = data['ingredients'].split(', ') if data.get('ingredients') else []
            for ingredient_name in ingredient_names:
                ingredient, _ = Ingredient.objects.get_or_create(name=ingredient_name)
                recipe.ingredients.add(ingredient)

            recipe.save()

        conn.close()
        self.stdout.write(self.style.SUCCESS("Successfully synced recipes from PostgreSQL to Django models."))
