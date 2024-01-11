from ..models import FieldType, BucketField, Bucket
from asgiref.sync import async_to_sync
import json


class Handler:
    # Sends the provides snapshot (json_event) to all in group
    @staticmethod
    def update(bucket_consumer, json_event):
        print("Inupdate Handler")
        async_to_sync(bucket_consumer.channel_layer.group_send)(
            str(bucket_consumer.bucket.pk),
            json_event
        )


    # Sends snapshot to current user, used on initial connect.
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

    # Helps to create snapshot
    # Will be recursive when Sub Buckets are implemented.
    @staticmethod
    def populate_contents(bucket):
        bucket_dict = dict()
        bucket_dict['name'] = bucket.name
        bucket_dict['id'] = bucket.pk
        bucket_dict['created_at'] = bucket.created_at
        print(bucket_dict)
        # field_type_bucket = FieldType.objects.get(pk=)

        queryset = BucketField.objects.filter(bucket__exact=bucket)
        contents = dict()
        for q in queryset:
            contents[q.key] = {
                "value": q.value,
                "created_at": q.created_at
            }

        bucket_dict['content'] = contents

        return bucket_dict

    # Adds or modifies a field value
    # on success, sends the new snapshot to all listeenrs
    # TODO: on error, will send error msg only to the consumer who requested the changes.
    @staticmethod
    def add_field(bucket_consumer, json_event):
        if bucket_consumer.access.pk == 3:
            error_json = {
                "type": "error",
                "error": "User does not have WRITE Access"
            }
            bucket_consumer.send(text_data=json.dumps(error_json))
            return

        # data has type, name, value keys
        data = json_event.pop('data')

        field_type = FieldType.objects.get(pk=data['type'])
        if data['value']:
            value = data['value']
        else:
            value = ''
        try:
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
            print(e)

    @staticmethod
    def remove_field(bucket_consumer, json_event):
        if bucket_consumer.access.pk == 3:
            error_json = {
                "type": "error",
                "error": "User does not have WRITE Access"
            }
            bucket_consumer.send(text_data=json.dumps(error_json))
            return

        # data has type, name, value keys
        data = json_event.pop('data')

        try:
            BucketField.objects.filter(bucket=bucket_consumer.bucket, key=data['key']).delete()
            # Prepares a snapshot and sends to all the listeners in the group using the update()
            final_json = Handler.create_snapshot(bucket=bucket_consumer.bucket)
            Handler.update(bucket_consumer, final_json)

        except Exception as e:
            print(e)

event_map = {
    'add_field': Handler.add_field,
    'update': Handler.update,
    'remove_field': Handler.remove_field
}