from rest_framework.response import Response

from core import logger


class Resp:
    """
    Template response for utility and helper functions/methods.
    """
    error: str = None
    message: str = None
    data: any = None
    status_code: int = None

    def __init__(self, error: str = None, message: str = None, data: any = None, status_code: int = 200) -> None:
        logger.info(f"Initializing method response.")
        self.error = error
        self.message = message
        self.data = data
        self.status_code = status_code

    def to_json(self) -> dict:
        resp = {
            "error": self.error,
            "message": self.message,
            "data": self.data
        }

        return resp

    def to_response(self) -> Response:
        resp = Response(
            self.to_json(),
            status=self.status_code
        )

        return resp
