"""
Views for the recipe APIs
"""
# We're adding feature to achieve searching by tags & ingredients
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient
from recipe import serializers


# These are for update the documentation.
# extend_schema_view allows us to extend
# auto-generated documents created by Django rest spectacular.
@extend_schema_view(
    # We wanna extend schema in list endpoint,
    # which is where we add filters to.
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                # The name of parameter we're going to pass in.
                'tags',
                # Specify the type is a string.
                OpenApiTypes.STR,
                # This is for user who's using the API to read.
                description='Comma seperated list of tag IDs to filter',
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma seperated list of ingredient IDs to filter',
            )
        ]
    )
)
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

    def _params_to_ints(self, qs):
        """Convert a list of strings to integers."""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        # '-id' is used for order from high id to low id
        tags = self.request.query_params.get('tags')
        ins = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            # This double underscore(__) usage is documented by Django.
            queryset = queryset.filter(tags__id__in=tag_ids)

        if ins:
            ins_ids = self._params_to_ints(ins)
            queryset = queryset.filter(ingredients__id__in=ins_ids)

        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

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


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter by items assigned to recipes.'
            )
        ]
    )
)
# GenericViewSet have to be put behind of Mixin
# cause it can override behaviors
# Django do the favor of update, after just put in mixins.UpdataModelMixin,
# the update operation is done.
class BaseRecipeAttrViewSet(mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):
    """Base view for recipe attributes"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve attr for authenticated user."""
        # bool(1 or 0) -> True or False
        assigned_only = bool(
            # If we don't provide assigned_only, we get default 0.
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            # This means there is a recipe associated with the attr.
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database."""
    # Avoid typo here!
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
