from channels.generic.websocket import WebsocketConsumer
import json
from asgiref.sync import async_to_sync
from django.contrib.auth.models import AnonymousUser
from ..models import UserBucket, Bucket, FieldType, BucketField
from django.contrib.auth.models import AnonymousUser
from ..helpers.messsage_handler import event_map, Handler


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
            Handler.send_snapshot(self)

        # print("Rejecting")
        # self.close(4401)

        async_to_sync(self.channel_layer.group_add)(str(self.bucket.pk), self.channel_name)

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(str(self.bucket.pk), self.channel_name)

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        print(text_data_json)

        event_type = text_data_json['type']
        event_map[event_type](self, text_data_json)

        # async_to_sync(self.channel_layer.group_send)(
        #     str(self.bucket.pk),
        #     text_data_json
        # )

    def update(self, event):
        print("InUpdate Consumer")
        self.send(text_data=json.dumps(event))


    # TODO: IMP this implementation is incorrect
    # TODO: when it calls add_field, its through send_group, so all listeners get this message to process it
    # Even if Viewer sends it, it will be acted upon becz add_field is also called by other users in this group.
    # Handle this before calling send_group. i.e. in receive block.

    # TODO: it check exisitng key for a bucket before creating, if exists, updates the new value and type.
    # TODO: it does check whether the sender has write access,
        # if not, wont create or update but doesnt send a message back.
    # def add_field(self, event):
    #     pass







