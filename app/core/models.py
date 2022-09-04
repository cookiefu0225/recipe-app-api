"""
Database models.
"""
import uuid
# Import os is for the path manipulation functions
import os

# After creating a new model, be sure to apply migrations before test.
# After testing, we need to register the model in django admin.
# For this app, go to core/admin.py
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image."""
    # ext = extention, like .jpg, .png
    ext = os.path.splitext(filename)[1]
    # Generate unique uid for a image
    filename = f'{uuid.uuid4()}{ext}'

    # The string is created with the proper format for
    # the os we run. Ex: \upload\recipe\<filename> in Windows
    return os.path.join('uploads', 'recipe', filename)


class UserManager(BaseUserManager):
    """User Manager"""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return user"""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    # We use this for authentication, this is how
    # wo replace username
    USERNAME_FIELD = 'email'


class Recipe(models.Model):
    """Recipe object."""
    # Set user of the recipe.
    user = models.ForeignKey(
        # We defined it in settings, it can be typed directly.
        # However, it's better to access by AUTH_USER_MODEL.
        settings.AUTH_USER_MODEL,
        # If the user is removed, the recipes would be removed as well.
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    # Any of our tags can be associated with our recipes,
    # any of our recipes can be associated with our tags.
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField('Ingredient')
    # We are not calling recipe_image_file_path, do not add ().
    # We are just pass a reference to the function.
    # This path generate method is documented in Django docs.
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self) -> str:
        return self.title


class Tag(models.Model):
    """Tag object."""
    # Set user of the tag.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    """Ingredient for recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name
