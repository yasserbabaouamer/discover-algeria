from rest_framework.exceptions import APIException


class CustomException(APIException):
    def __init__(self, detail, status):
        super().__init__(detail, 'error')
        self.status_code = status
