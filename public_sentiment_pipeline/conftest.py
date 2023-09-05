"""Contains useful properties for the unit tests"""


class FakeGet:
    def __init__(self) -> None:
        self.status_code = 200

    def json(self):
        return {"success": True}


class FakePost:
    def __init__(self) -> None:
        self.status_code = 200

    def json(self):
        return {"success": True, "access_token": "this is an access token"}
