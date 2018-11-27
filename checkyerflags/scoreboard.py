import os.path
from checkyerflags.logger import auto_logger

def update_scoreboard(flag_count, user, fb):
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

        # Skip if flag count is unchanged
        docs = fb.collection(u"scores").get()
        for doc in docs:
            fb_data = doc.to_dict()
            if user.id == fb_data['user_id']:
                existing_record = True
                if flag_count == fb_data['flag_count']:
                    return
                else:
                    doc_id = doc.id
                    break

        # Update record
        if existing_record:
            fb.collection(u"scores").document(doc_id).update({u"user_id": user.id, u"flag_count": flag_count})
        # Add new record
        elif not existing_record:
            fb.collection(u"scores").add({u"user_id": user.id, u"flag_count": flag_count})

    except BaseException as e:
        auto_logger.error(e)
        auto_logger.error(f"Couldn't update scoreboard value for user {user.name}")