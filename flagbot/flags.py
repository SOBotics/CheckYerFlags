import flagbot.ranks as ranks
import flagbot.se_api as stackexchange_api
from urllib.request import urlopen
from pyquery import PyQuery as pq


def check_own_flags(message, utils):
    """
    Check the flags of the user who posted the message
    """
    page = urlopen(f"https://stackoverflow.com/users/{message.user.id}?tab=topactivity")
    html = page.read().decode("utf-8")
    jQuery = pq(html)
    flag_count = str(pq(jQuery(".g-col.g-row.fl-none").children()[6]).html()).replace('\n', ' ').replace('\r', '').strip().strip(" helpful flags")
    try:
        current_flag_rank = get_current_flag_rank(int(flag_count.replace(",", "")))
        next_flag_rank = get_next_flag_rank(current_flag_rank)
        flag_count_difference = next_flag_rank["count"] - int(flag_count.replace(",", ""))
    except ValueError as e:
        if str(e) is "NEF":
            message.reply_to(f"You have {flag_count} helpful flags. Appears that you are not flagging that much.")
        return
    message.reply_to(f"You have {flag_count} helpful flags. Your last achieved rank was **{current_flag_rank['title']}** ({current_flag_rank['description']}) for {current_flag_rank['count']} helpful flags. You need {flag_count_difference} more flags for your next rank, *{next_flag_rank['title']}*.")

def check_own_flags_next_rank(message, utils):
    """
    Get the next rank for the user who posted the message
    """
    page = urlopen(f"https://stackoverflow.com/users/{message.user.id}?tab=topactivity")
    html = page.read().decode("utf-8")
    jQuery = pq(html)
    flag_count = str(pq(jQuery(".g-col.g-row.fl-none").children()[6]).html()).replace('\n', ' ').replace('\r', '').strip().strip(" helpful flags")
    try:
        current_flag_rank = get_current_flag_rank(int(flag_count.replace(",", "")))
        next_flag_rank = get_next_flag_rank(current_flag_rank)
        flag_count_difference = next_flag_rank["count"] - int(flag_count.replace(",", ""))
    except ValueError as e:
        if str(e) is "NEF":
            utils.post_message(f"You need {ranks.ranks[0]['count'] - int(flag_count.replace(',', ''))} more flags to get your first flag rank, **{ranks.ranks[0]['title']}** ({ranks.ranks[0]['count']} flags in total).")
        return
    message.reply_to(f"You need {flag_count_difference} more flags to get your next flag rank, **{ next_flag_rank['title']}** ({next_flag_rank['count']} flags in total).")

def check_flags(message, utils, config = None, user_id = 0, verbose = True):
    """
    Check the flags for the specified user
    """
    userId = ""
    user_name = ""
    if user_id == 0:
        try:
            userId = message.content.replace(' s ', ' status ').split('status ', 1)[1]
        except IndexError:
            pass
    else:
        userId = str(user_id)

    #Remove preceeding zeroes from the id, if there are any
    userId = userId.lstrip("0")

    #region Validate the specified ID using the Stack Exchange API
    validId = False
    if userId.isdecimal():
        # Now we call the Stack Exchange API to validate the user's id
        if utils is not None and utils.config is not None and utils.config["stackExchangeApiKey"] is not None:
            stack_exchange_api_key = utils.config["stackExchangeApiKey"]
        else:
            stack_exchange_api_key = config["stackExchangeApiKey"]

        se_api = stackexchange_api.se_api(stack_exchange_api_key)
        data = se_api.get_user(userId)

        if data is None:
            utils.post_message("The specfied user id does not belong to an existing user.")
            return
        if len(data["items"]) is 1:
            validId = True
            user_name = data["items"][0]["display_name"]
        if data['quota_remaining'] is not None and utils is not None:
            if data['quota_remaining'] >= utils.quota:
                utils.post_message(f"API quota rolled over at {utils.quota} remaining requests")

            utils.quota = data['quota_remaining']
    else:
        utils.post_message("The specfied argument for the user id is not correct. Only digits are allowed.")
        return
    #endregion

    if validId:
        page = urlopen(f"https://stackoverflow.com/users/{userId}?tab=topactivity")
        html = page.read().decode("utf-8")
        jQuery = pq(html)
        flag_count = str(pq(jQuery(".g-col.g-row.fl-none").children()[6]).html()).replace('\n', ' ').replace('\r', '').strip().strip(" helpful flags")

        try:
            current_flag_rank = get_current_flag_rank(int(flag_count.replace(",", "")))
            next_flag_rank = get_next_flag_rank(current_flag_rank)
        except ValueError as e:
            if str(e) is "NEF":
                if verbose:
                    utils.post_message(f"{user_name} has {flag_count} helpful flags. Appears that they're not flagging so much")
                else:
                    return { "flag_count": int(flag_count.replace(",", "")), "next_rank": ranks.ranks[0] }
            return
        if verbose:
            utils.post_message(f"{user_name} has {flag_count} helpful flags. Their last achieved rank was **{current_flag_rank['title']}** ({current_flag_rank['description']}) for {current_flag_rank['count']} helpful flags.")
        else:
            return { "flag_count": int(flag_count.replace(",", "")), "next_rank": next_flag_rank, "current_rank": current_flag_rank }
    else:
        if utils is not None:
            utils.post_message("The specfied user id does not belong to an existing user.")

def get_current_flag_rank(flag_count):
    """
    Get the current flag rank for the specified amount of flags
    """
    differences = []
    for rank in ranks.ranks:
        differences.append(flag_count - rank["count"])

    positive_differences = []
    for difference in differences:
        if difference >= 0:
            positive_differences.append(difference)

    if len(positive_differences) <= 0:
        raise ValueError("NEF")

    return ranks.ranks[differences.index(min(positive_differences))]

def get_next_flag_rank(current_rank):
    """
    Get the next flag rank for the specified rank
    """
    current_rank_index = ranks.ranks.index(current_rank)

    return  ranks.ranks[current_rank_index + 1]
