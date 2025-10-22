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
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": UserSerializer(user).data,
                }
            )
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
        user = User.objects.get(username=serializer.data["username"])
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


# VERIFY USER
class VerifyUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Verify the currently authenticated user and return their info.
        Called by frontend on page reload to confirm session validity.
        """
        return Response(
            {"user": UserSerializer(request.user).data}, status=status.HTTP_200_OK
        )


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
        return GroceryListItem.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )


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
                    weight_unit=ingredient.weight_unit,
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
                        weight_unit=ingredient.weight_unit,
                    )
                    added_count += 1

            message = []
            if added_count > 0:
                message.append(f"Added {added_count} new ingredient(s)")
            if updated_count > 0:
                message.append(f"Updated {updated_count} existing ingredient(s)")

            return Response(
                {"message": " and ".join(message) + " to grocery list"},
                status=status.HTTP_201_CREATED,
            )
        except Recipe.DoesNotExist:
            return Response(
                {"error": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND
            )


class UpdateGroceryListItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, item_id):
        try:
            item = GroceryListItem.objects.get(id=item_id, user=request.user)

            # Update all provided fields
            item.checked = request.data.get("checked", item.checked)

            # Allow updating quantity and units
            if "quantity" in request.data:
                item.quantity = request.data.get("quantity")
            if "volume_unit" in request.data:
                item.volume_unit = request.data.get("volume_unit")
            if "weight_unit" in request.data:
                item.weight_unit = request.data.get("weight_unit")

            item.save()
            return Response(GroceryListItemSerializer(item).data)
        except GroceryListItem.DoesNotExist:
            return Response(
                {"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND
            )


class AddGroceryListItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = GroceryListItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClearCheckedItemsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        deleted_count = GroceryListItem.objects.filter(
            user=request.user, checked=True
        ).delete()[0]

        return Response(
            {"message": f"Removed {deleted_count} items from grocery list"},
            status=status.HTTP_200_OK,
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


# USER PROFILE VIEWS
class UpdateUsernameView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        user = request.user
        new_username = request.data.get("username", "").strip()

        if not new_username:
            return Response(
                {"username": ["Username is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(new_username) < 3:
            return Response(
                {"username": ["Username must be at least 3 characters."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if username already exists (excluding current user)
        if User.objects.filter(username=new_username).exclude(id=user.id).exists():
            return Response(
                {"username": ["A user with that username already exists."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.username = new_username
        user.save()

        return Response(
            {
                "message": "Username updated successfully",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class UpdatePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        errors = {}

        # Validate current password
        if not current_password:
            errors["current_password"] = ["Current password is required."]
        elif not user.check_password(current_password):
            errors["current_password"] = ["Current password is incorrect."]

        # Validate new password
        if not new_password:
            errors["new_password"] = ["New password is required."]
        elif len(new_password) < 6:
            errors["new_password"] = ["Password must be at least 6 characters."]

        # Validate confirm password
        if not confirm_password:
            errors["confirm_password"] = ["Please confirm your new password."]
        elif new_password != confirm_password:
            errors["confirm_password"] = ["Passwords do not match."]

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        # Update password
        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password updated successfully"}, status=status.HTTP_200_OK
        )


class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        password = request.data.get("password")

        if not password:
            return Response(
                {"password": ["Password is required to delete account."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not request.user.check_password(password):
            return Response(
                {"password": ["Incorrect password."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Delete user (cascade will delete all associated recipes, ingredients, steps, grocery items)
        request.user.delete()

        return Response(
            {"message": "Account deleted successfully"}, status=status.HTTP_200_OK
        )


from openai import OpenAI
import json
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def generate_recipe(request):
    """
    Generate a recipe based on the user prompt unis OpenAI.
    Return a JSON structure ready for preview on the frontend.
    """
    user_prompt = request.data.get("prompt", "").strip()
    if not user_prompt:
        return Response({"error": "Prompt is required"}, status=400)

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    system_instructions = """
    you are a recipe generator AI.
    Generate A recipe in JSON format only.
    it must include:
    - title (string)
    - notes (string, short description)
    - ingredients (list of objects: name, quantity, and either volume_unit or weight_unit)
    - steps (list of objects: step and description)
    Example JSON:
    {
        "title": "Banana Protein Pancakes",
        "notes": "Healthy and high-protein breakfest option.",
        "ingredients": [
            {"name": "Banana", "quantity": 1, "weight_unit": null, "volume_unit": null},
            {"name": "Egg", "quantity": 1, "weight_unit": null, "volume_unit": null},
            {"name": "Oats", "quantity": 50, "weight_unit": "g", "volume_unit": null},
        ],
        "steps": [
            {"step": 1, "description": "Mash the banana."}
            {"step": 2, "description": "Mix in egg and oats."}
            {"step": 3, "description": "Cook on pan until golden."}
        ]

    }      
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
        )

        ai_output = response.choices[0].message.content.strip()
        try:
            ai_output = ai_output.replace("```json", "").replace("```", "")
            recipe_json = json.loads(ai_output)
        except json.JSONDecodeError:
            return Response(
                {"error": "Failed to parse AI response as JSON", "raw": ai_output},
                status=500,
            )

        return Response(recipe_json, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
