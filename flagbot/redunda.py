"""Background process for pinging Redunda"""

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
        """
        Start the one minute interval
        """
        self.ping_redunda()
        while not self.stopped.wait(60):
            self.ping_redunda()

    def ping_redunda(self):
        """
        Ping the Redunda API
        """
        try:
            if self.config["redundaKey"] is not "":
                data = parse.urlencode({"key": self.config["redundaKey"], "version": self.config["botVersion"]}).encode()
                req = request.Request("https://redunda.sobotics.org/status.json", data)

                response = request.urlopen(req)

                json.loads(response.read().decode("utf-8"))
            else:
                self.logging.warning("No Redunda key specified. Disabling Redunda pinging.")
                self.stopped.set()
            return True
        except (OSError, URLError) as e:
            current_timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            if self.logging is not None:
                self.logging.warning(f"Pinging Redunda failed at {current_timestamp} UTC")
            return False