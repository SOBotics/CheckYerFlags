import csv
import os


def add_custom_goal(user_id, flag_count, custom_message):
    delete_custom_goal(user_id)

    with open("custom_goals.csv", "a") as f:
        f.write(f"{user_id};{flag_count};{custom_message}\n")
        return True, None

def get_custom_goal_for_user(user_id):
    custom_goals = []

    if not os.path.exists("custom_goals.csv"):
        file = open("custom_goals.csv", "w+")
        file.close()

    with open("custom_goals.csv") as f:
        csv_reader = csv.reader(f, delimiter=";")
        for row in csv_reader:
            msg = None
            try:
                msg = row[2]
            except IndexError:
                pass

            custom_goals.append((row[0], row[1], msg))

    for rank in custom_goals:
        if int(rank[0]) == user_id:
            if int(rank[1]) <= -1:
                delete_custom_goal(user_id)
            else:
                return int(rank[1]), str(rank[2])

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