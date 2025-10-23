import json

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Recipe, Ingredient, Step, GroceryListItem


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password2']
        read_only_fields = ["id"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class GroceryListItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroceryListItem
        fields = ["id", "user", "name", "quantity", "volume_unit", "weight_unit", "checked", "created_at"]
        read_only_fields = ["id", "user", "created_at"]


class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = "__all__"


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)
    steps = StepSerializer(many=True, read_only=True)
    user = serializers.ReadOnlyField(source="user.username")
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "user",
            "title",
            "notes",
            "favorite",
            "image",
            "tags",
            "ingredients",
            "steps",
        ]
        extra_kwargs = {
            "notes": {"allow_blank": True, "required": False},
            "image": {"required": False, "allow_null": True},
            "tags": {"required": False},
        }

    def validate_tags(self, value):
        """
        Accept JSON strings from multipart form submissions and convert to lists.
        """
        if isinstance(value, str):
            if not value:
                return []
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError as exc:
                raise serializers.ValidationError("Invalid JSON for tags.") from exc
            if not isinstance(parsed, list):
                raise serializers.ValidationError("Tags must be provided as a list.")
            return parsed
        return value

    def validate_favorite(self, value):
        """
        Convert common string representations to booleans when using FormData.
        """
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "1", "yes", "on"}:
                return True
            if lowered in {"false", "0", "no", "off", ""}:
                return False
        return bool(value)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.image:
            storage = getattr(instance.image, "storage", None)
            if storage:
                data["image"] = storage.url(instance.image.name)
            else:
                data["image"] = instance.image.url
        else:
            data["image"] = None
        return data
