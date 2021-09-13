from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'firebase_id', 'name', 'phone',
                  'email', 'avatar', 'bio', 'date_joined']
        extra_kwargs = {
            'firebase_id': {'write_only': True}
        }


class CustomTokenObtainPairSerializer(serializers.Serializer):
    firebase_id = serializers.CharField()
    name = serializers.CharField(required=False)
    phone = serializers.CharField()
    email = serializers.EmailField(
        allow_blank=True, allow_null=True, required=False)
    avatar = serializers.FileField(required=False, allow_empty_file=True)
    bio = serializers.CharField(allow_blank=True, required=False)

    def validate(self, attrs):
        user, created = UserModel.objects.get_or_create(**attrs)
        token = TokenObtainPairSerializer.get_token(user)

        return {
            'user': UserSerializer(user).data,
            'access_token': str(token.access_token),
            'refresh_token': str(token)
        }
