from channels.generic.websocket import WebsocketConsumer
import json
from asgiref.sync import async_to_sync
from django.contrib.auth.models import AnonymousUser
from ..models import UserBucket, Bucket, FieldType, BucketField
from django.contrib.auth.models import AnonymousUser


class BucketConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.bucket_id = None
        self.user = None
        self.bucket = None
        self.access = None

    def connect(self):
        self.user = self.scope['user']
        bucket_id = self.scope['url_route']['kwargs']['bucket_id']
        self.bucket = Bucket.objects.get(pk=bucket_id)

        self.accept()
        if isinstance(self.user, AnonymousUser):
            self.close(4401)
        else:
            print(self.user)
            queryset = UserBucket.objects.filter(user__exact=self.user, bucket__exact=self.bucket)

            # If no entry for user-bucket - disconnect - user not allowed
            if len(queryset) < 1:
                self.close(4401)

            # user allowed - set access level for this connection.
            self.access = queryset[0].access

        # print("Rejecting")
        # self.close(4401)

        async_to_sync(self.channel_layer.group_add)(str(self.bucket.pk), self.channel_name)

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(str(self.bucket.pk), self.channel_name)

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        print(text_data_json)

        async_to_sync(self.channel_layer.group_send)(
            str(self.bucket.pk),
            text_data_json
        )

    def chat_message(self, event):
        event.pop('type')
        self.send(text_data=json.dumps(event))


    # TODO: IMP this implementation is incorrect
    # TODO: when it calls add_field, its through send_group, so all listeners get this message to process it
    # Even if Viewer sends it, it will be acted upon becz add_field is also called by other users in this group.
    # Handle this before calling send_group. i.e. in receive block.

    # TODO: it check exisitng key for a bucket before creating, if exists, updates the new value and type.
    # TODO: it does check whether the sender has write access,
        # if not, wont create or update but doesnt send a message back.
    def add_field(self, event):
        if self.access.pk == 3:
            print("Write access not granted!")
            # self.send(text_data="Write Access not granted!")
            return
        print("in add_field: ", self.user)
        # data has type, name, value keys
        data = event.pop('data')

        field_type = FieldType.objects.get(pk=data['type'])
        if data['value']:
            value = data['value']
        else:
            value = ''
        try:
            bucket_field, created = BucketField.objects.update_or_create(
                key=data['key'],
                bucket=self.bucket,
                defaults={
                    "type": field_type,
                    "value": value
                }
            )

            # bucket_field.save()
            print("Created: " + str(created))
        except Exception as e:
            print(e)




