from ..models import FieldType, BucketField, Bucket
from asgiref.sync import async_to_sync
import json


class Handler:
    # When a new update is received, i.e. update in field values
    # still need to figure out how to process deletion of fields, probably different function
    # TODO: Call model updates using CronJobs to change in DB
    @staticmethod
    def update(bucket_consumer, json_event):
        print("Inupdate Handler")
        async_to_sync(bucket_consumer.channel_layer.group_send)(
            str(bucket_consumer.bucket.pk),
            json_event
        )

    @staticmethod
    def send_snapshot(bucket_consumer):
        print("Send Snapshot: ")
        json_data = Handler.populate_contents(bucket_consumer.bucket)
        final_json = dict()
        final_json['type'] = 'update'
        final_json['data'] = json_data
        bucket_consumer.send(json.dumps(final_json, default=str))



    @staticmethod
    def populate_contents(bucket):
        bucket_dict = dict()
        bucket_dict['name'] = bucket.name
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

    @staticmethod
    def add_field(bucket_consumer, json_event):
        print("in add_field: ", bucket_consumer.user)
        if bucket_consumer.access.pk == 3:
            print("Write access not granted!")
            bucket_consumer.send(text_data="Write Access not granted!")
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

            # bucket_field.save()
            print("Created: " + str(created))


        except Exception as e:
            print(e)


event_map = {
    'add_field': Handler.add_field,
    'update': Handler.update
}