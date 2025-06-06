from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('recommend/', views.recommend_meal_plan, name='recommend_meal_plan'),
]
