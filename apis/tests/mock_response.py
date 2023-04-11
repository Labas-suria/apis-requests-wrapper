from requests.exceptions import JSONDecodeError


class MockResponse:
    """Class responsible for simulating a response to request.get method"""

    def __init__(self, data, status_code, reason=""):
        self.data = data
        self.status_code = status_code
        self.reason = reason

    def json(self):
        if self.data == "Non JSON response":
            raise JSONDecodeError("JSON Error", "json.json", 1)
        else:
            return self.data

    def content(self):
        return bytes(self.data, 'utf-8')
