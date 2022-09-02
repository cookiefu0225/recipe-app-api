"""
Views for the recipe APIs
"""
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient
from recipe import serializers


# viewsets generate many endpoint,
# use viewset when you create API with CRUD actions
class RecipeViewSet(viewsets.ModelViewSet):
    # The following texts in dots will generate in api description.
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
        # We are building a custom action.
        # ModelViewSet provides default actions such as list, delete, update.
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    # The function name matters!
    # Cannot use other function name.
    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)

    # We add a custom action, action decorator is provided by Django.
    # detail=True means this action will only apply to detail endpoints.
    # url_path specify a custom URL path for our action.
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseRecipeAttrViewSet(mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):
    """Base view for recipe attributes"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


# GenericViewSet have to be put behind of Mixin
# cause it can override behaviors
# Django do the favor of update, after just put in mixins.UpdataModelMixin,
# the update operation is done.
class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database."""
    # Avoid typo here!
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()

    def get_queryset(self):
        """Retrieve tags for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-context')    # noqa: E501


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()

    def get_queryset(self):
        """Retrieve ingredients for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')
