from ..models import FieldType, BucketField
from asgiref.sync import async_to_sync
import json

'''
    Handler class providing static methods for Bucket Consumer Class.
'''
class Handler:
    # Sends the provided snapshot (json_event) to all the listeners (consumers) in group
    # bucket_consumer is the consumer that triggered the event.
    @staticmethod
    def update(bucket_consumer, json_event):
        # Triggers the BucketConsumer.update() for all the current consumers.
        async_to_sync(bucket_consumer.channel_layer.group_send)(
            str(bucket_consumer.bucket.pk),
            json_event
        )

    # Sends snapshot to current consumer, used on initial connect.
    @staticmethod
    def send_snapshot(bucket_consumer):
        final_json = Handler.create_snapshot(bucket_consumer.bucket)
        bucket_consumer.send(json.dumps(final_json, default=str))

    # Prepares a JSON snapshot of given bucket.
    @staticmethod
    def create_snapshot(bucket):
        json_data = Handler.populate_contents(bucket)
        final_json = dict()
        final_json['type'] = 'update'
        final_json['data'] = json_data

        return final_json

    # Helps to create snapshot - populates all existing fields
    # Will be recursive when Sub Buckets are implemented.
    @staticmethod
    def populate_contents(bucket):
        bucket_dict = dict()
        bucket_dict['name'] = bucket.name
        bucket_dict['id'] = bucket.pk
        bucket_dict['created_at'] = bucket.created_at

        # get the contents of the bucket from database
        queryset = BucketField.objects.filter(bucket__exact=bucket)
        contents = dict()
        for q in queryset:
            contents[q.key] = {
                "value": q.value,
                "created_at": q.created_at,
                "type": q.type
            }

        bucket_dict['content'] = contents

        return bucket_dict

    # Adds or modifies a field value
    # on success, sends the new snapshot to all consumers
    @staticmethod
    def add_field(bucket_consumer, json_event):
        # Access Level id=3 is read only.
        if bucket_consumer.access.pk == 3:
            error_json = {
                "type": "error",
                "error": "User does not have WRITE Access"
            }
            # on error, send error message only to consumer that triggered the event
            bucket_consumer.send(text_data=json.dumps(error_json))
            return


        data = json_event.pop('data')
        # 'data' has type, name and value keys

        field_type = FieldType.objects.get(pk=data['type'])
        if data['value']:
            value = data['value']
        else:
            # if 'value' missing, create an empty field
            value = ''
        try:
            # update or create field in the database.
            bucket_field, created = BucketField.objects.update_or_create(
                key=data['key'],
                bucket=bucket_consumer.bucket,
                defaults={
                    "type": field_type,
                    "value": value
                }
            )
            # When created or edited, on success
            # Prepares a snapshot and sends to all the listeners in the group using the update()
            final_json = Handler.create_snapshot(bucket=bucket_consumer.bucket)
            Handler.update(bucket_consumer, final_json)

        except Exception as e:
            # TODO: handle database error and notify consumer that triggered the event.
            print(e)

    # To remove an existing field from the bucket.
    # Don't need to move this to cron job as deleting one field at a time is not expensive.
    @staticmethod
    def remove_field(bucket_consumer, json_event):
        # Access Level id=3 is read only.
        if bucket_consumer.access.pk == 3:
            error_json = {
                "type": "error",
                "error": "User does not have WRITE Access"
            }
            # on error, send error message only to consumer that triggered the event
            bucket_consumer.send(text_data=json.dumps(error_json))
            return


        data = json_event.pop('data')

        try:
            # Extract field name (key) from the json_event
            # remove the field from the database for the bucket.
            BucketField.objects.filter(bucket=bucket_consumer.bucket, key=data['key']).delete()
            # Prepares a snapshot and sends to all the listeners in the group using the update()
            final_json = Handler.create_snapshot(bucket=bucket_consumer.bucket)
            Handler.update(bucket_consumer, final_json)

        except Exception as e:
            # TODO: handle database error and notify consumer that triggered the event.
            print(e)

# mapping json_event types to handler methods.
# used by bucket_consumer class
event_map = {
    'add_field': Handler.add_field, # when new field is added.
    'update': Handler.update,   # unused for the moment. Not sure why we created this.
    'remove_field': Handler.remove_field    # when a field is deleted.
}