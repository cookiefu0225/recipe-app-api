# Generated by Django 3.2.15 on 2022-09-04 21:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_recipe_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tag',
            old_name='context',
            new_name='name',
        ),
    ]