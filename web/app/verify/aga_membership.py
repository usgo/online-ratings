import os
import requests
from urllib.parse import urlunparse, urlencode, ParseResult

MEMBERSHIP_API_FQDN = "usgo.org"
MEMBERSHIP_API_ROOT = "/mm/api/members/"
MEMBERSHIP_API_KEY = os.environ.get("AGA_MM_API_KEY", "")
EMAIL_FIELD_NAME = "email"

def get_email_address(aga_id):
    url = urlunparse(ParseResult(
        scheme="https",
        netloc=MEMBERSHIP_API_FQDN,
        path=os.path.join(MEMBERSHIP_API_ROOT, str(aga_id)),
        params="",
        query=urlencode({"api_key": MEMBERSHIP_API_KEY}),
        fragment=""))
    response = requests.get(url)
    try:
        if not response.json()['success']:
            return None
        return response.json()['payload']['row']['email']
    except IndexError:
        return None
