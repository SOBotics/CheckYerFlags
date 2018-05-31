import flagbot.ranks as ranks
import flagbot.se_api as stackexchange_api
from urllib.request import urlopen
from pyquery import PyQuery as pq


def check_own_flags(message, utils):
    page = urlopen("https://stackoverflow.com/users/{}?tab=topactivity".format(message.user.id))
    html = page.read().decode("utf-8")
    jQuery = pq(html)
    flag_count = str(pq(jQuery(".g-col.g-row.fl-none").children()[6]).html()).replace('\n', ' ').replace('\r', '').strip().strip(" helpful flags")
    try:
        current_flag_rank = get_current_flag_rank(int(flag_count.replace(",", "")))
        next_flag_rank = get_next_flag_rank(current_flag_rank)
        flag_count_difference = next_flag_rank["count"] - int(flag_count.replace(",", ""))
    except ValueError as e:
        if str(e) is "NEF":
            utils.post_message("You have {} helpful flags. Appears that you are not flagging that much.".format(flag_count))
        return
    utils.reply_with(message, "You have {} helpful flags. Your last achieved rank was **{}** ({}) for {} helpful flags. You need {} more flags for your next rank, *{}*.".format(flag_count, current_flag_rank["title"], current_flag_rank["description"], current_flag_rank["count"], flag_count_difference, next_flag_rank["title"]))

def check_own_flags_next_rank(message, utils):
    page = urlopen("https://stackoverflow.com/users/{}?tab=topactivity".format(message.user.id))
    html = page.read().decode("utf-8")
    jQuery = pq(html)
    flag_count = str(pq(jQuery(".g-col.g-row.fl-none").children()[6]).html()).replace('\n', ' ').replace('\r', '').strip().strip(" helpful flags")
    try:
        current_flag_rank = get_current_flag_rank(int(flag_count.replace(",", "")))
        next_flag_rank = get_next_flag_rank(current_flag_rank)
        flag_count_difference = next_flag_rank["count"] - int(flag_count.replace(",", ""))
    except ValueError as e:
        if str(e) is "NEF":
            utils.post_message("You need {} more flags to get your first flag rank, **{}** ({} flags in total).".format(ranks.ranks[0]["count"] - int(flag_count.replace(",", "")), ranks.ranks[0]["title"], ranks.ranks[0]["count"]))
        return
    utils.reply_with(message, "You need {} more flags to get your next flag rank, **{}** ({} flags in total).".format(flag_count_difference, next_flag_rank["title"], next_flag_rank["count"]))

def check_flags(message, utils, config = None, user_id = 0, verbose = True):
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
                utils.post_message("API quota rolled over at {}".format(utils.quota))

            utils.quota = data['quota_remaining']
    else:
        utils.post_message("The specfied argument for the user id is not correct. Only digits are allowed.")
        return
    #endregion

    if validId:
        page = urlopen("https://stackoverflow.com/users/{}?tab=topactivity".format(userId))
        html = page.read().decode("utf-8")
        jQuery = pq(html)
        flag_count = str(pq(jQuery(".g-col.g-row.fl-none").children()[6]).html()).replace('\n', ' ').replace('\r', '').strip().strip(" helpful flags")

        try:
            current_flag_rank = get_current_flag_rank(int(flag_count.replace(",", "")))
            next_flag_rank = get_next_flag_rank(current_flag_rank)
        except ValueError as e:
            if str(e) is "NEF":
                if verbose:
                    utils.post_message("{} has {} helpful flags. Appears that they're not flagging so much".format(user_name, flag_count))
                else:
                    return { "flag_count": int(flag_count.replace(",", "")), "next_rank": ranks.ranks[0] }
            return
        if verbose:
            utils.post_message("{} has {} helpful flags. Their last achieved rank was **{}** ({}) for {} helpful flags.".format(user_name, flag_count, current_flag_rank["title"], current_flag_rank["description"], current_flag_rank["count"]))
        else:
            return { "flag_count": int(flag_count.replace(",", "")), "next_rank": next_flag_rank, "current_rank": current_flag_rank }
    else:
        if utils is not None:
            utils.post_message("The specfied user id does not belong to an existing user.")

def get_current_flag_rank(flag_count):
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
    current_rank_index = ranks.ranks.index(current_rank)

    return  ranks.ranks[current_rank_index + 1]
