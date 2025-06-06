from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('meal_recommendation.urls')),  # Set meal_recommendation as the root app
]
