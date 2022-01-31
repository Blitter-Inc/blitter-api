from django.db.models import F
from django_filters import rest_framework as filters

from blitter.shared import utils
from . import manager
from . import models
from . import types


class BillFilter(filters.FilterSet):
    status = filters.TypedChoiceFilter(
        choices=(
            (types.BillStatus.UNSETTLED, 'Unsettled'),
            (types.BillStatus.FULFILLED, 'Fulfilled'),
        ),
        method='filter_status',
    )
    last_refreshed = filters.CharFilter(method='filter_last_refreshed')

    def filter_status(
        self, queryset: 'manager.BillQuerySet',
        _, value: str,
    ) -> 'manager.BillQuerySet':
        if value == types.BillStatus.FULFILLED:
            return queryset.filter(settled_amount__gte=F('amount'))
        elif value == types.BillStatus.UNSETTLED:
            return queryset.filter(settled_amount__lt=F('amount'))
        return queryset

    def filter_last_refreshed(
        self, queryset: 'manager.BillQuerySet',
        _, value: str,
    ) -> 'manager.BillQuerySet':
        last_refreshed_datetime = utils.parse_datetime_string(value)
        return queryset.filter(updated_at__gte=last_refreshed_datetime)

    class Meta:
        model = models.Bill
        fields = ['type', 'status', 'last_refreshed']
