from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.views import APIView

from .serializers import RegistrationSerializer, CustomTokenObtainPairSerializer


@extend_schema(
    tags=['Authentication'],
    description="Register a new user.",
    responses={
        201: {'detail': 'User created successfully!'},
        400: OpenApiResponse(description="Bad Request - Missing fields or invalid credentials"),
    }
)
class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'User created successfully!'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Authentication'],
    description="Obtain JWT tokens and set them in HttpOnly cookies.",
    responses={
        200: {'detail': 'Login successfully!'},
        401: OpenApiResponse(description="Unauthorized - Invalid credentials"),
    }
)
class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            refresh = validated_data['refresh']
            access = validated_data['access']

            user = serializer.user

            user_data = {
                "id": user.pk,
                "username": user.username,
                "email": user.email,
            }

            data = {
                'detail': 'Login successfully!',
                'user': user_data
            }

            response = Response(data, status=status.HTTP_200_OK)
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=False,  # False for development
                samesite='Lax',
            )

            response.set_cookie(
                key='access_token',
                value=str(access),
                httponly=True,
                secure=False,  # False for development
                samesite='Lax',
            )

            return response
        else:
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


@extend_schema(
    tags=['Authentication'],
    description="Refresh JWT access token using the refresh token stored in HttpOnly cookie.",
    responses={
        200: {'detail': 'Token refreshed'},
        401: OpenApiResponse(description="Unauthorized - Refresh token not provided or invalid"),
    }
)
class CookieTokenRefreshView(TokenRefreshView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = {}
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response({"error": "Refresh token not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except:
            return Response({"error": "Refresh token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)

        access_token = serializer.validated_data.get("access")
        data = {
            "detail": "Token refreshed",
            "access": access_token
        }

        response = Response(data, status=status.HTTP_200_OK)
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=True,
            samesite='Lax',
        )

        return response


@extend_schema(
    tags=['Authentication'],
    description="Log out the user by deleting JWT tokens from HttpOnly cookies.",
    responses={
        200: {'detail': 'Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid.'},
        401: OpenApiResponse(description="Unauthorized - User is not logged in"),
    }
)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        access_token = request.COOKIES.get("access_token")

        if not refresh_token and not access_token:
            return Response(
                {"error": "User is not logged in. No tokens found."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        response = Response(
            {"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."},
            status=status.HTTP_200_OK
        )
        response.delete_cookie('refresh_token')
        response.delete_cookie('access_token')
        return response
