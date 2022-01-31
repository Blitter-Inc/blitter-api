from typing import Callable
from django.db.models import QuerySet
from rest_framework.request import Request

from blitter.shared.types import FetchAPIRequestQueryParams
from . import manager
from . import models
from . import serializers
from . import types


def get_bill_status(bill):
    try:
        if bill.settled_amount and bill.settled_amount >= bill.amount:
            return types.BillStatus.FULFILLED
        return types.BillStatus.UNSETTLED
    except AttributeError:
        raise AttributeError('settled_amount needs to be annotated.')


def generate_initial_fetch_response(
    request: Request,
    props: FetchAPIRequestQueryParams,
    filter_queryset: Callable[[QuerySet], QuerySet],
):
    user_id: int = request.user.pk
    queryset: 'manager.BillQuerySet' = models.Bill.objects.created_by(user_id)
    filtered_queryset: 'manager.BillQuerySet' = filter_queryset(
        queryset.with_complete_data(),
    )
    ordered_sequence = list(filtered_queryset.only(
        'id').values_list('id', flat=True))
    object_batch = serializers.BillReadSerializer(
        filtered_queryset[:props.batch_size],
        many=True, context={'request': request},
    ).data

    return types.BillFetchAPIResponseDict(
        total_count=len(ordered_sequence),
        ordering=props.ordering,
        ordered_sequence=ordered_sequence,
        object_map={obj['id']: obj for obj in object_batch},
    )


def generate_refresh_fetch_response(
    request: Request,
    props: FetchAPIRequestQueryParams,
    filter_queryset: Callable[[QuerySet], QuerySet],
):
    user_id: int = request.user.pk
    queryset: 'manager.BillQuerySet' = models.Bill.objects.created_by(user_id)
    total_count: int = queryset.count()
    filtered_queryset: 'manager.BillQuerySet' = filter_queryset(
        queryset.with_complete_data(),
    )
    object_list = serializers.BillReadSerializer(
        filtered_queryset, many=True, context={'request': request}).data
    ordered_sequence = [obj['id'] for obj in object_list]
    object_map = {obj['id']: obj for obj in object_list}

    return types.BillFetchAPIResponseDict(
        total_count=total_count,
        ordering=props.ordering,
        ordered_sequence=ordered_sequence,
        object_map=object_map,
    )
