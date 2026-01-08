from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import RegistrationSerializer, CustomTokenObtainPairSerializer


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({'detail':'User created successfully!'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


User = get_user_model()

class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Get tokens from validated data
            refresh = serializer.validated_data.get('refresh')
            access = serializer.validated_data.get('access')
            
            # Get user from token payload or by username
            username = serializer.validated_data.get('username') or request.data.get('username')
            try:
                user_obj = User.objects.get(username=username)
                user_data = {
                    "id": user_obj.pk,
                    "username": user_obj.username,
                    "email": user_obj.email,
                }
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_401_UNAUTHORIZED)
            
            data = {
                'detail': 'Login successfully!',
                'user': user_data
            }
            
            response = Response(data, status=status.HTTP_200_OK)
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite='Lax',
            )

            response.set_cookie(
                key='access_token',
                value=str(access),
                httponly=True,
                secure=True,
                samesite='Lax',
            )
            
            return response
        else:
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class CookieTokenRefreshView(TokenRefreshView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
    
        if refresh_token is None:
            return Response({"error": "Refresh token not provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except:
            return Response({"error": "Refresh token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)
        
        access_token = serializer.validated_data.get("access")

        response = Response({"message": "Token refreshed successfully"}, status=status.HTTP_200_OK)
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=True,
            samesite='Lax',
        )

        return response
    

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        response = Response({"message": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."}, status=status.HTTP_200_OK)
        response.delete_cookie('refresh_token')
        response.delete_cookie('access_token')
        return response