from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import generics, status, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Recipe, Ingredient, Step, GroceryListItem
from .serializers import (
    UserSerializer,
    RecipeSerializer,
    IngredientSerializer,
    StepSerializer,
    GroceryListItemSerializer,
)

# GENERAL / AUTH VIEWS

class Home(APIView):
    def get(self, request):
        return Response({"message": "Welcome to the Recipe Collector API!"})


# SIGN IN
class SignInView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user).data,
            })
        return Response(
            {"error": "Invalid Credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


# SIGN UP
class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        # Validate the data and return errors if invalid
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # If valid, create the user
        self.perform_create(serializer)
        user = User.objects.get(username=serializer.data['username'])
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': serializer.data
        }, status=status.HTTP_201_CREATED)


# VERIFY USER
class VerifyUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Verify the currently authenticated user and return their info.
        Called by frontend on page reload to confirm session validity.
        """
        return Response({
            "user": UserSerializer(request.user).data
        }, status=status.HTTP_200_OK)


# RECIPE VIEWS
class RecipeList(generics.ListCreateAPIView):
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Recipe.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RecipeDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Recipe.objects.filter(user=self.request.user)


# INGREDIENT VIEWS
class IngredientList(generics.ListCreateAPIView):
    serializer_class = IngredientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        recipe_id = self.kwargs.get("recipe_id")
        return Ingredient.objects.filter(
            recipe__user=self.request.user,
            recipe_id=recipe_id,
        )

    def perform_create(self, serializer):
        recipe_id = self.kwargs.get("recipe_id")
        recipe = Recipe.objects.get(id=recipe_id, user=self.request.user)
        serializer.save(recipe=recipe)


class IngredientDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = IngredientSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        recipe_id = self.kwargs.get("recipe_id")
        return Ingredient.objects.filter(
            recipe__user=self.request.user,
            recipe_id=recipe_id,
        )

# GROCERY LIST VIEWS
class GroceryListView(generics.ListAPIView):
    serializer_class = GroceryListItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GroceryListItem.objects.filter(user=self.request.user).order_by('-created_at')


class AddRecipeToGroceryListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, recipe_id):
        try:
            recipe = Recipe.objects.get(id=recipe_id, user=request.user)
            ingredients = recipe.ingredients.all()
            
            added_count = 0
            updated_count = 0
            
            # Add each ingredient to grocery list
            for ingredient in ingredients:
                # Check if item with same name and units already exists
                existing_item = GroceryListItem.objects.filter(
                    user=request.user,
                    name__iexact=ingredient.name,  # Case-insensitive name match
                    volume_unit=ingredient.volume_unit,
                    weight_unit=ingredient.weight_unit
                ).first()
                
                if existing_item:
                    # If exists with matching units, add quantities together
                    existing_item.quantity += ingredient.quantity
                    existing_item.checked = False  # Uncheck when adding more
                    existing_item.save()
                    updated_count += 1
                else:
                    # Create new item if no match found
                    GroceryListItem.objects.create(
                        user=request.user,
                        name=ingredient.name,
                        quantity=ingredient.quantity,
                        volume_unit=ingredient.volume_unit,
                        weight_unit=ingredient.weight_unit
                    )
                    added_count += 1
            
            message = []
            if added_count > 0:
                message.append(f"Added {added_count} new ingredient(s)")
            if updated_count > 0:
                message.append(f"Updated {updated_count} existing ingredient(s)")
            
            return Response(
                {"message": " and ".join(message) + " to grocery list"},
                status=status.HTTP_201_CREATED
            )
        except Recipe.DoesNotExist:
            return Response(
                {"error": "Recipe not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class UpdateGroceryListItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, item_id):
        try:
            item = GroceryListItem.objects.get(id=item_id, user=request.user)
            item.checked = request.data.get('checked', item.checked)
            item.save()
            return Response(GroceryListItemSerializer(item).data)
        except GroceryListItem.DoesNotExist:
            return Response(
                {"error": "Item not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class ClearCheckedItemsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        deleted_count = GroceryListItem.objects.filter(
            user=request.user,
            checked=True
        ).delete()[0]
        
        return Response(
            {"message": f"Removed {deleted_count} items from grocery list"},
            status=status.HTTP_200_OK
        )

# STEP VIEWS
class StepList(generics.ListCreateAPIView):
    serializer_class = StepSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        recipe_id = self.kwargs.get("recipe_id")
        return Step.objects.filter(
            recipe__user=self.request.user,
            recipe_id=recipe_id,
        )

    def perform_create(self, serializer):
        recipe_id = self.kwargs.get("recipe_id")
        recipe = Recipe.objects.get(id=recipe_id, user=self.request.user)
        serializer.save(recipe=recipe)


class StepDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StepSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        recipe_id = self.kwargs.get("recipe_id")
        return Step.objects.filter(
            recipe__user=self.request.user,
            recipe_id=recipe_id,
        )
