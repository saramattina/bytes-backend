from django.db import models
from django.contrib.auth.models import User
import uuid
import os


def recipe_image_path(instance, filename):
    """
    Generate a unique path for recipe images: recipes/user_{id}/{uuid}.{ext}
    Prevents filename conflicts and organizes images by user
    """
    ext = filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('recipes', f'user_{instance.user.id}', unique_filename)


class Recipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    notes = models.TextField(max_length=400, blank=True)
    favorite = models.BooleanField(default=False)
    image = models.ImageField(upload_to=recipe_image_path, blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="ingredients"
    )
    name = models.CharField(max_length=100)
    quantity = models.FloatField()

    class VolumeUnits(models.TextChoices):
        TSP = "tsp", "Teaspoon"
        TBSP = "tbsp", "Tablespoon"
        FL_OZ = "fl_oz", "Fluid Ounce"
        CUP = "cup", "Cup"
        PT = "pt", "Pint"
        QT = "qt", "Quart"
        GAL = "gal", "Gallon"
        ML = "ml", "Milliliter"
        L = "l", "Liter"

    class WeightUnits(models.TextChoices):
        G = "g", "Gram"
        KG = "kg", "Kilogram"
        OZ = "oz", "Ounce"
        LB = "lb", "Pound"

    volume_unit = models.CharField(
        max_length=10, choices=VolumeUnits.choices, blank=True, null=True
    )
    weight_unit = models.CharField(
        max_length=10, choices=WeightUnits.choices, blank=True, null=True
    )

    def __str__(self):
        return self.name


class GroceryListItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    quantity = models.FloatField()
    volume_unit = models.CharField(max_length=10, blank=True, null=True)
    weight_unit = models.CharField(max_length=10, blank=True, null=True)
    checked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class Step(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="steps")
    step = models.IntegerField()
    description = models.TextField(max_length=250)

    def __str__(self):
        return f"Step {self.step}: {self.description[:30]}"
