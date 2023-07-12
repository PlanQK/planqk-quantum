import json

from requests import Response


class PlanqkError(Exception):
    def __init__(self, *message):
        super().__init__(' '.join(message))
        self.message = ' '.join(message)

    def __str__(self):
        return repr(self.message)


class PlanqkClientError(Exception):
    def __init__(self, response: Response):
        super().__init__(response)
        self.response = response

    def __str__(self):
        error_json = json.loads(self.response.text) if self.response.text else None
        error_msg = error_json['error_message'] if error_json is not None else None
        status = error_json['status'] if error_json is not None else None
        status_code = self.response.status_code
        return f'{error_msg} (HTTP error: {status})' if error_msg is not None else f'HTTP error code: {status_code}'


class CredentialUnavailableError(PlanqkError):
    pass


class InvalidAccessTokenError(PlanqkError):
    def __init__(self, value="Invalid personal access token provided."):
        self.value = value
        super().__init__(self.value)

    pass
