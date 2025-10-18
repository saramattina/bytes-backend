from django.contrib import admin
from django.urls import path
from .views import Home, LoginView, SignUp, VerifyUserView, RecipeList, RecipeDetail, IngredientList, IngredientDetail, StepList, StepDetail

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", Home.as_view(), name="home"),
    path("users/login/", LoginView.as_view(), name="login"),
    path("users/sign-up/", SignUp.as_view(), name="sign-up"),
    path('users/token/refresh/', VerifyUserView.as_view(), name='token_refresh'),
    path("recipes/", RecipeList.as_view(), name="recipe-list"),
    path("recipes/<int:id>", RecipeDetail.as_view(), name="recipe-detail"),
    path("recipes/<int:recipe_id>/ingredients/", IngredientList.as_view(), name="ingredient-list"),
    path("recipes/<int:recipe_id>/ingredients/<int:id>", IngredientDetail.as_view(), name="ingredient-detail"),
    path("recipes/<int:recipe_id>/steps/", StepList.as_view(), name="step-list"),
    path("recipes/<int:recipe_id>/step/<int:id>", StepDetail.as_view(), name="step-detail")
]