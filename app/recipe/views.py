"""
Views for the recipe APIs
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe import serializers


# viewsets generate many endpoint,
# use viewset when you create API with CRUD actions
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.RecipeDetailSerializer
    # Represent the objects that available for this viewset
    # Viewset expects to work with a model, and
    # this is the way we tell it.
    queryset = Recipe.objects.all()
    # Specify method we use for auth.
    authentication_classes = [TokenAuthentication]
    # Check user have to be authenticated.
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        # '-id' is used for order from high id to low id
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request."""
        # Specify list action
        if self.action == 'list':
            return serializers.RecipeSerializer

        return self.serializer_class
