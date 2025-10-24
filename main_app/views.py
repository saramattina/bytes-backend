from decimal import Decimal, InvalidOperation

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import generics, status, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from openai import OpenAI
import json
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions


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
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_queryset(self):
        return Recipe.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RecipeDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_queryset(self):
        return Recipe.objects.filter(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()

        # Remove current image if requested
        if data.get("image") == "":
            if instance.image:
                instance.image.delete(save=False)
            data.pop("image")

        # Replace existing image when a new one is uploaded
        if "image" in request.FILES and instance.image:
            instance.image.delete(save=False)

        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Delete the image file before deleting the recipe
        if instance.image:
            instance.image.delete(save=False)
        
        return super().destroy(request, *args, **kwargs)


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

            message_parts = []
            if added_count > 0:
                message_parts.append(f"Added {added_count} new ingredient(s)")
            if updated_count > 0:
                connector = "updated" if message_parts else "Updated"
                message_parts.append(f"{connector} {updated_count} existing ingredient(s)")

            message_text = " and ".join(message_parts) + " to grocery list" if message_parts else "No changes made to grocery list"

            return Response(
                {"message": message_text},
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
        data = request.data
        name = data.get("name", "").strip()
        quantity = data.get("quantity")
        volume_unit = (data.get("volume_unit") or "").strip()
        weight_unit = (data.get("weight_unit") or "").strip()

        if not name:
            return Response(
                {"name": ["Name is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if quantity in (None, ""):
            return Response(
                {"quantity": ["Quantity is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if volume_unit and weight_unit:
            return Response(
                {
                    "units": [
                        "Provide either a volume unit or a weight unit, not both."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            quantity_value = Decimal(str(quantity))
        except (InvalidOperation, TypeError):
            return Response(
                {"quantity": ["Quantity must be a valid number."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        measurement_type = get_measurement_type(volume_unit, weight_unit)
        if measurement_type == "volume" and volume_unit not in VOLUME_TO_ML:
            return Response(
                {"volume_unit": ["Invalid volume unit."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if measurement_type == "weight" and weight_unit not in WEIGHT_TO_GRAMS:
            return Response(
                {"weight_unit": ["Invalid weight unit."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing_items = GroceryListItem.objects.filter(
            user=request.user, name__iexact=name
        )

        matching_item = None
        if measurement_type == "volume":
            matching_item = next(
                (item for item in existing_items if item.volume_unit),
                None,
            )
        elif measurement_type == "weight":
            matching_item = next(
                (item for item in existing_items if item.weight_unit),
                None,
            )
        else:
            matching_item = next(
                (
                    item
                    for item in existing_items
                    if not item.volume_unit and not item.weight_unit
                ),
                None,
            )

        if matching_item:
            try:
                if measurement_type == "volume":
                    converted = convert_quantity(
                        quantity_value,
                        volume_unit,
                        matching_item.volume_unit,
                        VOLUME_TO_ML,
                    )
                    matching_item.quantity += float(converted)
                elif measurement_type == "weight":
                    converted = convert_quantity(
                        quantity_value,
                        weight_unit,
                        matching_item.weight_unit,
                        WEIGHT_TO_GRAMS,
                    )
                    matching_item.quantity += float(converted)
                else:
                    matching_item.quantity += float(quantity_value)

                matching_item.checked = False
                matching_item.save()
                return Response(
                    {
                        "message": f"Updated grocery list item for {matching_item.name}.",
                        "item": GroceryListItemSerializer(matching_item).data,
                    },
                    status=status.HTTP_200_OK,
                )
            except ValueError:
                return Response(
                    {"units": ["Unable to merge due to incompatible units."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # No matching item found, create a new one
        serializer = GroceryListItemSerializer(
            data={
                "name": name,
                "quantity": float(quantity_value),
                "volume_unit": volume_unit,
                "weight_unit": weight_unit,
            }
        )
        if serializer.is_valid():
            item = serializer.save(user=request.user)
            return Response(
                {
                    "message": f"Added {item.name} to grocery list.",
                    "item": GroceryListItemSerializer(item).data,
                },
                status=status.HTTP_201_CREATED,
            )
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


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def generate_recipe(request):
    """
    Generate a recipe based on the user prompt unis OpenAI.
    Return a JSON structure ready for preview on the frontend.
    """
    user_prompt = request.data.get("prompt", "").strip()
    tags = request.data.get("tags", [])
    if not user_prompt:
        return Response({"error": "Prompt is required"}, status=400)

    tags_text = ", ".join(tags) if tags else "no diatary tags"
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    system_instructions = """
    You are a professional chef and nutrition-focused recipe generator AI.
    Your goal is to generate **delicious, realistic, step-by-step recipes** for a cooking app.
    All responses must be **valid JSON only** — no text outside the JSON block.

    Each recipe must include:
    - title (string)
    - notes (short description, 1–3 sentences about flavor and nutrition, and total cook/prep time)
    - tags (list of lowercase strings, e.g. ["contains_dairy", "spicy"])
    - ingredients (list of objects: {name, quantity, volume_unit, weight_unit})
    - steps (list of objects: {step (int), description (string)})

    Ingredient Rules:
    - Use only these allowed `volume_unit` values: ["tsp", "tbsp", "fl_oz", "cup", "pt", "qt", "gal", "ml", "l"]
    - Use only these allowed `weight_unit` values: ["g", "kg", "oz", "lb"]
    - Each ingredient must include **either/none** volume_unit or weight_unit (never both).
    - If a real-world ingredient doesn't use a measurable unit like "clove" or "slice", convert it into a measurable one (e.g., 1 garlic clove → 1 tsp minced garlic), or if that’s not possible, set both units to null and specify the non-measurable form directly in the ingredient name (e.g., "Garlic Clove", quantity: 1).

    **Cooking & Flavor Style:**
    - Always include realistic cooking details:
        - Mention time ranges, heat levels, and visual/tactile cues (“until golden”, “until thickened”).
        - For meats: specify doneness cues, internal temperature, and flipping instructions.
        - For grains or oats: specify exact cooking times and methods (e.g., “microwave on high for 90 seconds, stir, and rest 30 seconds”).
        - For sauces/dressings: include whisking, blending, or reduction steps as appropriate.
    - Recipes must taste balanced and delicious — combine herbs, spices, and sauces creatively but realistically.

    **Output format:**  
    Return only valid JSON following this structure.
    
    Example JSON (detailed):

    {
    "title": "Creamy Spicy Chicken Rice Bowl",
    "notes": "A flavorful, high-protein rice bowl with tender chicken, sautéed spinach, and a creamy yogurt-sriracha sauce. Cook time: 20 minutes, prep time: 15 minutes",
    "tags": ["contains_dairy", "spicy"],
    "ingredients": [
        {"name": "Chicken Breast", "quantity": 200, "weight_unit": "g", "volume_unit": null},
        {"name": "Olive Oil", "quantity": 1, "weight_unit": null, "volume_unit": "tbsp"},
        {"name": "Garlic Powder", "quantity": 0.5, "weight_unit": null, "volume_unit": "tsp"},
        {"name": "Paprika", "quantity": 0.5, "weight_unit": null, "volume_unit": "tsp"},
        {"name": "Cooked Rice", "quantity": 150, "weight_unit": "g", "volume_unit": null},
        {"name": "Fresh Spinach", "quantity": 80, "weight_unit": "g", "volume_unit": null},
        {"name": "Greek Yogurt", "quantity": 60, "weight_unit": "g", "volume_unit": null},
        {"name": "Sriracha", "quantity": 1, "weight_unit": null, "volume_unit": "tbsp"},
        {"name": "Salt", "quantity": 1, "weight_unit": null, "volume_unit": "tsp"},
        {"name": "Black Pepper", "quantity": 0.5, "weight_unit": null, "volume_unit": "tsp"}
    ],
    "steps": [
        {"step": 1, "description": "Pat the chicken dry and season both sides with salt, pepper, garlic powder, and paprika."},
        {"step": 2, "description": "Heat olive oil in a skillet over medium-high heat. Add the chicken and sear for 5–6 minutes per side until golden and cooked through (internal temp 74°C / 165°F)."},
        {"step": 3, "description": "Remove chicken and rest for 2–3 minutes before slicing thinly."},
        {"step": 4, "description": "In the same pan, add spinach and sauté for 1–2 minutes until wilted."},
        {"step": 5, "description": "In a bowl, mix Greek yogurt and sriracha until creamy and orange in color."},
        {"step": 6, "description": "Assemble the bowl: layer rice, spinach, and sliced chicken. Drizzle the yogurt-sriracha sauce on top and serve warm."}
    ]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instructions},
                {
                    "role": "user",
                    "content": f"Generate a recipe based on this request: '{user_prompt}'."
                    f"The recipe should align with these tags: '{tags_text}",
                },
            ],
            response_format={"type": "json_object"},
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
# Unit conversion helpers for grocery list merging
VOLUME_TO_ML = {
    "tsp": Decimal("4.92892"),
    "tbsp": Decimal("14.7868"),
    "fl_oz": Decimal("29.5735"),
    "cup": Decimal("236.588"),
    "pt": Decimal("473.176"),
    "qt": Decimal("946.353"),
    "gal": Decimal("3785.41"),
    "ml": Decimal("1"),
    "l": Decimal("1000"),
}

WEIGHT_TO_GRAMS = {
    "g": Decimal("1"),
    "kg": Decimal("1000"),
    "oz": Decimal("28.3495"),
    "lb": Decimal("453.592"),
}


def convert_quantity(value, from_unit, to_unit, conversion_map):
    """Convert between units of the same measurement type."""
    if from_unit not in conversion_map or to_unit not in conversion_map:
        raise ValueError("Unsupported unit conversion.")

    value_decimal = Decimal(value)
    base_value = value_decimal * conversion_map[from_unit]
    return base_value / conversion_map[to_unit]


def get_measurement_type(volume_unit, weight_unit):
    if volume_unit:
        return "volume"
    if weight_unit:
        return "weight"
    return "count"
