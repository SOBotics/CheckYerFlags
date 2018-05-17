"""
Class for interacting with the Stack Exchange API
"""
import gzip
import io
import json
import logging
import urllib.error
from urllib.request import urlopen


class se_api:
    def __init__(self, se_api_key):
        self.api_key = se_api_key

    def get_user(self, user_id):
        try:
            response = urlopen("https://api.stackexchange.com/2.2/users/{}?order=desc&sort=reputation&site=stackoverflow&key={}".format(user_id, self.api_key)).read()
            buffer = io.BytesIO(response)
            gzipped_file = gzip.GzipFile(fileobj=buffer)
            content = gzipped_file.read()
            return json.loads(content.decode("utf-8"))
        except urllib.error.HTTPError as e:
            logging.error("Error calling the SE API: Got repsonse code {} and message {}.".format(e.code, e.reason))
            return None