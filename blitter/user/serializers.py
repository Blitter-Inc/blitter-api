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
        user, created = UserModel.objects.get_or_create(phone=attrs['phone'], defaults={
            'firebase_id': attrs.get('firebase_id'),
            'name': attrs.get('name', ''),
            'email': attrs.get('email'),
            'avatar': attrs.get('avatar'),
            'bio': attrs.get('bio', ''),
        })
        token = TokenObtainPairSerializer.get_token(user)

        return {
            'user': UserSerializer(user, context={'request': self.context['request']}).data,
            'access_token': str(token.access_token),
            'refresh_token': str(token),
            'is_new_user': True if created else False
        }


class FetchProfilesSerializer(serializers.Serializer):
    phone_numbers = serializers.ListField(child=serializers.CharField())

    def validate(self, attrs):
        request = self.context['request']
        phone_numbers = attrs['phone_numbers']
        phone_numbers.append(request.user.phone)       # fetching profile for current user as well
        user_objects = UserModel.objects.filter(phone__in=phone_numbers)
        profiles = UserSerializer(
            user_objects, many=True,
            context={'request': request},
        ).data
        return {profile['id']: profile for profile in profiles}
