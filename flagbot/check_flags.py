
import gzip
import io
import json
import flagbot.ranks as ranks
import flagbot.html_parser as html_parser
from urllib.request import urlopen
from pyquery import PyQuery as pq


def checkOwnFlags(message, utils):
    page = urlopen("https://stackoverflow.com/users/{}?tab=topactivity".format(message.user.id))
    html = page.read().decode("utf-8")
    jQuery = pq(html)
    flagCount = str(pq(jQuery(".g-col.g-row.fl-none").children()[6]).html()).replace('\n', ' ').replace('\r', '').strip().strip(" helpful flags")
    currentFlagRank = getCurrentFlagRank(int(flagCount.replace(",", "")))
    utils.replyWith(message, "You have {} helpful flags. Your last achieved rank was **{}** ({}) for {} helpful flags.".format(flagCount, currentFlagRank["title"], currentFlagRank["description"], currentFlagRank["count"]))
    # message.message.reply("**This feature is not working yet!** You need [69] more helpful flags to get your next rank: **Burn the evil** (666 flags)") # original message, currently kept for historical reasons

def checkFlags(message, utils):
    userId = ""
    try:
        userId = message.content.split('status ', 1)[1]
    except IndexError:
        pass

    #region Validate the specified ID using the Stack Exchange API
    validId = False
    if userId.isdecimal():
        # Now we call the Stack Exchange API to validate the user's id
        response = urlopen("https://api.stackexchange.com/2.2/users/{}?order=desc&sort=reputation&site=stackoverflow&key={}".format(userId, utils.config["stackExchangeApiKey"])).read()
        buffer = io.BytesIO(response)
        gzipped_file = gzip.GzipFile(fileobj=buffer)
        content = gzipped_file.read()
        data = json.loads(content.decode("utf-8"))

        if len(data["items"]) is 1:
            validId = True
        if data['quota_remaining'] is not None:
            utils.quota = data['quota_remaining']
    else:
        utils.postMessage("The specfied argument for the user id is not correct. Only digits are allowed.")
        return
    #endregion

    if validId:
        page = urlopen("https://stackoverflow.com/users/{}?tab=topactivity".format(message.content.split('status ', 1)[1]))
        html = page.read().decode("utf-8")
        jQuery = pq(html)
        flagCount = str(pq(jQuery(".g-col.g-row.fl-none").children()[6]).html()).replace('\n', ' ').replace('\r', '').strip().strip(" helpful flags")
        # Stripping mod markup from the name
        userName = str(pq(jQuery(".name")[0]).html()).replace('\n', ' ').replace('\r', '').strip()
        userName = html_parser.strip_tags(userName)
        try:
            currentFlagRank = getCurrentFlagRank(int(flagCount.replace(",", "")))
        except ValueError as e:
            if str(e) is "NEF":
                utils.postMessage("{} has {} helpful flags. They don't have enough helpful flags for a rank yet.".format(userName, flagCount))
            return
        utils.postMessage("{} has {} helpful flags. Their last achieved rank was **{}** ({}) for {} helpful flags.".format(userName, flagCount, currentFlagRank["title"], currentFlagRank["description"], currentFlagRank["count"]))
    else:
        utils.postMessage("The specfied user id does not belong to an existing user.")

def getCurrentFlagRank(flagCount):
    differences = []
    for rank in ranks.ranks:
        differences.append(flagCount - rank["count"])

    positive_differences = []
    for difference in differences:
        if difference > 0:
            positive_differences.append(difference)

    if len(positive_differences) <= 0:
        raise ValueError("NEF")


    return ranks.ranks[differences.index(min(positive_differences))]
