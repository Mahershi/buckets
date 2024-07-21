from channels.generic.websocket import WebsocketConsumer
import json
from asgiref.sync import async_to_sync
from ..models import UserBucket, Bucket
from django.contrib.auth.models import AnonymousUser
from ..helpers.messsage_handler import event_map, Handler
from django.core.exceptions import ObjectDoesNotExist

'''
    Represents a WebSocket Connection Channel and its Consumer.
    Presents method for Consumer to initiate and maintain WebSocket connection.
'''
class BucketConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.bucket_id = None
        self.user = None
        self.bucket = None
        self.access = None
        self.qp = None

    # Attach a consumer to a bucket, i.e. initialize consumer.
    def connect(self):
        # User is authorized using JWT Token in the header.
        self.user = self.scope['user']
        bucket_id = self.scope['url_route']['kwargs']['bucket_id']

        try:
            self.bucket = Bucket.objects.get(pk=bucket_id)
        except ObjectDoesNotExist:
            # if the bucket does not exist, accept and close.
            # WebSockets cannot be closed normally without accepting first.
            self.accept()
            self.close(4401)
            return
        self.accept()
        if isinstance(self.user, AnonymousUser):
            # Unauthorized User - Close WebSocket Connection
            self.close(4401)
        else:
            # User Authorized and Bucket exists, but user might not have access to bucket.
            # Check relation between user and bucket in database, along with Access level.
            queryset = UserBucket.objects.filter(user__exact=self.user, bucket__exact=self.bucket)

            if len(queryset) < 1:
                # If no entry for table user-bucket - disconnect - user not allowed
                self.close(4401)
            else:
                # user/consumer allowed - set access level for this connection.
                self.access = queryset[0].access
                print("Sending Snapshot")

                # Call handler method to send the latest snapshot to new connecting consumer.
                Handler.send_snapshot(self)

                # Add the Consumer to the group to allow broadcast.
                async_to_sync(self.channel_layer.group_add)(str(self.bucket.pk), self.channel_name)

    # Disconnect consumer
    def disconnect(self, code):
        try:
            async_to_sync(self.channel_layer.group_discard)(str(self.bucket.pk), self.channel_name)
        except Exception as e:
            # TODO: Add more specific Exception Handling
            pass

    # Triggered when this WebSocket receives a Message.
    def receive(self, text_data=None, bytes_data=None):
        try:
            # Deserialize string to json
            text_data_json = json.loads(text_data)
            # Extract type of event
            event_type = text_data_json['type']
            # Trigger handler method based on type of method.
            event_map[event_type](self, text_data_json)
        except Exception as e:
            # TODO: Implement more specific Exception handling.
            print("Receive Exception: ", e)

    # Sends the json string over the web socket connection for the 'self' (current obj) consumer
    def update(self, event):
        # Serialize json to string, only string allowed to send over web socket connection.
        self.send(text_data=json.dumps(event, default=str))








