from django.utils import timezone
from rest_framework import serializers
from .models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"token": str(refresh.access_token), "refreshToken": str(refresh)}

class UserSerializer(serializers.ModelSerializer):
    is_premium = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'role', 'avatar', 'phone', 'subscription_plan', 'subscription_period',
            'subscription_start', 'subscription_end', 'is_premium',
            'is_verified', 'created_at',
        ]
        read_only_fields = ['id', 'email', 'created_at', 'is_verified']


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'avatar']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid email or password.")

            if not user.check_password(password):
                raise serializers.ValidationError("Invalid email or password.")
        else:
            raise serializers.ValidationError("Both email and password are required.")

        # A subscription_plan can go stale once subscription_end passes (nothing
        # else updates it), so downgrade it here rather than trusting the stored
        # value for dashboard routing.
        if (user.subscription_plan != 'free' and user.subscription_end
            and user.subscription_end < timezone.now()):
            user.subscription_plan = 'free'
            user.subscription_period = None
            user.save(update_fields=['subscription_plan', 'subscription_period'])

        data['user'] = user
        data['is_premium'] = user.is_premium
        return data

