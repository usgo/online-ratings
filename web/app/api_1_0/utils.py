from app.api_1_0.api_exception import ApiException
from flask import request

def requires_json(f):
    def wrapped(*args, **kwargs):
        if not "application/json" in request.headers.get('Content-Type', ''):
            raise ApiException(status_code=415)
        return f(*args, **kwargs)
    return wrapped