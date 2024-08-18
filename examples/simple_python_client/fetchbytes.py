import time
import os
import logging
import pprint
import base64
import requests

log = logging.getLogger(__name__)

API_URL = os.environ.get("FETCHBYTES_API_URL", "https://api.fetchbytes.com/")
API_KEY = os.environ.get("FETCHBYTES_API_KEY", "this_password_will_fail")


def fetch_bytes(method, *, json=True, raise_for_status=True, **kwargs):
    """
    Simple wrapper around requests.post to call the FetchBytes API.
    Parameters:
    - method: API method to call
    - json: parse response as JSON
    - raise_for_status: raise exception for non-200 status codes
    - **kwargs: parameters to pass to the API

    Example:
    fetch_bytes("navigate", url="https://bot.sannysoft.com/", content=True)
    """
    start = time.time()
    res = requests.post(API_URL + method + "?key=" + API_KEY, json=kwargs)
    log.debug(f"API call <{method}> took {time.time() - start:.2f} seconds.")
    if res.status_code != 200:
        log.error("Error %s: %s", res.status_code, res.text)

    if json and res.status_code == 200:
        result = res.json()
        if "debugLog" in result:
            print("Debug Log:")
            for line in result["debugLog"]:
                print(line)
            del result["debugLog"]
            print("=" * 80)
        if "actions" in result:
            for action_result in result["actions"]:
                if "debugScreenshot" in action_result:
                    with open(
                        "screenshot_%s_%s.png" % (time.time(), action_result["action"]),
                        "wb",
                    ) as out:
                        # decode base64 screenshot
                        buf = base64.b64decode(action_result["debugScreenshot"])
                        out.write(buf)
                    del action_result["debugScreenshot"]
        if "debugScreenshot" in result:
            with open("screenshot_%s.png" % time.time(), "wb") as out:
                buf = base64.b64decode(result["debugScreenshot"])
                out.write(buf)
            del result["debugScreenshot"]
        log.debug("API Response: \n%s", pprint.pformat(result))
        ret = res.json()
    else:
        log.debug("API Response: \n%s", res.content[0:255])
        ret = res.content

    if raise_for_status:
        res.raise_for_status()

    log.debug("API Response: \n%s", res.content[0:1000])
    return res.content
