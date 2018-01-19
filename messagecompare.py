def compareMessage(message, command):
    if "@cyf " + command in message or "@cf " + command in message or "@CheckYerFlags " + command in message or "cyf " + command in message or "cf " + command in message:
        return True
    else:
        return False