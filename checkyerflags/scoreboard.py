import os.path
from firebase_admin import db
from checkyerflags.logger import auto_logger
from urllib import parse, request
import json
from urllib.error import URLError
from urllib3 import PoolManager, disable_warnings, exceptions

def update_scoreboard(flag_count, user):
    try:
        disable_warnings(exceptions.InsecureRequestWarning)
        data = json.dumps({"fkey": "", "id": user.id, "flags": flag_count})
        http = PoolManager()
        r = http.request('POST', "https://rankoverflow.philnet.ch/api/scoreboard/store", headers={'Content-Type': 'application/json'}, body=data)

        dump = r.read()
    except (OSError, URLError) as e:
        return

def update_scoreboard_legacy(flag_count, user):
    """
    Call the scoreboard api to update the flag count for a user
    """

    #Check if service account key is provided, otherwise return
    try:
        if not os.path.isfile("./service_account_key.json"):
            return

        #Only add users with 500 flags or more
        if flag_count <= 499:
            return

        #Set flag count
        scores = db.reference("/scores")
        scores.child(str(user.id)).set(flag_count)

    except BaseException as e:
        auto_logger.error(e)
        auto_logger.error(f"Couldn't update scoreboard value for user {user.name}")