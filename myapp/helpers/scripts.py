from rest_framework.response import Response


def custom_response(status, success: bool = True, data={}):
    return Response(
        status=status,
        data={
            "success": success,
            "data": data,
        }
    )


def error_response(status, success: bool = False, error='', detail=''):
    return Response(
        status=status,
        data={
            "success": success,
            'error': error,
            'detail': detail
        }
    )
