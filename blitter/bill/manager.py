from datetime import datetime
from django.db.models import Manager, QuerySet, Q, Sum


class BillManager(Manager):

    def created_by(self, user_id: int) -> QuerySet:
        return self.get_queryset().filter(
            Q(created_by__pk=user_id) | Q(subscribers__user_id=user_id),
        ).distinct()


class BillQuerySet(QuerySet):

    def with_complete_data(self) -> QuerySet:
        return self.annotate(
            settled_amount=Sum('subscribers__amount_paid'),
        ).prefetch_related(
            'subscribers', 'attachments',
        )

    def updated_after(self, datetime_str: datetime) -> QuerySet:
        return self.filter(updated_at__gte=datetime_str)
