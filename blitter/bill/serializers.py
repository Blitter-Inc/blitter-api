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
        file = serializers.SerializerMethodField()

        class Meta:
            model = models.BillAttachment
            exclude = ['bill']

        def get_file(self, obj):
            request = self.context['request']
            return request.build_absolute_uri(obj.file.url)

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
