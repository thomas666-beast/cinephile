from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Public self-registration. Role is forced to VIEWER."""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "password", "password_confirm", "first_name", "last_name")

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        # Role is NOT taken from client input; enforced server-side.
        user = User.objects.create_user(
            password=password,
            role=User.Role.VIEWER,
            **validated_data,
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Read/update the current user. Role and is_staff are read-only here."""

    class Meta:
        model = User
        fields = (
            "id", "email", "first_name", "last_name",
            "role", "is_staff", "date_joined", "last_login",
        )
        read_only_fields = (
            "id", "email", "role", "is_staff", "date_joined", "last_login",
        )
