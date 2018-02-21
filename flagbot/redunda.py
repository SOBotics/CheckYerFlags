from threading import Thread
from urllib import parse, request
from time import localtime, strftime

import json
from urllib.error import URLError


class RedundaThread(Thread):
    def __init__(self, event, config, logging):
        Thread.__init__(self)
        self.stopped = event
        self.config = config
        self.logging = logging

    def run(self):
        while not self.stopped.wait(60):
            self.pingRedunda()

    def pingRedunda(self):
        try:
            data = parse.urlencode({"key": self.config["redundaKey"], "version": self.config["botVersion"]}).encode()
            req = request.Request("https://redunda.sobotics.org/status.json", data)

            response = request.urlopen(req)

            jsonReturned = json.loads(response.read().decode("utf-8"))
        except (OSError, URLError) as e:
            current_timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            self.logging.warn("Pinging Redunda failed at {} CET".format(current_timestamp))