from django.contrib import admin
from django.urls import path
from .views import Home, LoginView, SignUp, VerifyUserView, RecipeList, RecipeDetail

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", Home.as_view(), name="home"),
    path("users/login/", LoginView.as_view(), name="login"),
    path("users/sign-up/", SignUp.as_view(), name="sign-up"),
    path('users/token/refresh/', VerifyUserView.as_view(), name='token_refresh'),
    path("recipes/", RecipeList.as_view(), name="recipe-list"),
    path("reciples/<int:id>", RecipeDetail.as_view(), name="recipe-detail"),
]