BOT_PREFIX = '!'

def checkBotCommand(message,*commands):
    result = False
    for command in commands:
        if message.content.startswith(BOT_PREFIX+command):
           result = True
           break
    return result

