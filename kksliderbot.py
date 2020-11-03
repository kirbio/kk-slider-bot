import discord
import const
import asyncio 
import sys

import youtubestreaming as yt
from util import *
from youtube_dl.utils import DownloadError

client = discord.Client()

current_voice_channel = None
current_status = None
song_queue = []
flg_stop = False
flg_loop = False

def parse_parameters(content):
    return content.strip().split()[1:]

#Join voice channel if it has not, otherwise do nothing.
async def joinVoiceChannel(message,currentdj):
    global current_voice_channel
    print('joining voice...')
    if current_voice_channel is None:
        if currentdj.voice is not None:
            current_voice_channel = await currentdj.voice.channel.connect()
            print('connected to vc')
            return True
        else:
            await message.channel.send('You are not connecting to VC right now.')
            return False
    else:
        print('already connected')
        return True

def songEndEvent(channel):
    global song_queue, flg_stop, flg_loop, client

    print('ending song...')
    # print(len(song_queue),flg_stop)

    asyncio.run_coroutine_threadsafe(client.change_presence(status=discord.Status.idle, activity=None), client.loop)

    if not flg_loop or flg_stop:
        if len(song_queue) > 0:
            curr_song = song_queue.pop(0)  
    else:
        print('looping...')

    #if manually called stop, stop advancing the queue, too.
    if flg_stop:
        flg_stop = False
        flg_loop = False
        return

    #if song queue is empty
    if not song_queue:
        return

    asyncio.run_coroutine_threadsafe(songStartEvent(channel), client.loop)

async def songStartEvent(channel):
    global song_queue, current_status, flg_loop

    print('starting song...')
    #if song queue is empty
    if not song_queue:
        await channel.send('Please queue up some songs first!')
        return

    song, dj = song_queue[0]
    if song['loop']:
        flg_loop = True

    async with channel.typing():
        player = await yt.YTDLSource.from_url(song['id'],stream=True)
        # print('playing: {} from {}'.format(player.title, dj))
        current_voice_channel.play(player, after=lambda e: songEndEvent(channel))
        await channel.send(formatNowPlaying(song['title'], song['duration'], dj, flg_loop))

    # set bot status
    current_status = discord.Game(name=song['title'])
    await client.change_presence(status=discord.Status.online, activity=current_status)
    
async def playEvent(channel, url, currentdj, loop=False):
    global song_queue
    try:
        print('queueing...')
        # player = await yt.YTDLSource.from_url(url,stream=True)
        # song_queue.append((player,currentdj))
        song_list = yt.extract_info(url)
        '''
        song keys : (['id', 'uploader', 'uploader_id', 'uploader_url', 'channel_id', 'channel_url', 'upload_date', 'license', 'creator', 'title', 'alt_title', 'thumbnails', 'description', 'categories', 'tags', 'subtitles', 'automatic_captions', 'duration', 'age_limit', 'annotations', 'chapters', 'webpage_url', 'view_count', 'like_count', 'dislike_count', 'average_rating', 'formats', 'is_live', 'start_time', 'end_time', 'series', 'season_number', 'episode_number', 'track', 'artist', 'album', 'release_date', 'release_year', 'extractor', 'webpage_url_basename', 'extractor_key', 'n_entries', 'playlist', 'playlist_id', 'playlist_title', 'playlist_uploader', 'playlist_uploader_id', 'playlist_index', 'thumbnail', 'display_id', 'requested_subtitles', 'format_id', 'url', 'player_url', 'ext', 'format_note', 'acodec', 'abr', 'container', 'asr', 'filesize', 'fps', 'height', 'tbr', 'width', 'vcodec', 'downloader_options', 'format', 'protocol', 'http_headers'])
        '''
        len_before = len(song_queue)
        for song in song_list:
            print('queued', song['title'], song['duration'])
            song['loop'] = loop
            song_queue.append((song, currentdj))

        if len_before == 0:          
            await songStartEvent(channel)
        else:
            await channel.send(formatQueueing(song['title'], song['duration'], currentdj, len(song_queue)-1, song['loop']))
    # except DownloadError:
        # await channel.send('Video not found or the player could not play this video')
    except:
        await channel.send('Unexpected Error : ' + sys.exc_info()[0].__name__)
        print(sys.exc_info()[0])

async def resumeEvent(channel):
    current_voice_channel.resume()
    await client.change_presence(status=discord.Status.online, activity=current_status)
    await channel.send(formatResponse('Resumed'))

@client.event
async def on_connect():
    #raidful.updateLocal()
    #client.loop.create_task(sync_db())
    print('Connected')


@client.event
async def on_disconnect():
    print('Disconnected')


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    global current_voice_channel, song_queue, flg_loop, flg_stop, current_status
    
    params = parse_parameters(message.content)
    channel = message.channel
    currentdj = message.author

    # bot message
    if message.author == client.user:
        return

    #If the message does not start with prefix, ignore
    if not message.content.startswith(BOT_PREFIX):
        return

    #If the caller is not in the same VC as the bot, unless an admin
    if not currentdj.voice is None:
        if not current_voice_channel is None:
            # print(currentdj.voice.channel)
            # print(current_voice_channel.channel)
            if currentdj.voice.channel != current_voice_channel.channel:
                await message.channel.send('You are not in the same VC with the bot.')
                return
    else:
        await message.channel.send('You are not connecting to VC right now.')
        return

    # COMMANDS

    if checkBotCommand(message,'grandad'):
        await channel.send(formatResponse('Fleentstones'))

    elif checkBotCommand(message,'play',HQRIP_COMMAND):
        #Return if not connected to VC
        if not await joinVoiceChannel(message,currentdj):
            return

        if len(params) == 0:
            if current_voice_channel.is_playing():
                await channel.send('Currently playing audio. Please use `stop` to stop current song or `skip` to start next song immediately')
            elif current_voice_channel.is_paused():
                await resumeEvent(channel)
            else:
                await songStartEvent(channel)
        else:
            url = ' '.join(params)
            if checkBotCommand(message,HQRIP_COMMAND):
                url += ' siivagunner'
            await playEvent(channel, url, currentdj.display_name)
        
                
    elif checkBotCommand(message, 'loop'):
        #Return if not connected to VC
        if not await joinVoiceChannel(message,currentdj):
            return

        if len(params) > 0: #loop <URL> - play <URL> with loop
            url = ' '.join(params)
            await playEvent(channel, url, currentdj.display_name, loop=True)
        else:
            flg_loop = not flg_loop
            await channel.send('Loop current song: {}'.format(flg_loop))
            print('flg_loop:',flg_loop)


    elif checkBotCommand(message, 'now', 'np', 'nowplaying'):
        if len(song_queue) > 0:
            song, dj = song_queue[0]
            await channel.send(formatNowPlaying(song['title'], song['duration'], dj, flg_loop))
        else:
            await channel.send('Currently not playing any song')

    elif checkBotCommand(message, 'link', 'info'):
        if len(song_queue) > 0:
            song, dj = song_queue[0]
            print(song)
            await channel.send(song['webpage_url'])
        else:
            await channel.send('Currently not playing any song')

    elif checkBotCommand(message, 'undo', 'dequeue', 'dq'):
        if len(song_queue) > 1:
            song_queue.pop()
            await channel.send('Removed last song in queue')
        else:
            await channel.send('No song in queue log')

    elif checkBotCommand(message, 'pop', 'remove'):
        if len(params) > 0:
            try:
                index = int(params[0])
            except ValueError:
                await channel.send('Invalid index')
                return

            if index < 1:
                await channel.send('Invalid index')
                return
            elif index > len(song_queue):
                index = -1
        else:
            index = -1

        if len(song_queue) > 1:
            song, dj = song_queue.pop(index)
            await channel.send('Removed {} from {}'.format(song['title'], dj))
        else:
            await channel.send('No song in queue log')


    elif checkBotCommand(message,'pause'):

        if current_voice_channel==None:
            await channel.send('Currently not connect to Voice Channel')
            return

        if current_voice_channel.is_paused():
            await channel.send('Currently already paused')
            return

        if not current_voice_channel.is_playing():
            await channel.send('Currently not playing any song')
            return
        
        current_voice_channel.pause()
        await client.change_presence(status=discord.Status.do_not_disturb, activity=current_status)
        await channel.send(formatResponse('Paused'))

    elif checkBotCommand(message,'resume'):
        
        if current_voice_channel==None:
            await channel.send('Currently not connect to Voice Channel')
            return

        if not current_voice_channel.is_paused():
            await channel.send('Currently not paused')
            return
        await resumeEvent(channel)

    elif checkBotCommand(message,'stop'):
        print('stopping...')
        if current_voice_channel==None:
            await channel.send('Currently not connect to Voice Channel')
            return
        
        flg_stop = True
        current_voice_channel.stop()
        await channel.send(formatResponse('Stopped'))

    elif checkBotCommand(message,'skip','sk'):
        print('skipping...')
        if current_voice_channel==None:
            await channel.send('Currently not connect to Voice Channel')
            return
        if flg_loop:
            flg_loop = False
        current_voice_channel.stop()
        await channel.send(formatResponse('Skipped'))

    elif checkBotCommand(message,'queue','q','list','ls'):
        
        if len(song_queue)==0:
            await channel.send("`The song queue is empty`")
            return
        
        await channel.send(formatQueueList(song_queue, current_voice_channel, flg_loop))

    elif checkBotCommand(message, 'clear', 'flush'):
        print('clearing...')
        if current_voice_channel==None:
            await channel.send('Currently not connect to Voice Channel.')
            return
        
        flg_stop = True

        async with channel.typing():
            current_voice_channel.stop()
            while len(song_queue) > 0:
                song_queue.pop()
        
        await channel.send(formatResponse('Cleared Queue'))

    elif checkBotCommand(message, 'help'):
        await channel.send('https://www.youtube.com/watch?v=yD2FSwTy2lw')
        
    elif checkBotCommand(message,'disconnect','dc'):
        if isAdminMessage(message):
            server = message.guild.voice_client
            await server.disconnect(force=True)
            current_voice_channel=None
            print('disconnected from vc')

    elif checkBotCommand(message,'logout'):
        if not isAdminMessage(message):
            await channel.send('This command can only be invoked by administrator.\nPlease call @Kirbio or @Sunny for help.')
        else:
            await client.logout()
            await client.close()

    # Simple test command to check if the bot is not dead
    elif checkBotCommand(message,'ping','ping2'):
        await channel.send(formatResponse('Pong'))

    elif checkBotCommand(message,'status'):
        if isAdminMessage(message):
            await channel.send('flg_loop'+ str(flg_loop))
            await channel.send('flg_stop'+ str(flg_stop))
            await channel.send('queue'+ str(len(song_queue)))
            await channel.send('is playing'+ str(current_voice_channel.is_playing()))
            await channel.send('is pause'+ str(current_voice_channel.is_paused()))

    else:
        print('unknown command')

client.run(const.BOT_TOKEN)
