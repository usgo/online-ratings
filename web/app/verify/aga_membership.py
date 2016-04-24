from logging import getLogger
import os
import requests

LOG = getLogger('aga_membership')
MEMBERSHIP_API_URL = "https://usgo.org/mm/api/members"
MEMBERSHIP_API_KEY = os.environ.get("AGA_MM_API_KEY", "")

def get_email_address(aga_id):
    url = os.path.join(MEMBERSHIP_API_URL, str(aga_id))
    try:
        response = requests.get(url, params={"api_key": MEMBERSHIP_API_KEY})
        if not response.json()['success']:
            LOG.error("API call didn't succeed: %s", response.json())
            return None
        return response.json()['payload']['row']['email']
    except ValueError:
        LOG.exception("Couldn't interpret response as json: %s", response.content)
    except KeyError:
        LOG.exception("Got unexpected json format %s", response.json())
    except Exception:
        LOG.exception("Unknown error")
    return None
