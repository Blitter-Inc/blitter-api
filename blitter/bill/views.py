from django.db.models import Q, Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter

from . import models
from . import serializers


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
        return models.Bill.objects.filter(
            Q(created_by__pk=user_id) | Q(subscribers__pk=user_id)
        ).prefetch_related(
            'subscriber_instances', 'attachments',
        ).distinct().annotate(
            settled_amount=Sum('subscriber_instances__amount_paid'),
        )

    def get_serializer_class(self):
        if self.request.method == 'get':
            return serializers.BillReadSerializer
        return serializers.BillReadSerializer   # will change
