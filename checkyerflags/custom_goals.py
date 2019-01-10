from firebase_admin import db

def add_custom_goal(user_id, flag_count, custom_message):
    #Set flag count
    custom_ranks = db.reference("/custom_ranks")
    custom_ranks.child(str(user_id)).set({'flag_count': flag_count, 'custom_message': custom_message})
    return True

def get_custom_goal_for_user(user_id):
    custom_ranks = db.reference("/custom_ranks")
    return custom_ranks.child(str(user_id)).get()

def delete_custom_goal(user_id):
    custom_ranks = db.reference("/custom_ranks")
    cr = custom_ranks.get()

    #Remove user
    ranks = dict(cr)
    try:
        del ranks[str(user_id)]
    except KeyError:
        return False

    custom_ranks.set(ranks)
    return True