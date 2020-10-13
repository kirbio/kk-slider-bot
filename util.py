import const

BOT_PREFIX = '!'
HQRIP_COMMAND = 'rip'

def checkBotCommand(message,*commands):
    for command in commands:
        if message.content.split()[0] == BOT_PREFIX+command:
           return True
    return False

def formatDuration(t):
    return '{}:{:02d}'.format(t//60,t%60)

def formatNumber(number):
    mapping = {0 : 'zero', 1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6:'six',7:'seven',8:'eight',9:'nine',10:'keycap_ten'}
    return mapping[number]

def formatNowPlaying(title, duration, dj, loop=False):
    result = ''
    result += '**NOW PLAYING :**\n'
    icon = 'repeat' if loop else 'loud_sound'
    result += ':{}:  `{} ({})` from {}\n'.format(icon,title,formatDuration(duration),dj)
    return result

def formatQueueing(title, duration, dj, number):
    result = ''
    result += '**QUEUED :**\n'
    result += ':{}:  `{} ({})` from {}\n'.format(formatNumber(number),title,formatDuration(duration),dj)
    return result

def formatQueueItem(title, duration, dj, number):
    return ':{}:  `{} ({})` from {}\n'.format(formatNumber(number), title, formatDuration(duration), dj)
    
def formatResponse(text):
    return '**{}**'.format(text.upper())

def formatQueueList(song_queue, current_voice_channel, loop):

    result = ''
    if not current_voice_channel.is_paused() and not current_voice_channel.is_playing():
        result += '**NEXT SONGS IN QUEUE :**\n'
        for i,x in enumerate(song_queue):
            s,dj = x[0],x[1]
            result += formatQueueItem(s['title'], s['duration'], dj, i+1)
    else:
        s, dj = song_queue[0]
        result += formatNowPlaying(s['title'], s['duration'], dj, loop)
        if len(song_queue) > 1:
            result += '\n'
            result += '**NEXT SONGS IN QUEUE :**\n'
            for i,x in enumerate(song_queue[1:]):
                s,dj = x[0],x[1]
                result += formatQueueItem(s['title'], s['duration'], dj, i+1)

    return result

def isAdminMessage(message):
    return message.author.display_name in const.ADMIN_LIST