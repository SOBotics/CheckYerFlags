import firebase_admin
import os.path
from firebase_admin import credentials
from firebase_admin import firestore

from checkyerflags.logger import auto_logger

def update_scoreboard(flag_count, user):
    """
    Call the scoreboard api to update the flag count for a user
    """

    #Check if service account key is provided, otherwise exits
    try:
        if not os.path.isfile("./service_account_key.json"):
            pass

        #Initialize Firestore
        cred = credentials.Certificate("./service_account_key.json")
        firebase_admin.initialize_app(cred, {
            'projectId': u"rankoverflow-56959",
        })
        db = firestore.client()

        existing_record = False
        doc_id = None

        # Skip if flag count is unchanged
        docs = db.collection(u"scores").get()
        for doc in docs:
            db_data = doc.to_dict()
            print(f"{user.id} == {db_data['user_id']}")
            if user.id == db_data['user_id']:
                existing_record = True
                print(f"found existing recond for {user.id}")
                if flag_count == db_data['flag_count']:
                    print("flag count unchanged")
                    return
                else:
                    print("flag count changed")
                    doc_id = doc.id
                    break

        # Update record
        print(existing_record)
        if existing_record:
            db.collection(u"scores").document(doc_id).update({u"user_id": user.id, u"flag_count": flag_count})
        # Add new record
        elif not existing_record:
            db.collection(u"scores").add({u"user_id": user.id, u"flag_count": flag_count})

    except BaseException as e:
        auto_logger.error(e)
        auto_logger.error(f"Couldn't update scoreboard value for user {user.name}")