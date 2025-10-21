from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    Home, SignInView, SignUpView, VerifyUserView,
    RecipeList, RecipeDetail, IngredientList, IngredientDetail, StepList, StepDetail
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", Home.as_view(), name="home"),

    # Auth
    path("users/sign-in/", SignInView.as_view(), name="sign-in"),
    path("users/sign-up/", SignUpView.as_view(), name="sign-up"),
    path("users/verify/", VerifyUserView.as_view(), name="verify-user"),
    path('users/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Recipes
    path("recipes/", RecipeList.as_view(), name="recipe-list"),
    path("recipes/<int:id>/", RecipeDetail.as_view(), name="recipe-detail"),
    path("recipes/<int:recipe_id>/ingredients/", IngredientList.as_view(), name="ingredient-list"),
    path("recipes/<int:recipe_id>/ingredients/<int:id>/", IngredientDetail.as_view(), name="ingredient-detail"),
    path("recipes/<int:recipe_id>/steps/", StepList.as_view(), name="step-list"),
    path("recipes/<int:recipe_id>/steps/<int:id>/", StepDetail.as_view(), name="step-detail")
]
