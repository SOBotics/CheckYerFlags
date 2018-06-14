"""
Class for interacting with the Stack Exchange API
"""
import gzip
import io
import json
import urllib.error
from urllib.request import urlopen
from flagbot.logger import main_logger


class se_api:
    def __init__(self, se_api_key):
        self.api_key = se_api_key

    def get_user(self, user_id):
        """
        Get an user object for the specified user id from the API
        """
        try:
            response = urlopen(f"https://api.stackexchange.com/2.2/users/{user_id}?order=desc&sort=reputation&site=stackoverflow&key={self.api_key}").read()
            buffer = io.BytesIO(response)
            gzipped_file = gzip.GzipFile(fileobj=buffer)
            content = gzipped_file.read()
            return json.loads(content.decode("utf-8"))
        except urllib.error.HTTPError as e:
            main_logger.error(f"Error calling the SE API: Got repsonse code {e.code} and message {e.reason}.")
            return None