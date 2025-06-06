from django import forms

class UserInputForm(forms.Form):
    age = forms.IntegerField(label="Age")
    height = forms.IntegerField(label="Height (in cm)")
    weight = forms.IntegerField(label="Weight (in kg)")

    gender = forms.ChoiceField(
        choices=[('M', 'Male'), ('F', 'Female')],
        label="Gender"
    )

    activity_level = forms.ChoiceField(
        choices=[
            ('sedentary', 'Sedentary (little to no exercise)'),
            ('light', 'Lightly Active (light exercise/sports 1-3 days per week)'),
            ('moderate', 'Moderately Active (moderate exercise/sports 3-5 days per week)'),
            ('active', 'Active (intense exercise/sports 6-7 days per week)'),
            ('very_active', 'Very Active (very intense exercise, physical job)'),
        ],
        label="Activity Level"
    )

    fitness_goals = forms.ChoiceField(
        choices=[
            ('lose', 'Lose Weight'),
            ('maintain', 'Maintain Weight'),
            ('gain', 'Gain Weight')
        ],
        label="Fitness Goals"
    )

    dietary_preference = forms.ChoiceField(
        choices=[
            ('Healthy', 'Healthy'),
            ('Vegetarian', 'Vegetarian'),
            ('Low Carb', 'Low Carb'),
            ('High Protein', 'High Protein'),
            ('Vegan', 'Vegan'),
        ],
        label="Dietary Preference"
    )

    allergens = forms.MultipleChoiceField(
        choices=[
            ('lactose', 'Lactose Intolerant'),
            ('beef', 'Beef'),
            ('gluten', 'Gluten'),
            ('chicken', 'Chicken'),
            ('peanuts', 'Peanuts'),
            ('shellfish', 'Shellfish'),
            ('soy', 'Soy'),
            ('eggs', 'Eggs'),
            ('fish', 'Fish'),
            ('other', 'Other (specify below)'),
        ],
        widget=forms.CheckboxSelectMultiple,
        label="Allergens",
        required=False
    )

    other_allergen = forms.CharField(
        label="If Other, specify:",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter custom allergen'})
    )
