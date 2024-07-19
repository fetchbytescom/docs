import requests
import time
import os
import logging
import pprint

log = logging.getLogger(__name__)

API_URL = os.environ.get("FETCHBYTES_API_URL", "https://api.fetchbytes.com/")
API_KEY = os.environ.get("FETCHBYTES_API_KEY", "this_password_will_fail")


def fetch_bytes(method, *, json=True, raise_for_status=True, **kwargs):
    start = time.time()
    res = requests.post(API_URL + method + "?key=" + API_KEY, json=kwargs)
    log.debug(f"API call <{method}> took {time.time() - start:.2f} seconds.")
    if res.status_code != 200:
        log.error("Error %s: %s", res.status_code, res.text)
    if raise_for_status:
        res.raise_for_status()
    if json:
        log.debug("API Response: \n%s", pprint.pformat(res.json()))
        return res.json()
    log.debug("API Response: \n%s", res.content[0:1000])
    return res.content
