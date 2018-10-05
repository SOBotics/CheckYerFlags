import requests
from requests import HTTPError

from checkyerflags.logger import auto_logger

def update_scoreboard(flag_count, score_board_fkey, user):
    """
    Call the scoreboard api to update the flag count for a user
    """

    if flag_count >= 500 and score_board_fkey != "":
        try:
            r = requests.post("https://rankoverflow.philnet.ch/api/scoreboard/add", json={"fkey": score_board_fkey, "user_id": user.id, "flag_count": flag_count})
            if r.status_code != 200:
                auto_logger.warn(f"Couldn't update scoreboard value for user {user.name}")
        except HTTPError:
            auto_logger.warn(f"Couldn't update scoreboard value for user {user.name}")