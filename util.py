BOT_PREFIX = '!'

def checkBotCommand(message,command):
    return message.content.startswith(BOT_PREFIX+command)
