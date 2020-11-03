import const

BOT_PREFIX = '!'
HQRIP_COMMAND = 'rip'

def checkBotCommand(message,*commands):
    for command in commands:
        if message.content.split()[0] == BOT_PREFIX+command:
           return True
    return False

def formatDuration(t):
    if type(t) == float:
        t = int(t)
    return '{}:{:02d}'.format(t//60,t%60)

def formatNumber(number):
    mapping = {0 : 'zero', 1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6:'six',7:'seven',8:'eight',9:'nine',10:'keycap_ten'}
    return mapping[number]

def formatNowPlaying(title, duration, dj, loop=False, header=True):
    result = ''
    if header:
        result += '**NOW PLAYING :**\n'
    looping = ':repeat:' if loop else ''
    result += ':loud_sound:{}  `{} ({})` from {}\n'.format(looping,title,formatDuration(duration),dj)
    return result

def formatQueueItem(title, duration, dj, number, loop=False):
    looping = ':repeat:' if loop else ''
    return ':{}:{}  `{} ({})` from {}\n'.format(formatNumber(number), looping, title, formatDuration(duration), dj)

def formatQueueing(title, duration, dj, number, loop=False):
    result = ''
    result += '**QUEUED :**\n'
    result += formatQueueItem(title, duration, dj, number, loop)
    return result
    
def formatResponse(text):
    return '**{}**'.format(text.upper())

def formatQueueList(song_queue, current_voice_channel, loop):

    result = '**QUEUE LIST**\n'
    if not current_voice_channel.is_paused() and not current_voice_channel.is_playing():
        for i,x in enumerate(song_queue):
            s,dj = x[0],x[1]
            result += formatQueueItem(s['title'], s['duration'], dj, i+1, s['loop'])
    else:
        s, dj = song_queue[0]
        result += formatNowPlaying(s['title'], s['duration'], dj, loop, header=False)
        if len(song_queue) > 1:
            for i,x in enumerate(song_queue[1:]):
                s,dj = x[0],x[1]
                result += formatQueueItem(s['title'], s['duration'], dj, i+1, s['loop'])
    return result

def isAdminMessage(message):
    return message.author.display_name in const.ADMIN_LIST