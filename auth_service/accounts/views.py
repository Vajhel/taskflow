from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate

from .models import User
from .serializers import UserRegistrationSerializer, UserSerializer, LoginSerializer
from .authentication import generate_token


class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя."""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = generate_token(user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token,
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Аутентификация пользователя и выдача JWT-токена."""
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = authenticate(
        username=serializer.validated_data['username'],
        password=serializer.validated_data['password'],
    )
    if user is None:
        return Response(
            {'error': 'Неверные учётные данные.'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    token = generate_token(user)
    return Response({
        'user': UserSerializer(user).data,
        'token': token,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """Получение профиля текущего пользователя."""
    return Response(UserSerializer(request.user).data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile_update_view(request):
    """Обновление профиля текущего пользователя."""
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_token_view(request):
    """Валидация JWT-токена (используется другими микросервисами)."""
    return Response({
        'valid': True,
        'user': UserSerializer(request.user).data,
    })


class UserListView(generics.ListAPIView):
    """Список всех пользователей."""
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
