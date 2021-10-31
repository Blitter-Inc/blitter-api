from rest_framework import serializers

from . import models


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


    subscribers = serializers.SerializerMethodField()
    attachments = serializers.SerializerMethodField()

    class Meta:
        model = models.Bill
        fields = [
            'id', 'name', 'type', 'amount', 'description',
            'created_by', 'created_at', 'updated_at',
            'subscribers', 'attachments',
        ]
    
    def get_subscribers(self, obj):
        subscribers = obj.subscriber_instances.all()
        return self.BillSubscriberNestedSerializer(subscribers, many=True).data

    def get_attachments(self, obj):
        attachments = obj.attachments.all()
        return self.BillAttachmentNestedSerializer(attachments, many=True, context={'request': self.context['request']}).data
