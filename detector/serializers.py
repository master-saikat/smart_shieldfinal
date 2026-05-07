from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ScanHistory


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanHistory
        # Explicit fields only — never expose internal user FK or all fields
        fields = ['id', 'scan_type', 'input_data', 'risk_score', 'label', 'explanation', 'created_at']