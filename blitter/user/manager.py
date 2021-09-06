from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone, password, **kwargs):
        if not phone:
            raise ValueError('User must have a phone.')

        if 'email' in kwargs:
            kwargs['email'] = self.normalize_email(kwargs['email'])

        user = self.model(phone=phone, **kwargs)
        user.password = make_password(password)
        user.save()
        return user

    def create_user(self, phone, password=None, **kwargs):
        return self._create_user(phone, password, **kwargs)

    def create_superuser(self, phone, password, **kwargs):
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_staff', True)
        return self._create_user(phone, password, **kwargs)
