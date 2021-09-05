from django.db import models
from django.utils import timezone

from blitter.shared.models import TimestampMixin


class Event(TimestampMixin, models.Model):

    class EventType(models.TextChoices):
        # TODO: Add more EventTypes
        MISC = 'misc', 'Miscellaneous'

    name = models.CharField('Event name', max_length=254, blank=False)
    type = models.CharField('Event type', max_length=254,
                            choices=EventType.choices, default=EventType.MISC)
    description = models.TextField('Event description', blank=True)
    start = models.DateTimeField('Start', default=timezone.now)
    end = models.DateTimeField('End', blank=True, null=True)
    venue = models.CharField('Event venue', max_length=254, blank=True)
    cover_image = models.FileField(
        'Cover image', upload_to='media/event/event/cover_image', blank=True, null=True)
    created_by = models.ForeignKey(
        'user.User', on_delete=models.SET_NULL, related_name='created_events', null=True)
    members = models.ManyToManyField('user.User')
    bills = models.ManyToManyField('bill.Bill', through='EventBill')

    class Meta:
        db_table = 'event_event'
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def __str__(self):
        return f'ID: {self.pk} | {self.name}'


class EventBill(TimestampMixin, models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    bill = models.ForeignKey('bill.Bill', on_delete=models.CASCADE)
    last_updated_by = models.ForeignKey(
        'user.User', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'event_eventbill'
        verbose_name = 'Event Bill'
        verbose_name_plural = 'Event Bills'

    def __str__(self):
        return f'ID: {self.pk} | EventID {self.event_id}'
