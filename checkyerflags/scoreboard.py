import os.path
from firebase_admin import db
from checkyerflags.logger import auto_logger

def update_scoreboard(flag_count, user):
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