from uuid import uuid4


class UUIDTokenGenerator():
    def __init__(self):
        pass

    def create(self):
        return str(uuid4())
