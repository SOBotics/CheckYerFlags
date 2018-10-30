debug_config = {
    "botOwner": "<YOUR_NAME>", # The person which is responsible for running the instance (Your SE/SO chat username, so the bot and other people know whom to ping
    "botMachine": "<YOUR_MACHINE_NAME>", # The system the bot runs on (example: EC2).
    "room": 1, # The ID for the chatroom we work with
    "chatHost": "stackoverflow.com", # The site where the bot runs. The underlying library isn't designed to operate on any chat site except chat.stackoverflow.com
    "email": "", # The credentials to log in to an account which posts the messages
    "password": "",
    "stackExchangeApiKey": "K8pani4F)SeUn0QlbHQsbA((", # We shouldn't run out of quota, as they key usages are IP based. Required.
    "score_board_fkey": "" # Not required, key for the SOBotics scoreboard.
}

prod_config = {
    "botOwner": "<YOUR_NAME>",
    "botMachine": "<YOUR_MACHINE_NAME>",
    "room": 1,
    "chatHost": "stackoverflow.com",
    "email": "",
    "password": "",
    "stackExchangeApiKey": "K8pani4F)SeUn0QlbHQsbA((",
    "redundaKey": "", # Not required, key for Redunda. This is not in the debug config since it does make little sense to ping Redunda while developing
    "score_board_fkey": ""
}