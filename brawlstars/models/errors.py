class ClientError(Exception):
    """
    Raised when a request with the BrawlStars API had failed.
    
    Attribute
    ---------
    status: The response status.
    reason: The reason for the error.
    message: The error message.
    type: ...
    detail: ...
    """
    def __init__(self, response_status:int, data:dict) -> None:
        self.status = response_status
        reason = data.get("reason")
        message = data.get("message")
        self.type = data.get("type", "")
        self.detail = data.get("detail", "")
        super().__init__(f"{self.status} {reason}: {message}")


class BadRequest(ClientError):
    """
    Client provided incorrect parameters for the request.
    Status code 400.

    Inherits from `ClientError`.
    """

    pass


class Forbidden(ClientError):
    """
    Access denied, either because of missing/incorrect
    credentials or used API token does not grant
    access to the requested resource.
    Status code 403.

    Inherits from `ClientError`.
    """

    pass


class NotFound(ClientError):
    """
    Resource was not found.
    Status code 404.

    Inherits from `ClientError`.
    """

    pass


class TooManyRequests(ClientError):
    """
    Request was throttled, because amount of requests was above the threshold defined for the used API token.
    Status code 429.

    Inherits from `ClientError`.
    """

    pass


class BrawlStarsServerError(ClientError):
    """
    Errors at server side.
    Status code 500, 503.
    Inherits from `ClientError`.
    """

    pass
