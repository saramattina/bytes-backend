from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Recipe, Ingredient, Step
from .serializers import UserSerializer, RecipeSerializer, IngredientSerializer, StepSerializer

class Home(APIView):
    def get(self, request):
        return Response({"message": "Welcome to the Recipe Collector API!"})
    
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
                "user": UserSerializer(user).data
            })
        else:
            return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    
class SignUpView(generics.CreateAPIView):
    queryset= User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(username=response.data['username'])
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': response.data
        })

class VerifyUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        refresh = RefreshToken.for_user(request.user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(request.user).data
        })

    
class RecipeList(generics.ListCreateAPIView):
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Recipe.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
class RecipeDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        return Recipe.objects.filter(user=user)
    
class IngredientList(generics.ListCreateAPIView):
    serializer_class = IngredientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Ingredient.objects.filter(recipe__user=user)

    def perform_create(self, serializer):
        recipe_id = self.request.data.get('recipe')
        recipe = Recipe.objects.get(id=recipe_id, user=self.request.user)
        serializer.save(recipe=recipe)
        
class IngredientDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = IngredientSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        return Ingredient.objects.filter(user=user)

class StepList(generics.ListCreateAPIView):
    serializer_class = StepSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Step.objects.filter(recipe__user=user)

    def perform_create(self, serializer):
        recipe_id = self.request.data.get('recipe')
        recipe = Recipe.objects.get(id=recipe_id, user=self.request.user)
        serializer.save(recipe=recipe)

        
class StepDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StepSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        return Step.objects.filter(user=user)