import random
from django.shortcuts import render
from .forms import UserInputForm
from .models import Recipe
from django.db import connection

def home(request):
    return render(request, 'meal_recommendation/home.html')

def recommend_meal_plan(request):
    if request.method == "POST":
        form = UserInputForm(request.POST)
        if form.is_valid():
            # Extract user inputs
            age = form.cleaned_data['age']
            height = form.cleaned_data['height']
            weight = form.cleaned_data['weight']
            gender = form.cleaned_data['gender']
            activity_level = form.cleaned_data['activity_level']
            fitness_goals = form.cleaned_data['fitness_goals']
            dietary_preference = form.cleaned_data['dietary_preference']
            allergens = form.cleaned_data['allergens']

            # Calculate daily calorie needs
            if gender == 'M':
                bmr = 10 * weight + 6.25 * height - 5 * age + 5
            else:
                bmr = 10 * weight + 6.25 * height - 5 * age - 161

            activity_multiplier = {
                'sedentary': 1.2,
                'light': 1.375,
                'moderate': 1.55,
                'active': 1.725,
                'very_active': 1.9,
            }
            daily_calories = bmr * activity_multiplier[activity_level]

            if fitness_goals == 'lose':
                daily_calories -= 500  # Calorie deficit
            elif fitness_goals == 'gain':
                daily_calories += 500  # Calorie surplus

            # Divide daily calories among meals
            meals_per_day = {
                "Breakfast": 0.25 * daily_calories,
                "Lunch": 0.35 * daily_calories,
                "Dinner": 0.3 * daily_calories,
                "Snacks": 0.1 * daily_calories,
            }

            # Track used recipes to avoid repetition
            used_recipes = set()

            # Fetch recipes from PostgreSQL based on dietary preference, allergens, and calories
            weekly_plan = {}
            for day in range(7):
                day_plan = {}
                for meal, calorie_target in meals_per_day.items():
                    query = f"""
                        SELECT name, calories, category, prep_time, cook_time, ingredients, protein, fat, carbs 
                        FROM recipes
                        WHERE category = %s 
                        AND calories IS NOT NULL 
                        AND NOT EXISTS (
                            SELECT 1 FROM unnest(string_to_array(ingredients, ', ')) AS ing
                            WHERE ing ILIKE ANY (ARRAY[%s])
                        )
                        AND name NOT IN %s
                        ORDER BY ABS(calories - %s)
                        LIMIT 1
                    """
                    with connection.cursor() as cursor:
                        allergens_array = [f"%{allergen}%" for allergen in allergens] if allergens else []
                        cursor.execute(query, [
                            dietary_preference,
                            allergens_array,
                            tuple(used_recipes) if used_recipes else ('dummy_recipe',),
                            calorie_target
                        ])
                        result = cursor.fetchone()

                    if result:
                        recipe_name, recipe_calories, category, prep_time, cook_time, ingredients, protein, fat, carbs = result
                        day_plan[meal] = {
                            'name': recipe_name,
                            'calories': recipe_calories,
                            'category': category,
                            'prep_time': prep_time,
                            'cook_time': cook_time,
                            'ingredients': ingredients,
                            'protein': protein,
                            'fat': fat,
                            'carbs': carbs
                        }
                        used_recipes.add(recipe_name)
                    else:
                        day_plan[meal] = None  # No recipe available

                weekly_plan[f"Day {day + 1}"] = day_plan

            # Render the weekly plan
            return render(request, 'meal_recommendation/result.html', {
                'weekly_plan': weekly_plan,
                'daily_calories': daily_calories,
            })
    else:
        form = UserInputForm()

    return render(request, 'meal_recommendation/form.html', {'form': form})
