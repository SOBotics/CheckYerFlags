import binascii
import gzip
import io
import json
import flagbot.html_parser as html_parser
from urllib.request import urlopen
from pyquery import PyQuery as pq


def checkOwnFlags(message, chat_helper):
    page = urlopen("https://stackoverflow.com/users/{}?tab=topactivity".format(message.user.id))
    html = page.read().decode("utf-8")
    jQuery = pq(html)
    flagCount = str(pq(jQuery(".g-col.g-row.fl-none").children()[6]).html()).replace('\n', ' ').replace('\r', '').strip().strip(" helpful flags")
    chat_helper.replyWith(message, "You have {} helpful flags. Ranks are coming soon, you can suggest levels [here](https://github.com/SOBotics/FlaggersHall/issues/11)!".format(flagCount));
    # message.message.reply("**This feature is not working yet!** You need [69] more helpful flags to get your next rank: **Burn the evil** (666 flags)") # original message, currently kept for historical reasons

def checkFlags(message, chat_helper):
    userId = ""
    try:
        userId = message.content.split('status ', 1)[1]
    except IndexError:
        pass

    validId = False
    if userId.isdecimal():
        # Now we call the Stack Exchange API to validate the user's id
        response = urlopen("https://api.stackexchange.com/2.2/users/{}?order=desc&sort=reputation&site=stackoverflow&key=K8pani4F)SeUn0QlbHQsbA((".format(userId)).read()
        buffer = io.BytesIO(response)
        gzipped_file = gzip.GzipFile(fileobj=buffer)
        content = gzipped_file.read()
        data = json.loads(content.decode("utf-8"))

        if len(data["items"]) is 1:
            validId = True
        if data['quota_remaining'] is not None:
            chat_helper.setQuota(data['quota_remaining']);
    else:
        chat_helper.postMessage("The specfied argument for the user id is not correct. Only digits are allowed.")
        return

    if validId:
        page = urlopen("https://stackoverflow.com/users/{}?tab=topactivity".format(message.content.split('status ', 1)[1]))
        html = page.read().decode("utf-8")
        jQuery = pq(html)
        flagCount = str(pq(jQuery(".g-col.g-row.fl-none").children()[6]).html()).replace('\n', ' ').replace('\r', '').strip().strip(" helpful flags")
        userName = str(pq(jQuery(".name")[0]).html()).replace('\n', ' ').replace('\r', '').strip()
        # Stripping mod markup from the name
        userName = html_parser.strip_tags(userName)
        chat_helper.postMessage("{} has {} helpful flags. Ranks are coming soon, you can suggest levels [here](https://github.com/SOBotics/FlaggersHall/issues/11)!".format(userName, flagCount))
    else:
        chat_helper.postMessage("The specfied user id does not belong to an existing user.")