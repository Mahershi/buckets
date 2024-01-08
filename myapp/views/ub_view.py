from ..models import Bucket, UserBucket, User, Access
from ..serializers import BucketSerializer, UBSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..helpers.scripts import custom_response, error_response


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