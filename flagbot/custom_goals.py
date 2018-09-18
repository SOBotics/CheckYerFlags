import csv

def add_custom_goal(user_id, flag_count, overwrite):
    custom_goal_current = get_custom_goal_for_user(user_id)
    if custom_goal_current is not None and not overwrite:
        return False, custom_goal_current

    if overwrite:
        delete_custom_goal(user_id)

    with open("custom_goals.csv", "a") as f:
        f.write(f"{user_id};{flag_count}\n")
        return True, None

def get_custom_goal_for_user(user_id):
    custom_goals = []

    with open("custom_goals.csv") as f:
        csv_reader = csv.reader(f, delimiter=";")
        for row in csv_reader:
            custom_goals.append((row[0] , row[1]))

    for rank in custom_goals:
        if int(rank[0]) == user_id:
            return rank[1]

    return None

def delete_custom_goal(user_id):
    rows = []

    with open("custom_goals.csv", "r") as f:
        data_rows = csv.reader(f, delimiter=";")
        for row in data_rows:
            rows.append(row)
        f.close()

    if rows is None:
        return False

    with open("custom_goals.csv", "w") as f:
        for row in rows:
            if int(row[0]) != user_id:
                f.write(f"{row[0]};{row[1]}\n")
        return True