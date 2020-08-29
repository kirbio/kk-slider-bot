BOT_PREFIX = '!'

def checkBotCommand(message,*commands):
    result = False
    for command in commands:
        if message.content.startswith(BOT_PREFIX+command):
           result = True
           break
    return result

def formatNowPlaying(title, dj):
    result = ''
    result += '**NOW PLAYING :**\n'
    result += ':loud_sound:  `{}` from {}\n'.format(title,dj)
    return result

def formatQueueing(title, dj):
    result = ''
    result += '**QUEUE ADDED :**\n'
    result += ':play_pause:  `{}` from {}\n'.format(title,dj)
    return result
    

def formatQueueList(song_queue, current_voice_channel):

    result = ''
    if not current_voice_channel.is_paused() and not current_voice_channel.is_playing():
        result += '**NEXT SONGS IN QUEUE :**\n'
        for s,dj in song_queue:
            result += ':notes:  `{}` from {}\n'.format(s.title, dj)
    else:
        s, dj = song_queue[0]
        result += formatNowPlaying(s.title, dj)
        if len(song_queue) > 1:
            result += '\n'
            result += '**NEXT SONGS IN QUEUE :**\n'
            for s,dj in song_queue[1:]:
                result += ':notes:  `{}` from {}\n'.format(s.title, dj)

    return result