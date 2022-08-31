"""
Serializers for recipe APIs.
"""
from rest_framework import serializers

from core.models import Recipe, Tag, Ingredient


# We have to move TagSerializer here because we're going to
# add nested serializer into RecipeSerializer
class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'context']
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredients."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    # many=True because tags would be a list of tags
    # By default, nested serializer is read only,
    # which means we cannot create items with those values.
    # We add custom logic to enable writing and editing by
    # adding methods.
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'time_minutes', 'price', 'link', 'tags',
            'ingredients',
        ]
        read_only_field = ['id']

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""
        # The context is passed to the serializer by the view
        # when you're using the serializer for that particular view.
        auth_user = self.context['request'].user
        for tag in tags:
            # get_or_create is a helper method that's available for
            # the model manager.
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                # We can user context=tag['context'].
                # However, using **tag enables our codes to
                # add new attrs in tag and make them passed in as well.
                **tag
            )
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handle getting or creating ingredients as needed."""
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            ing_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient
            )
            recipe.ingredients.add(ing_obj)

    # Override original create method
    def create(self, validated_data):
        """Create a recipe."""
        # If tags exists in validated_data,
        # remove it and assign to tags variable.
        # Otherwise, return an empty list.
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        # Use everything except tags to create recipe.
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_ingredients(ingredients, recipe)
        self._get_or_create_tags(tags, recipe)

        return recipe

    def update(self, instance, validated_data):
        """Update recipe."""
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


# This would be an extension of RecipeSerializer,
# so we want things in basic serializer and then add extra fields
class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
