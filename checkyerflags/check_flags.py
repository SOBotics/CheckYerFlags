from urllib.error import HTTPError
from urllib.request import urlopen

from pyquery import PyQuery as pq

import checkyerflags.ranks as ranks
import checkyerflags.se_api as stackexchange_api
from checkyerflags.utils import Struct


def get_flag_count_for_user(user_id, utils):
    """
    Check the flags for the specified user
    """

    #Remove preceeding zeroes from the id, if there are any
    userId = int(str(user_id).lstrip("0"))

    if _user_id_valid(userId, utils):
        page = urlopen(f"https://stackoverflow.com/users/{userId}?tab=topactivity")
        html = page.read().decode("utf-8")
        jQuery = pq(html)
        flag_count = str(pq(pq(pq(jQuery(".grid--cell.mt-auto.fc-black-350.fs-caption.lh-sm .grid.gs4.fd-column").children()[1]).children()[0]).children()[1]).html()).replace(',', '').strip().strip(" helpful flags")
        if flag_count.isdecimal():
            return int(flag_count)
        raise ValueError(f"Value '{flag_count}' can not be converted to a number")
    else:
        if utils is not None:
            raise NonExistentUserIdError

def get_current_flag_rank(flag_count):
    """
    Get the current flag rank for the specified amount of flags
    """

    #Calculate differences between rank flag count and current flag count
    differences = []
    for rank in ranks.ranks:
        differences.append(flag_count - rank["count"])

    #Get all posivite rank differences (IOW not yet reached)
    positive_differences = []
    for difference in differences:
        if difference >= 0:
            positive_differences.append(difference)

    if len(positive_differences) <= 0:
        raise NotEnoughFlagsError

    return ranks.ranks[differences.index(min(positive_differences))]

def get_next_flag_rank(current_rank = None):
    """
    Get the next flag rank for the specified rank
    """

    current_rank_index = -1

    if current_rank is None:
        return ranks.ranks[0]

    if type(current_rank) is Struct:
        current_rank_index = next((index for (index, d) in enumerate(ranks.ranks) if d["count"] == current_rank.count), None)
    else:
        current_rank_index = ranks.ranks.index(current_rank)

    return ranks.ranks[current_rank_index + 1]

def get_flags_to_next_rank(_flag_count):
    flag_count = int(_flag_count.replace(",", ""))
    current_flag_rank = get_current_flag_rank(flag_count)
    next_flag_rank = Struct(**get_next_flag_rank(current_flag_rank))
    return next_flag_rank.count - int(flag_count)


def _user_id_valid(user_id, utils):
    """
    Validate the specified ID using the Stack Exchange API
    """
    user_id = str(user_id)

    if user_id.isdecimal():
        # Now we call the Stack Exchange API to validate the user's id
        if utils is not None and utils.config is not None and utils.config.stackExchangeApiKey is not None:
            stack_exchange_api_key = utils.config.stackExchangeApiKey
        else:
            raise NoApiKeyError

        se_api = stackexchange_api.se_api(stack_exchange_api_key)
        data = Struct(**se_api.get_user(user_id))

        if data is None or len(data.items) is 0:
            raise NonExistentUserIdError
        if len(data.items) is 1:
            return True
    else:
        raise InvalidUserIdError

def get_user_name(user_id, utils):
    """
    Get the display name from the ID using the Stack Exchange API
    """

    if user_id.isdecimal():
        # Now we call the Stack Exchange API to validate the user's id
        if utils is not None and utils.config is not None and utils.config.stackExchangeApiKey is not None:
            stack_exchange_api_key = utils.config.stackExchangeApiKey
        else:
            raise NoApiKeyError

        try:
            se_api = stackexchange_api.se_api(stack_exchange_api_key)
            data = Struct(**se_api.get_user(user_id))
        except HTTPError:
            raise NonExistentUserIdError

        if len(data.items) is 1 and data.items[0]["display_name"] is not None:
            return data.items[0]["display_name"]
    else:
        raise InvalidUserIdError


class InvalidUserIdError(Exception):
    pass
class NonExistentUserIdError(Exception):
    pass
class NotEnoughFlagsError(Exception):
    pass
class NoApiKeyError(Exception):
    pass