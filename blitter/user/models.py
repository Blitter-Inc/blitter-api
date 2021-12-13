from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from blitter.shared.models import TimestampMixin
from .manager import UserManager


class User(TimestampMixin, AbstractBaseUser, PermissionsMixin):

    firebase_id = models.CharField(
        "Firebase ID", max_length=254, blank=False, unique=True)
    name = models.CharField('Name', max_length=254, blank=True)
    phone = models.CharField('Phone', max_length=18, blank=False, unique=True)
    email = models.EmailField('Email', blank=True, null=True, unique=True)
    bio = models.TextField('Bio', blank=True)
    avatar = models.FileField(
        'Avatar', upload_to='user/avatar', blank=True, null=True)
    is_staff = models.BooleanField('Is staff', default=False)
    date_joined = models.DateTimeField('Date joined', default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    EMAIL_FIELD = 'email'

    def __str__(self) -> str:
        return f'{self.phone} [{self.name}]'
