from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from blitter.shared.models import TimestampMixin
from .manager import UserManager


class User(TimestampMixin, AbstractBaseUser, PermissionsMixin):

    firebase_id = models.CharField(
        'Firebase ID', max_length=254, blank=False, unique=True)
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

    @property
    def primary_upi(self):
        return self.upi_addresses.filter(is_primary=True).first()


class UPIAddress(TimestampMixin):

    user = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='upi_addresses')
    address = models.CharField(
        'Address', max_length=128, blank=False, unique=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = 'user_upiaddress'
        verbose_name = 'UPI Address'
        verbose_name_plural = 'UPI Addresses'
        constraints = [
            models.UniqueConstraint(fields=['user'], condition=models.Q(
                is_primary=True), name='unique_primaryupiaddress_user'),
        ]

    def __str__(self) -> str:
        return self.address


class Transaction(TimestampMixin):

    class TransactionMode(models.TextChoices):
        UPI = 'upi', 'UPI'
        CREDIT_CARD = 'credit_card', 'Credit Card'
        DEBIT_CARD = 'debit_card', 'Debit Card'
        NET_BANKING = 'net_banking', 'Net Banking'

    class TransactionStatus(models.TextChoices):
        FAILED = 'failed', 'Failed'
        SUCCESS = 'success', 'Success'

    sender = models.ForeignKey(
        'User', on_delete=models.DO_NOTHING, related_name='debit_transactions')
    receiver = models.ForeignKey(
        'User', on_delete=models.DO_NOTHING, related_name='credit_transactions')
    mode = models.CharField('Mode', max_length=128,
                            choices=TransactionMode.choices)
    amount = models.DecimalField(
        'Amount', max_digits=12, decimal_places=2, blank=False)
    status = models.CharField('Status', max_length=128,
                              choices=TransactionStatus.choices)

    class Meta:
        db_table = 'user_transaction'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'

    def __str__(self) -> str:
        return f"Amount: {self.amount} ({self.status})"
