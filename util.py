import const

BOT_PREFIX = '!'
HQRIP_COMMAND = 'rip'

def checkBotCommand(message,*commands):
    result = False
    for command in commands:
        if message.content.startswith(BOT_PREFIX+command):
           result = True
           break
    return result

def formatDuration(t):
    return '{}:{:02d}'.format(t//60,t%60)

def formatNowPlaying(title, duration, dj):
    result = ''
    result += '**NOW PLAYING :**\n'
    result += ':loud_sound:  `{} ({})` from {}\n'.format(title,formatDuration(duration),dj)
    return result

def formatQueueing(title, duration, dj):
    result = ''
    result += '**QUEUE ADDED :**\n'
    result += ':play_pause:  `{} ({})` from {}\n'.format(title,formatDuration(duration),dj)
    return result

def formatQueueItem(title, duration, dj):
    return ':notes:  `{} ({})` from {}\n'.format(title, formatDuration(duration), dj)
    
def formatResponse(text):
    return '**{}**'.format(text.upper())

def formatQueueList(song_queue, current_voice_channel):

    result = ''
    if not current_voice_channel.is_paused() and not current_voice_channel.is_playing():
        result += '**NEXT SONGS IN QUEUE :**\n'
        for s,dj in song_queue:
            result += formatQueueItem(s.title, s.data['duration'], dj)
    else:
        s, dj = song_queue[0]
        result += formatNowPlaying(s.title, s.data['duration'], dj)
        if len(song_queue) > 1:
            result += '\n'
            result += '**NEXT SONGS IN QUEUE :**\n'
            for s,dj in song_queue[1:]:
                result += formatQueueItem(s.title, s.data['duration'], dj)

    return result

def isAdminMessage(message):
    return message.author.display_name in const.ADMIN_LIST