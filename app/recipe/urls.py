"""
URL mappings for the recipe app.
"""
# include makes us be able to user urls by passing it in
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from recipe import views


router = DefaultRouter()
# This create a new endpoint /recipes,
# then assign all endpoints from recipe viewset to that endpoint
# The endpoints of viewset will auto generated URLs depending on
# functionality provided by the viewset
router.register('recipes', views.RecipeViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
]
