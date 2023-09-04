"""Contains useful properties for the unit tests"""


class FakeRequest:
    def __init__(self) -> None:
        self.status_code = 200

    def json(self):
        return {"success": True}
