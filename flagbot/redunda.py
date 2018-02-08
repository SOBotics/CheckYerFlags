from urllib import parse, request

import json
import time


def pingRedunda(bot_version):
    data = parse.urlencode({"key": "19b558436329ff6eb8247bc21fdd2aaa1135597b5bb858a10e8eef2688b8565e", "version": bot_version}).encode()
    req = request.Request("https://redunda.sobotics.org/status.json", data)

    response = request.urlopen(req)

    jsonReturned = json.loads(response.read().decode("utf-8"))

def continousPing(bot_version):
    while True:
        pingRedunda(bot_version)
        time.sleep(60)