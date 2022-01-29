from django.db.models import Q, Sum, QuerySet
from rest_framework.request import Request

from blitter.shared.types import FetchAPIRequestQueryParams
from blitter.shared.utils import parse_datetime_string
from . import models
from . import serializers
from . import types


def get_bill_status(bill):
    try:
        if bill.settled_amount and bill.settled_amount >= bill.amount:
            return models.Bill.BillStatus.FULFILLED
        return models.Bill.BillStatus.UNSETTLED
    except AttributeError:
        raise AttributeError('settled_amount needs to be annotated.')


def generate_initial_fetch_response(request: Request, props: FetchAPIRequestQueryParams):
    user_id = request.user.pk
    queryset: 'QuerySet[models.Bill]' = models.Bill.objects.filter(
        Q(created_by__pk=user_id) | Q(subscribers__user_id=user_id)
    ).distinct().order_by(props.ordering)
    ordered_sequence = list(queryset.only(
        'id').values_list('id', flat=True))
    object_batch = serializers.BillReadSerializer(queryset.annotate(
        settled_amount=Sum('subscribers__amount_paid'),
    ).prefetch_related(
        'subscribers', 'attachments',
    )[:props.batch_size], many=True, context={'request': request}).data

    return types.BillFetchAPIResponseDict(
        total_count=len(ordered_sequence),
        ordering=props.ordering,
        ordered_sequence=ordered_sequence,
        object_map={obj['id']: obj for obj in object_batch},
    )


def generate_refresh_fetch_response(request: Request, props: FetchAPIRequestQueryParams):
    user_id = request.user.pk
    last_refreshed = parse_datetime_string(props.last_refreshed)
    queryset = models.Bill.objects.filter(
        Q(created_by__pk=user_id) | Q(subscribers__user_id=user_id),
    ).distinct()
    total_count = queryset.count()
    object_list = serializers.BillReadSerializer(
        queryset.filter(
            updated_at__gte=last_refreshed,
        ).order_by(props.ordering).annotate(
            settled_amount=Sum('subscribers__amount_paid'),
        ).prefetch_related(
            'subscribers', 'attachments',
        ), many=True, context={'request': request}).data
    ordered_sequence = [obj['id'] for obj in object_list]
    object_map = {obj['id']: obj for obj in object_list}

    return types.BillFetchAPIResponseDict(
        total_count=total_count,
        ordering=props.ordering,
        ordered_sequence=ordered_sequence,
        object_map=object_map,
    )
