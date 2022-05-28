from django.contrib.auth import get_user_model
from django.db.models import Q, Sum
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, DestroyModelMixin
from rest_framework.viewsets import ViewSet, GenericViewSet
from rest_framework_simplejwt.views import TokenViewBase

from blitter.bill import models as bill_models
from . import models
from . import serializers


UserModel = get_user_model()


class CustomTokenObtainPairView(TokenViewBase):
    serializer_class = serializers.CustomTokenObtainPairSerializer


class UserViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @action(methods=['PATCH'], detail=False, url_name='update-profile', url_path='update-profile')
    def update_profile(self, request):
        serializer = serializers.UserSerializer(
            request.user, data=request.data, partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(methods=['POST'], detail=False, url_name='fetch-profiles', url_path='fetch-profiles')
    def fetch_profiles(self, request):
        serializer = serializers.FetchProfilesSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
    
    @action(methods=['GET'], detail=False, url_name='fetch-counters', url_path='fetch-counters')
    def fetch_counters(self, request):
        res = dict()
        user_id = request.user.id
        bill_query = bill_models.Bill.objects.filter(
            Q(created_by__pk=user_id) | Q(subscribers__user_id=user_id)
        ).distinct()
        res['total_bill_count'] = bill_query.count()
        
        res['total_transaction_count'] = models.Transaction.objects.filter(Q(sender__pk=user_id) | Q(receiver__pk=user_id)).count()
        
        credit_transaction_query = models.Transaction.objects.filter(receiver__pk=user_id)
        res['credit_transaction_count'] = credit_transaction_query.count()
        res['credit_transaction_amount'] = credit_transaction_query.aggregate(credit_transaction_amount=Sum('amount'))['credit_transaction_amount']
        
        debit_transaction_query = models.Transaction.objects.filter(sender__pk=user_id)
        res['debit_transaction_count'] = debit_transaction_query.count()
        res['debit_transaction_amount'] = debit_transaction_query.aggregate(debit_transaction_amount=Sum('amount'))['debit_transaction_amount']

        return Response(res)


class UPIAddressViewSet(GenericViewSet, ListModelMixin, DestroyModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UPIAddressSerializer

    def get_queryset(self):
        return models.UPIAddress.objects.filter(user=self.request.user)

    @staticmethod
    def get_object_query(pk):
        query = models.UPIAddress.objects.filter(pk=pk)
        if not query.exists():
            raise NotFound()
        return query

    @action(methods=['POST'], detail=False)
    def add(self, request):
        serializer = self.get_serializer_class()(
            data={**request.data, 'user': request.user.pk, 'is_primary': not request.user.upi_addresses.exists()})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(methods=['PATCH'], detail=True, url_name='set-primary', url_path='set-primary')
    def set_primary(self, request, pk):
        query = self.get_object_query(pk)
        models.UPIAddress.objects.filter(user=request.user).exclude(
            pk=pk).update(is_primary=False, updated_at=timezone.now())
        query.update(is_primary=True, updated_at=timezone.now())
        return Response({'message': 'success'})


class TransactionViewSet(GenericViewSet, ListModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.TransactionSerializer

    def mark_bill_subscriber_as_paid(self, request):
        subscriber = bill_models.BillSubscriber.objects.select_related('bill').filter(
            pk=request.data.get('subscriber_id'),
        ).first()
        subscriber.amount_paid = subscriber.amount
        subscriber.fulfilled = True
        subscriber.save()
        bill = subscriber.bill
        bill.updated_at = timezone.now()
        bill.save()

    def get_queryset(self):
        user = self.request.user
        return models.Transaction.objects.filter(Q(sender=user) | Q(receiver=user))

    @staticmethod
    def get_object_query(pk):
        query = models.Transaction.objects.filter(pk=pk)
        if not query.exists():
            raise NotFound()
        return query

    @action(methods=['POST'], detail=False)
    def add(self, request):
        serializer = self.get_serializer_class()(
            data={**request.data, 'sender': request.user.pk})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.mark_bill_subscriber_as_paid(request)
        return Response(serializer.data)

    @action(methods=['PATCH'], detail=True)
    def status(self, request, pk):
        query = self.get_object_query(pk)
        new_status = request.data.get('status')
        if not new_status or new_status not in {
            models.Transaction.TransactionStatus.PENDING.value,
            models.Transaction.TransactionStatus.FAILED.value,
            models.Transaction.TransactionStatus.SUCCESS.value,
        }:
            raise ValidationError("Provide valid value for status.")
        query.update(status=new_status, updated_at=timezone.now())
        return Response({'message': 'success'})
