from dataclasses import dataclass
from django.db import models, transaction

from blitter.shared.models import TimestampMixin


class Bill(TimestampMixin, models.Model):

    class BillType(models.TextChoices):
        FOOD = 'food', 'Food'
        SHOPPING = 'shopping', 'Shopping'
        ENTERTAINMENT = 'entertainment', 'Entertainment'
        OUTING = 'outing', 'Outing'
        MISC = 'miscelleneous', 'Miscellaneous'

    @dataclass
    class BillStatus:
        UNSETTLED = 'unsettled'
        FULFILLED = 'fulfilled'

    name = models.CharField('Bill name', max_length=254, blank=True)
    amount = models.DecimalField(
        'Amount', max_digits=12, decimal_places=2, blank=False)
    type = models.CharField('Bill type', max_length=254,
                            choices=BillType.choices, default=BillType.MISC)
    description = models.TextField('Description', blank=True)
    created_by = models.ForeignKey(
        'user.User', on_delete=models.SET_NULL, related_name='created_bills', null=True)

    class Meta:
        db_table = 'bill_bill'
        verbose_name = 'Bill'
        verbose_name_plural = 'Bills'

    def __str__(self):
        return f'ID: {self.pk} | {self.name}: {self.amount}'


class BillSubscriber(TimestampMixin, models.Model):
    bill = models.ForeignKey(
        'Bill', on_delete=models.CASCADE, related_name="subscribers")
    user = models.ForeignKey(
        'user.User', on_delete=models.CASCADE, related_name="subscribed_bills")
    amount = models.DecimalField(
        'Amount', max_digits=12, decimal_places=2, blank=False)
    amount_paid = models.DecimalField(
        'Amount paid', max_digits=12, decimal_places=2, default=0)
    fulfilled = models.BooleanField('Fullfilled', default=False)

    class Meta:
        db_table = 'bill_billsubscriber'
        verbose_name = 'Bill Subscriber'
        verbose_name_plural = 'Bill Subscribers'
        constraints = [
            models.UniqueConstraint(
                fields=['bill', 'user'], name='unique_bill_subscriber')
        ]

    def __str__(self):
        return f'ID: {self.pk} | {self.amount}/-'
    
    @classmethod
    def bulk_update_individual(cls, subscribers: list[dict]):
        with transaction.atomic():
            for obj in subscribers:
                user_id = obj.get('user')
                if not user_id:
                    continue
                values_to_be_updated = obj.copy()
                values_to_be_updated.pop('user')
                cls.objects.filter(user_id=user_id).update(**values_to_be_updated)



class BillAttachment(TimestampMixin, models.Model):
    bill = models.ForeignKey(
        'Bill', on_delete=models.CASCADE, related_name='attachments')
    name = models.CharField('Bill attachment name', max_length=254, blank=True)
    file = models.FileField(
        'File', upload_to='bill/billattachment', blank=False)

    class Meta:
        db_table = 'bill_billattachment'
        verbose_name = 'Bill Attachment'
        verbose_name_plural = 'Bill Attachments'

    def __str__(self):
        return f'ID: {self.pk} | {self.name}'
