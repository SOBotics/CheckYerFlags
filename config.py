"""
Is this file are the configurations for debug and production mode defined. In the debug config is also explained for what the properties are for
"""

debug_config = {
    "botParent": "chade_", # The person which is responsible for running the instance (e.g. you if you're running your own instance)
    "botMachine": "PurePlastic (dev)", # The machine the bot runs on.
    "botVersion": "v0.9.0", # The current version of the Bot, be sure to read the wiki on how to increment the version
    "room": 163468, # The ID for the chatroom we work with
    "chatHost": "stackoverflow.com", # The site where the bot runs. Please note that the bot has only been tested in rooms on stackoverflow.com
    "email": "", # The credentials to log in a user which posts the messages
    "password": "", # IMPORTANT: DO NOT COMMIT YOUR CHANGES IF YOUR CREDENTIALS ARE STILL IN HERE
    "stackExchangeApiKey": "K8pani4F)SeUn0QlbHQsbA((", # If you want to run the bot productively on your own, you may request a API key for yourself (directly from StackApps, not from me).
    "redundaKey": "19b558436329ff6eb8247bc21fdd2aaa1135597b5bb858a10e8eef2688b8565e" # Just clear this value if you want to run your own instance. If you think you really need a key on your own, we can discuss it
}

prod_config = {
    "botParent": "chade_",
    "botMachine": "UbuntuServer",
    "botVersion": "v0.9.0",
    "rooms": 111347,
    "chatHost": "stackoverflow.com",
    "email": "",
    "password": "",
    "stackExchangeApiKey": "",
    "redundaKey": ""
}