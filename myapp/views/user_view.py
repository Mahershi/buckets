from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from ..models import User
from ..helpers.scripts import custom_response, error_response
from django.http.response import Http404
from rest_framework.request import Request
from rest_framework.decorators import action
from ..serializers import UserSerializer
from rest_framework.exceptions import ValidationError


class UserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, ]
    queryset = User.objects.all()

    def get_permissions(self):
        print(self.action)
        if self.action == 'create':
            self.permission_classes = [AllowAny, ]
        else:
            self.permission_classes = [IsAuthenticated, ]

        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        try:
            resp = super().create(request, *args, **kwargs)
            return custom_response(
                status=200,
                data=resp.data
            )
        except ValidationError as e:
            return error_response(
                status=400,
                error=e.detail
            )

    @action(methods=['GET'], detail=False)
    def get_profile(self, request: Request, *args, **kwargs):
        if request.user:
            serializer = UserSerializer(request.user, many=False)
            return custom_response(
                status=200,
                data=serializer.data
            )
        else:
            return error_response(
                status=403,
                error="Unauthenticated Request"
            )

    def retrieve(self, request, *args, **kwargs):
        # can only call app/user/<id> to retrieve if Authenticated User is a Super User.
        if request.user:
            if request.user.is_superuser:
                try:
                    resp = super().retrieve(request, args, **kwargs)
                    return custom_response(
                        200,
                        data=resp.data,
                    )
                except Http404 as e:
                    print(type(e))
                    return error_response(
                        status=404,
                        error="Does not Exist!"
                    )
            else:
                return error_response(status=403, error="Unauthenticated Request: User is not Super user")

    def list(self, request, *args, **kwargs):
        return error_response(
            status=404,
        )

    def destroy(self, request, *args, **kwargs):
        return error_response(
            status=404,
        )

