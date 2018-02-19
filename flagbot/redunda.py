from threading import Thread
from urllib import parse, request
from time import localtime, strftime

import json
from urllib.error import URLError


class RedundaThread(Thread):
    def __init__(self, event, bot_version, logging):
        Thread.__init__(self)
        self.stopped = event
        self.bot_version = bot_version
        self.logging = logging

    def run(self):
        while not self.stopped.wait(60):
            self.pingRedunda()

    def pingRedunda(self):
        try:
            data = parse.urlencode({"key": "19b558436329ff6eb8247bc21fdd2aaa1135597b5bb858a10e8eef2688b8565e", "version": self.bot_version}).encode()
            req = request.Request("https://redunda.sobotics.org/status.json", data)

            response = request.urlopen(req)

            jsonReturned = json.loads(response.read().decode("utf-8"))
        except (OSError, URLError) as e:
            current_timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            self.logging.warn("Pinging Redunda failed at {} CET", current_timestamp)