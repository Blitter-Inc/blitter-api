from django.db.models import Q, Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter

from blitter.shared.types import FetchAPIRequestType
from blitter.shared.utils import FetchAPIRequestParser
from . import models
from . import serializers
from . import utils


class BillViewSet(ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description', 'type', 'created_by__name']
    ordering_fields = [
        'name', 'amount', 'type',
        'created_by__name', 'created_at', 'updated_at',
    ]
    ordering = ['-updated_at', '-created_at']

    def get_queryset(self):
        user_id = self.request.user.pk
        return models.Bill.objects.annotate(
            settled_amount=Sum('subscribers__amount_paid'),
        ).filter(
            Q(created_by__pk=user_id) | Q(subscribers__user_id=user_id)
        ).distinct().prefetch_related(
            'subscribers', 'attachments',
        )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.BillReadSerializer
        elif self.request.method == 'POST' or self.request.method == 'PATCH':
            return serializers.BillWriteSerializer
        return serializers.BillReadSerializer   # will change

    @action(methods=['GET'], detail=False)
    def fetch(self, request: Request) -> Response:
        parser = FetchAPIRequestParser(request)
        if not parser.is_valid():
            return Response(data=parser.error_dict, status=status.HTTP_400_BAD_REQUEST)

        props = parser.props

        if props.request_type == FetchAPIRequestType.INITIAL:
            response_dict = utils.generate_initial_fetch_response(
                request, props)
        elif props.request_type == FetchAPIRequestType.REFRESH:
            response_dict = utils.generate_refresh_fetch_response(
                request, props)

        return Response(response_dict)
