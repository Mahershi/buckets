'''
    TODO: Implement cron jobs where required to improve response time.
        Possibly while remove array element.

'''


from ..models import FieldType, BucketField, Bucket, ArrayField
from asgiref.sync import async_to_sync
import json
from django.core.exceptions import ObjectDoesNotExist
import traceback



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


    @staticmethod
    def populate_array(bf: BucketField):
        array_elements: ArrayField = ArrayField.objects.filter(parent_field=bf).order_by('index')
        contents = dict()

        contents['name'] = bf.key
        contents['created_at'] = bf.created_at
        contents['type'] = bf.type

        elements = list()
        for element in array_elements:
            elements.append({
                "value": element.value,
                "index": element.index,
                "type": element.type,
                "created_at": element.created_at
            })
        contents['elements'] = elements
        return contents

    # Helps to create snapshot - populates all existing fields
    # Will be recursive when Sub Buckets are implemented.
    @staticmethod
    def populate_contents(bucket):
        bucket_dict = dict()
        bucket_dict['name'] = bucket.name
        bucket_dict['id'] = bucket.pk
        bucket_dict['created_at'] = bucket.created_at

        # get the contents of the bucket from database
        try:
            queryset = BucketField.objects.filter(bucket__exact=bucket)
            contents = dict()
            for q in queryset:
                if q.type.id == 4:
                    sub_bucket: Bucket = Bucket.objects.get(pk=q.value)
                    contents[q.key] = Handler.populate_contents(sub_bucket)
                    contents[q.key]['type'] = 'BUCKET'
                elif q.type.id == 5:
                    contents[q.key] = Handler.populate_array(q)
                else:
                    contents[q.key] = {
                        "value": q.value,
                        "created_at": q.created_at,
                        "type": q.type
                    }

            bucket_dict['content'] = contents
        except Exception as e:
            print("Exception Populating Contents: ", str(e))
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
            cur_bucket = bucket_consumer.bucket
            if '.' in data['key']:
                try:
                    for sub_b_name in data['key'].split('.')[:-1]:
                        print("For slug:", sub_b_name)
                        # just to check if sub_b exists in the cur_bucket.
                        bf: BucketField = BucketField.objects.get(bucket=cur_bucket, key=sub_b_name)
                        # bf.value is the pk of the subbucket.
                        cur_bucket: Bucket = Bucket.objects.get(pk=bf.value)
                except ObjectDoesNotExist as e:
                    print("Bucket hierarchy exception: ", sub_b_name, " not found!")
                    print(traceback.format_exc())
                    return
                except Exception as e:
                    print("Unknown Exception: ", e)
                    print(traceback.format_exc())
                    return

            key = data['key'].split('.')[-1]
            print("Adding key:", key, " in Bucket:", cur_bucket, " type:", field_type)

            # Handling creation of Map type.
            if field_type.type == 'BUCKET':
                # Create a new Bucket and assign pk as value.
                # TODO: big issue: do not create new is existing for this Parent bucket.
                # # TODO: above has been implemeted but need rigorous testing.
                try:
                    bucket_field: BucketField = BucketField.objects.get(bucket=cur_bucket, key=key)
                    # This sub bucket already exists. Just get its pk
                    value = bucket_field.value
                except ObjectDoesNotExist:
                    # First time creating Sub Bucket with this map
                    new_bucket = Bucket(name=key, is_root=False)
                    new_bucket.save()
                    print("New BUCKET Created: ", new_bucket.pk)
                    value = new_bucket.pk

            # This is kind of useless in case of BUCKET and above 'except' is not performed.
            # TODO: find a work around to optimize.
            # update or create field in the database.
            bucket_field, created = BucketField.objects.update_or_create(
                key=key,
                bucket=cur_bucket,
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




    # Add an element to existing array.
    @staticmethod
    def add_array_element(bucket_consumer, json_event):
        if bucket_consumer.access.pk == 3:
            error_json = {
                "type": "error",
                "error": "User does not have WRITE Access"
            }
            # on error, send error message only to consumer that triggered the event
            bucket_consumer.send(text_data=json.dumps(error_json))
            return

        data = json_event.pop('data')
        cur_bucket = bucket_consumer.bucket

        field_type = FieldType.objects.get(pk=data['type'])
        if data['value']:
            value = data['value']
        else:
            # if 'value' missing, create an empty field
            value = ''

        # b1.b2....bn.arr
        if '.' in data['key']:
            try:
                for sub_b_name in data['key'].split('.')[:-1]:
                    # just to check if sub_b exists in the cur_bucket.
                    bf: BucketField = BucketField.objects.get(bucket=cur_bucket, key=sub_b_name)
                    # bf.value is the pk of the subbucket.
                    cur_bucket: Bucket = Bucket.objects.get(pk=bf.value)
            except ObjectDoesNotExist as e:
                print("Bucket hierarchy exception: ", sub_b_name, " not found!")
                print(traceback.format_exc())
                return
            except Exception as e:
                print("Unknown Exception: ", e)
                print(traceback.format_exc())
                return

        # NAME of the array that element is being added to.
        array_key = data['key'].split('.')[-1]
        bf = BucketField.objects.get(bucket=cur_bucket, key=array_key)

        # Not allowing adding Bucket or ARRAY as Array elements. Will get too complex.
        # TODO: Proper exception handling
        if field_type.type == 'BUCKET' or field_type.type == 'ARRAY':
            return
        try:
            print("creating array field")
            array_field: ArrayField = ArrayField.objects.create(
                parent_field=bf,
                value=value,
                type=field_type,
                index=0
            )

            final_json = Handler.create_snapshot(bucket=bucket_consumer.bucket)
            Handler.update(bucket_consumer, final_json)
        except Exception as e:
            print("Error Creating Array Field: ", e)
            print(traceback.format_exc())



    @staticmethod
    def remove_array_element(bucket_consumer, json_element):
        # TODO: implement, also handle reindexing for rest of the index greater than what is removed
        pass


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
        cur_bucket = bucket_consumer.bucket

        if '.' in data['key']:
            try:
                for sub_b_name in data['key'].split('.')[:-1]:
                    # just to check if sub_b exists in the cur_bucket.
                    bf: BucketField = BucketField.objects.get(bucket=cur_bucket, key=sub_b_name)
                    # bf.value is the pk of the subbucket.
                    cur_bucket: Bucket = Bucket.objects.get(pk=bf.value)
            except ObjectDoesNotExist as e:
                print("Bucket hierarchy exception: ", sub_b_name, " not found!")
                print(traceback.format_exc())
                return
            except Exception as e:
                print("Unknown Exception: ", e)
                print(traceback.format_exc())
                return

        key = data['key'].split('.')[-1]


        try:
            # Get the field mapping.
            bf: BucketField = BucketField.objects.get(bucket=cur_bucket, key=key)

            # If the field mapping to be deleted is a Bucket, delete its entry from Bucket table
            # This will trigger deletion of child fields.
            if bf.type.type == 'BUCKET':
                try:
                    Bucket.objects.get(pk=bf.value).delete()
                except ObjectDoesNotExist:
                    print("Sub Bucket to be deleted does not Exist in Bucket table")

            # Delete the field mapping irrespective of type
            # Important - DONOT Remove - Will break for sub buckets if removed.
            bf.delete()

            # Prepares a snapshot and sends to all the listeners in the group using the update()
            final_json = Handler.create_snapshot(bucket=bucket_consumer.bucket)
            Handler.update(bucket_consumer, final_json)
        except ObjectDoesNotExist as e:
            print("Field to be Deleted does not exist.", str(e))
        except Exception as e:
            # TODO: handle database error and notify consumer that triggered the event.
            print(e)

# mapping json_event types to handler methods.
# used by bucket_consumer class
event_map = {
    'add_field': Handler.add_field, # when new field is added.
    'update': Handler.update,   # unused for the moment. Not sure why we created this.
    'remove_field': Handler.remove_field, # when a field is deleted.
    'add_array_element': Handler.add_array_element
}