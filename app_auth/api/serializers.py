from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    """User registration with password confirmation."""
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirmed_password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
        }

    def validate_confirmed_password(self, value):
        password = self.initial_data.get('password')
        if password and value and password != value:
            raise serializers.ValidationError("Passwords do not match.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value

    def save(self):
        account = User(
            username=self.validated_data['username'],
            email=self.validated_data['email']
        )
        account.set_password(self.validated_data['password'])
        account.save()
        return account


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT token serializer with custom error handling."""
    
    def validate(self, attrs):
        try:
            data = super().validate(attrs)
            data['user'] = self.get_user_data()
            data['detail'] = 'Login successfully!'
            return data
        except Exception:
            raise serializers.ValidationError("Incorrect username or password.")
        
    def get_user_data(self):
        """Get formatted user data for the response."""
        return {
            "id": self.user.pk,
            "username": self.user.username,
            "email": self.user.email,
        }