debug_config = {
    "botParent": "<YOUR_NAME>", # The person which is responsible for running the instance (at best your SE/SO username, so people know whom to ping)
    "botMachine": "<YOUR_MACHINE_NAME>", # The system the bot runs on (example: UbuntuServer).
    "botVersion": "v1.3.0", # The current version of the Bot, be sure to read the wiki on how to increment the version
    "room": 1, # The ID for the chatroom we work with
    "chatHost": "stackoverflow.com", # The site where the bot runs. The underlying library isn't designed to operate on any chat site except chat.stackoverflow.com
    "email": "", # The credentials to log in a user which posts the messages
    "password": "",
    "stackExchangeApiKey": "K8pani4F)SeUn0QlbHQsbA((", # We shouldn't run out of quota, as they key usages are IP based.
    "redundaKey": "", # Not required, key for Redunda.
    "score_board_fkey": "" # Not required, key for the SOBotics scoreboard.
}

prod_config = {
    "botParent": "<YOUR_NAME>",
    "botMachine": "<YOUR_MACHINE_NAME>",
    "botVersion": "v1.3.0",
    "room": 1,
    "chatHost": "stackoverflow.com",
    "email": "",
    "password": "",
    "stackExchangeApiKey": "K8pani4F)SeUn0QlbHQsbA((",
    "redundaKey": "",
    "score_board_fkey": ""
}