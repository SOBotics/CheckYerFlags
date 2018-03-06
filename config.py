"""
Is this file are the configurations for debug and production mode defined. In the debug config is also explained for what the properties are for
"""

debugConfig = {
    "botParent": "chade_", # The person which is responsible for running the instance (e.g. you if you're running your own instance)
    "botMachine": "HP Envy (dev machine)", # The machine the bot runs on. Try to give it something easy to identify (I use the manufacturer and model name of my machine for development, and the distribution name for the productive server)
    "botVersion": "v0.8.0", # The current version of the Bot, be sure to read the wiki on how to increment the version
    "room": 163468, # The ID for the chatroom we work with.
    "chatHost": "stackoverflow.com", # The site where the bot runs. Please note that the bot has only been tested in rooms on stackoverflow.com
    "email": "", # The credentials to log in a user which posts the messages.
    "password": "", # WARNING: DO NOT COMMIT YOUR CHANGES IF YOUR CREDENTIALS ARE STILL IN HERE
    "stackExchangeApiKey": "K8pani4F)SeUn0QlbHQsbA((", # If you want to run the bot productively on your own, you may request a API key for yourself.
    "redundaKey": "19b558436329ff6eb8247bc21fdd2aaa1135597b5bb858a10e8eef2688b8565e" # If you want to have a key on your own, ping me so I so we can discuss the situation (because I may need to add you as collaborator in order to create a key that show the bot of with you as the owner)
}

prodConfig = {
    "botParent": "chade_", # The person which is responsible for running the instance (e.g. you if you're running your own instance)
    "botMachine": "UbuntuServer", # The machine the bot runs on. Try to give it something easy to identify (I use the manufacturer and model name of my machine for development, and the distribution name for the productive server)
    "botVersion": "v0.8.0", # The current version of the Bot, be sure to read the wiki on how to increment the version
    "room": 111347,
    "chatHost": "stackoverflow.com", # The site where the bot runs. Please note that the bot has only been tested in rooms on stackoverflow.com
    "email": "", # The credentials to log in a user which posts the messages.
    "password": "", # WARNING: DO NOT COMMIT YOUR CHANGES IF YOUR CREDENTIALS ARE STILL IN HERE
    "stackExchangeApiKey": "K8pani4F)SeUn0QlbHQsbA((", # If you want to run the bot productively on your own, you may request a API key for yourself.
    "redundaKey": "1edfa96cf4edac49271759220c029a35c21fddda3e1fb28d82ec6bcba6dd6c7a" # If you want to have a key on your own, ping me so I so we can discuss the situation (because I may need to add you as collaborator in order to create a key that show the bot of with you as the owner)
}