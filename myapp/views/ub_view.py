from ..models import Bucket, UserBucket, User, Access
from ..serializers import BucketSerializer, UBSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..helpers.scripts import custom_response, error_response
from rest_framework.decorators import action
from rest_framework.request import Request
from django.core.exceptions import ObjectDoesNotExist


class UBView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = UBSerializer
    queryset = UserBucket.objects.all()

    def list(self, request, *args, **kwargs):
        if request.user:
            self.queryset = self.queryset.filter(user__exact=request.user)
            serializer = UBSerializer(self.queryset, many=True)

            return custom_response(
                status=200,
                data=serializer.data
            )
        else:
            return error_response(
                status=403,
                error="Unauthorized Request"
            )

    @action(methods=['GET'], detail=False)
    def bucket(self, request: Request, *args, **kwargs):
        if request.user:
            if request.query_params.get('bucket_id'):
                try:
                    bucket = Bucket.objects.get(pk=request.query_params.get('bucket_id'))
                    self.queryset = self.queryset.filter(user__exact=request.user, bucket__exact=bucket)

                    if len(self.queryset) == 0:
                        return error_response(
                            status=401,
                            error="Unauthorized Access: User does not have access to this bucket"
                        )
                    else:
                        ub = self.queryset[0]
                        serializer = UBSerializer(ub, many=False)
                        return custom_response(
                            status=200,
                            data=serializer.data
                        )
                except ObjectDoesNotExist:
                    return error_response(
                        status=404,
                        error="Bucket does not exist"
                    )
            else:
                return error_response(
                    status=400,
                    error="Bucket Id not provided"
                )
        else:
            return error_response(
                status=401,
                error="User not Authenticated"
            )