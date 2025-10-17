from rest_framework import serializers
from django.contrib.auth.models import User
from models import Recipe, Step


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )

        return user


class StepSerializer(serializers.ModelSerializer):

    class Meta:
        model = Step
        fields = "__all__"


class RecipeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    step = StepSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = "__all__"
