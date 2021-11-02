from rest_framework import serializers

from . import models, utils


class BillReadSerializer(serializers.ModelSerializer):

    class BillSubscriberNestedSerializer(serializers.ModelSerializer):

        class Meta:
            model = models.BillSubscriber
            fields = [
                'id', 'user_id', 'amount', 'amount_paid',
                'fulfilled', 'created_at', 'updated_at',
            ]

    class BillAttachmentNestedSerializer(serializers.ModelSerializer):

        class Meta:
            model = models.BillAttachment
            exclude = ['bill']

    status = serializers.SerializerMethodField()
    settled_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    subscribers = serializers.SerializerMethodField()
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

    def get_subscribers(self, obj):
        subscribers = obj.subscriber_instances.all()
        return self.BillSubscriberNestedSerializer(subscribers, many=True).data

    def get_attachments(self, obj):
        attachments = obj.attachments.all()
        return self.BillAttachmentNestedSerializer(
            attachments, many=True,
            context={'request': self.context['request']},
        ).data


class BillWriteSerializer(serializers.ModelSerializer):

    class BillSubscriberNestedSerializer(serializers.ModelSerializer):

        class Meta:
            model = models.BillSubscriber
            fields = [
                'id', 'user_id', 'amount',
                'amount_paid', 'fulfilled',
            ]

    class BillAttachmentNestedSerializer(serializers.Serializer):
        name = serializers.CharField(required=False)
        file = serializers.FileField()

    attachments = BillAttachmentNestedSerializer(
        many=True, required=False, allow_null=True)
    subscribers = BillSubscriberNestedSerializer(
        many=True, required=False, allow_null=True)

    class Meta:
        model = models.Bill
        exclude = ['created_by']

    def create_subscribers(self, bill, subscribers):
        models.BillSubscriber.objects.bulk_create([
            models.BillSubscriber(bill=bill, **obj)
            for obj in subscribers
        ])

    def create_attachments(self, bill, attachments):
        models.BillAttachment.objects.bulk_create([
            models.BillAttachment(bill=bill, **obj)
            for obj in attachments
        ])

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
