from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Recipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    notes = models.TextField(max_length=250)
    favorite = models.BooleanField(default=False)
    image = models.ImageField(upload_to="recipes/", blank=True, null=True)

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    quantity = models.FloatField()

    class VolumeUnits(models.TextChoices):
        CUP = "cup", "Cup"
        TBSP = "tbsp", "Tablespoon"
        TSP = "tsp", "Teaspoon"

    class WeightUnits(models.TextChoices):
        G = "g", "Gram"
        OZ = "oz", "Ounce"

    volume_unit = models.CharField(
        max_length=10, choices=VolumeUnits.choices, blank=True, null=True
    )
    weight_unit = models.CharField(
        max_length=10, choices=WeightUnits.choices, blank=True, null=True
    )

    def __str__(self):
        return self.name


class Step(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    step = models.IntegerField()
    description = models.TextField(max_length=250)

    def __str__(self):
        return self.step
