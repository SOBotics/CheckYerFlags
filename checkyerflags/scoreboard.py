import os.path
from firebase_admin import db
from checkyerflags.logger import auto_logger

def update_scoreboard(flag_count, user):
    """
    Call the scoreboard api to update the flag count for a user
    """

    #Check if service account key is provided, otherwise exits
    try:
        if not os.path.isfile("./service_account_key.json"):
            return

        #Only add users with 500 flags or more
        if flag_count <= 499:
            return

        existing_record = False
        doc_id = None

        #Set flag count
        ref = db.reference("/scores")
        ref.set({user.id: flag_count})

    except BaseException as e:
        auto_logger.error(e)
        auto_logger.error(f"Couldn't update scoreboard value for user {user.name}")