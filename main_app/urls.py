from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    Home,
    SignInView,
    SignUpView,
    VerifyUserView,
    RecipeList,
    RecipeDetail,
    IngredientList,
    IngredientDetail,
    StepList,
    StepDetail,
    GroceryListView,
    AddRecipeToGroceryListView,
    UpdateGroceryListItemView,
    ClearCheckedItemsView,
    AddGroceryListItemView,  # Add this import
    UpdateUsernameView,
    UpdatePasswordView,
    DeleteAccountView,
    generate_recipe,
)

urlpatterns = [
    path("", Home.as_view(), name="home"),
    # Auth
    path("users/sign-in/", SignInView.as_view(), name="sign-in"),
    path("users/sign-up/", SignUpView.as_view(), name="sign-up"),
    path("users/verify/", VerifyUserView.as_view(), name="verify-user"),
    path("users/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Recipes
    path("recipes/", RecipeList.as_view(), name="recipe-list"),
    path("recipes/<int:id>/", RecipeDetail.as_view(), name="recipe-detail"),
    path(
        "recipes/<int:recipe_id>/ingredients/",
        IngredientList.as_view(),
        name="ingredient-list",
    ),
    path(
        "recipes/<int:recipe_id>/ingredients/<int:id>/",
        IngredientDetail.as_view(),
        name="ingredient-detail",
    ),
    path("recipes/<int:recipe_id>/steps/", StepList.as_view(), name="step-list"),
    path(
        "recipes/<int:recipe_id>/steps/<int:id>/",
        StepDetail.as_view(),
        name="step-detail",
    ),
    # Grocery List
    path("grocery-list/", GroceryListView.as_view(), name="grocery-list"),
    path(
        "grocery-list/add-item/",
        AddGroceryListItemView.as_view(),
        name="add-grocery-item",
    ),
    path(
        "grocery-list/add-recipe/<int:recipe_id>/",
        AddRecipeToGroceryListView.as_view(),
        name="add-recipe-to-grocery",
    ),
    path(
        "grocery-list/item/<int:item_id>/",
        UpdateGroceryListItemView.as_view(),
        name="update-grocery-item",
    ),
    path(
        "grocery-list/clear-checked/",
        ClearCheckedItemsView.as_view(),
        name="clear-checked-items",
    ),
    # User Profile
    path(
        "users/update-username/", UpdateUsernameView.as_view(), name="update-username"
    ),
    path(
        "users/update-password/", UpdatePasswordView.as_view(), name="update-password"
    ),
    path("users/delete-account/", DeleteAccountView.as_view(), name="delete-account"),
    # Ai
    path("recipes/generate/", generate_recipe, name="generate-recipe"),
]
