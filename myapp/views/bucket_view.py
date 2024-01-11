from ..models import Bucket, UserBucket, User, Access
from ..serializers import BucketSerializer, UBSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..helpers.scripts import custom_response, error_response
from rest_framework.request import Request
from django.core.exceptions import ObjectDoesNotExist


class BucketView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = BucketSerializer
    queryset = Bucket.objects.all()


    def list(self, request, *args, **kwargs):
        return error_response(
            status=404
        )

    def create(self, request: Request, *args, **kwargs):
        if request.user:
            try:
                name = request.data['name']
                bucket: Bucket = Bucket(name=name)
                bucket.save()

                # access.pk = 1 for Owner
                access = Access.objects.get(pk=1)
                ub = UserBucket(bucket=bucket, user=request.user, access=access)
                ub.save()

                serializer = BucketSerializer(bucket, many=False)

                return custom_response(
                    status=200,
                    data=serializer.data
                )
            except KeyError as e:
                return error_response(
                    status=400,
                    error="Bucket Name not provided"
                )
            except ObjectDoesNotExist as e:
                return error_response(
                    status=500,
                    error="Internal ObjectDoesNotExist Error"
                )
        else:
            # Not really useful as there already is default exception handling for this one.
            return error_response(
                status=403,
                error="Unauthenticated Request"
            )
