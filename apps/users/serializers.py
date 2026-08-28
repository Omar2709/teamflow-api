from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
        )
        read_only_fields = ("id",)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    password_confirmation = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "password_confirmation",
        )

        read_only_fields = ("id",)

    def validate(self, attrs):
        password = attrs.get("password")
        password_confirmation = attrs.pop(
            "password_confirmation",
            None,
        )

        if password != password_confirmation:
            raise serializers.ValidationError({
                "password_confirmation": (
                    "Las contraseñas no coinciden."
                )
            })

        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class CurrentUserResponseSerializer(serializers.Serializer):
    message = serializers.CharField(read_only=True)
    data = UserSerializer(read_only=True)

class LogoutRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        write_only=True,
    )


class LogoutResponseSerializer(serializers.Serializer):
    message = serializers.CharField(
        read_only=True,
    )