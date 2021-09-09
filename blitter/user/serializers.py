from django.db import models
from django.db.models import fields
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = '__all__'

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField()
        self.fields['password'] = serializers.CharField(required=False)

    def validate(self, attrs):
        data = self.context['request'].data
        required_keys = ['phone', 'firebase_id']

        for key in required_keys:
            if key not in data:
                raise ValidationError(f'Provide {key}')

        queryset = get_user_model().objects.filter(phone=data['phone'])
        if not queryset:
            user = get_user_model().objects.create_user(**data)
        else:
            validated_user = queryset.filter(
                firebase_id=data['firebase_id'])
            if not validated_user:
                raise ValidationError('Invalid Firebase Id')
            user = queryset.first()

        token = self.get_token(user)

        return {
            'user': UserSerializer().to_representation(user),
            'access_token': str(token.access_token),
            'refresh_token': str(token)
        }
