from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", 'password', 'is_active']

    def create(self, validated_data):
        validated_data["is_active"] = True
        user = User.objects.create_user(**validated_data)
        return user


