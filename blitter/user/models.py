from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from .manager import UserManager


class User(AbstractBaseUser, PermissionsMixin):

    name = models.CharField('Name', max_length=254, blank=False)
    phone = models.CharField('Phone', max_length=18, blank=False, unique=True)
    email = models.EmailField('Email', blank=False, null=True, unique=True)
    bio = models.TextField('Bio', blank=True, null=True)
    avatar = models.FileField(
        'Avatar', upload_to='media/user/avatar', blank=True, null=True)
    is_staff = models.BooleanField('Is staff', default=False)
    date_joined = models.DateTimeField('Date joined', default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    EMAIL_FIELD = 'email'

    def __str__(self) -> str:
        return f'{self.phone} [{self.name}]'
