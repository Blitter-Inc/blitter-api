from rest_framework import serializers

from . import models, utils


class BillSubscriberNestedSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.BillSubscriber
        exclude = ['bill']


class BillAttachmentNestedSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.BillAttachment
        exclude = ['bill']


class BillReadSerializer(serializers.ModelSerializer):

    status = serializers.SerializerMethodField()
    settled_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    subscribers = BillSubscriberNestedSerializer(many=True)
    attachments = serializers.SerializerMethodField()

    class Meta:
        model = models.Bill
        fields = [
            'id', 'name', 'type', 'description',
            'status', 'amount', 'settled_amount',
            'created_by', 'created_at', 'updated_at',
            'subscribers', 'attachments',
        ]

    def get_status(self, obj):
        return utils.get_bill_status(obj)

    def get_attachments(self, obj):
        attachments = obj.attachments.all()
        return BillAttachmentNestedSerializer(
            attachments, many=True,
            context={'request': self.context['request']},
        ).data


class BillWriteSerializer(serializers.ModelSerializer):

    subscribers = BillSubscriberNestedSerializer(
        many=True, required=False, allow_null=True)
    settled_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True)
    created_by = serializers.SerializerMethodField()
    attachments = serializers.SerializerMethodField()

    class Meta:
        model = models.Bill
        fields = '__all__'

    def get_created_by(self, obj):
        return obj.created_by_id

    def get_attachments(self, obj):
        attachments = obj.attachments.all()
        return BillAttachmentNestedSerializer(
            attachments, many=True,
            context={'request': self.context['request']},
        ).data

    def create_subscribers(self, bill, subscribers):
        models.BillSubscriber.objects.bulk_create([
            models.BillSubscriber(bill=bill, **obj)
            for obj in subscribers
        ], ignore_conflicts=True)

    def create(self, validated_data):
        user = self.context['request'].user
        attachments = validated_data.pop('attachments', None)
        subscribers = validated_data.pop('subscribers', None)
        bill_obj = super().create({**validated_data, 'created_by': user})
        if subscribers:
            self.create_subscribers(bill_obj, subscribers)
        if attachments:
            self.create_attachments(bill_obj, attachments)
        return bill_obj

    def update(self, instance, validated_data):
        subscribers = validated_data.pop('subscribers', None)
        super().update(instance, validated_data)
        if subscribers:
            # Updating values for existing Bill subscribers
            models.BillSubscriber.bulk_update_individual(subscribers)
            # Adding new Bill subscribers
            self.create_subscribers(instance, subscribers)
            # Deleting Bill subscribers that are not in currently provided subscriber object
            # and have amount_paid = 0
            subscriber_user_ids = [obj['user'] for obj in subscribers]
            models.BillSubscriber.objects.filter(
                bill=instance,
                amount_paid=0,
            ).exclude(
                user_id__in=subscriber_user_ids,
            ).delete()

        return instance
