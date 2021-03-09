import getopt

mapping = {0 : 'zero', 
           1: 'one', 
           2: 'two', 
           3: 'three', 
           4: 'four', 
           5: 'five', 
           6:'six',
           7:'seven',
           8:'eight',
           9:'nine',
           10:'keycap_ten'}

def formatDuration(t):
    if type(t) == float:
        t = int(t)
    return '{}:{:02d}'.format(t//60,t%60)

def formatNumber(number):
    return mapping[number] if number in mapping else 'asterisk'

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

def formatQueueList(song_queue, current_voice_channel):

    result = '**QUEUE LIST**\n'
    if not current_voice_channel.is_paused() and not current_voice_channel.is_playing():
        for i,s in enumerate(song_queue):
            result += formatQueueItem(s['title'], s['duration'], s['dj'], i+1, s['loop'])
    else:
        s = song_queue[0]
        result += formatNowPlaying(s['title'], s['duration'], s['dj'], s['loop'], header=False)
        if len(song_queue) > 1:
            for i,s in enumerate(song_queue[1:]):
                result += formatQueueItem(s['title'], s['duration'], s['dj'], i+1, s['loop'])
    return result[:2000]

def parse_arguments(args):
    optlist, args = getopt.gnu_getopt(args, 's:r')
    for k,v in optlist:
        if k == '-s':
            assert 0.5 <= float(v) <= 2.0, 'Speed must be between 0.5 and 2.0'
    return optlist, args