from django.contrib import admin
from .models import Recipe, Ingredient, Step, GroceryListItem

# Register your models here.
admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(GroceryListItem)
admin.site.register(Step)