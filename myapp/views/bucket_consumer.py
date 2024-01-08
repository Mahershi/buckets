from channels.generic.websocket import WebsocketConsumer
import json
from asgiref.sync import async_to_sync
from django.contrib.auth.models import AnonymousUser
from ..models import UserBucket, Bucket
from django.contrib.auth.models import AnonymousUser


class BucketConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.bucket_id = None
        self.user = None

    def connect(self):
        self.user = self.scope['user']
        self.bucket_id = self.scope['url_route']['kwargs']['bucket_id']
        bucket = Bucket.objects.get(pk=self.bucket_id)

        self.accept()
        if isinstance(self.user, AnonymousUser):
            self.close(4401)
        else:
            print(self.user)
            print(bucket)
            queryset = UserBucket.objects.filter(user__exact=self.user, bucket__exact=bucket)
            if len(queryset) < 1:
                self.close(4401)

        # print("Rejecting")
        # self.close(4401)


        async_to_sync(self.channel_layer.group_add)(self.bucket_id, self.channel_name)

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(self.bucket_id, self.channel_name)

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        print("Got: ", message)

        async_to_sync(self.channel_layer.group_send)(
            self.bucket_id,
            {
                'type': 'chat_message',
                'message': message
             }
        )

    def chat_message(self, event):
        event.pop('type')
        self.send(text_data=json.dumps(event))



