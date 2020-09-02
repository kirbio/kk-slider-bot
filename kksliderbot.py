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

def parse_parameters(content):
    return content.strip().split()[1:]

#Join voice channel if it has not, otherwise do nothing.
async def joinVoiceChannel(message,currentdj):
    global current_voice_channel
    if current_voice_channel is None:
        if currentdj.voice is not None:
            current_voice_channel = await currentdj.voice.channel.connect()
            print('connected to vc')
            return True
        else:
            await message.channel.send('You are not connecting to VC right now.')
            return False
    return True

def songEndEvent(channel):
    global song_queue, flg_stop, client

    print('ending song...')
    print(len(song_queue),flg_stop)
    if len(song_queue) > 0:
        song_queue.pop(0)

    asyncio.run_coroutine_threadsafe(client.change_presence(status=discord.Status.idle, activity=None), client.loop)

    #if manually called stop, stop advancing the queue, too.
    if flg_stop:
        flg_stop = False
        return

    #if song queue is empty
    if not song_queue:
        return

    asyncio.run_coroutine_threadsafe(songStartEvent(channel), client.loop)
    # player, dj = song_queue[0]
    # print('playing: {} from {}'.format(player.title, dj))
    # current_voice_channel.play(player, after=lambda e: check_queue())
    #return channel.send('Now playing: {}'.format(player.title))
        

async def songStartEvent(channel):
    global song_queue, current_status

    print('starting song...')
    #if song queue is empty
    if not song_queue:
        await channel.send('Please queue up some songs first!')
        return
    

    async with channel.typing():
        player, dj = song_queue[0]
        print('playing: {} from {}'.format(player.title, dj))
        current_voice_channel.play(player, after=lambda e: songEndEvent(channel))
    
    await channel.send(formatNowPlaying(player.title, player.data['duration'], dj))

    # set bot status
    current_status = discord.Game(name=player.title)
    await client.change_presence(status=discord.Status.online, activity=current_status)
    

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
    global current_voice_channel, song_queue, flg_stop, current_status
    
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
            else:
                await songStartEvent(channel)
        else:
            url = ' '.join(params)
            if checkBotCommand(message,HQRIP_COMMAND):
                url += ' siivagunner'
        
            try:
                print('queueing...')
                player = await yt.YTDLSource.from_url(url,stream=True)
                song_queue.append((player,currentdj.display_name))
                
                if len(song_queue) <= 1:          
                    await songStartEvent(channel)
                else:
                    await channel.send(formatQueueing(player.title, player.data['duration'], currentdj.display_name, len(song_queue)-1))
            except DownloadError:
                await channel.send('Video not found or the player could not play this video')
            except:
                await channel.send('Unexpected Errror : ' + sys.exc_info()[0].__name__)
    
    elif checkBotCommand(message, 'now', 'np', 'nowplaying'):
        if len(song_queue) > 0:
            player, dj = song_queue[0]
            await channel.send(formatNowPlaying(player.title, player.data['duration'], dj))
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
            player, dj = song_queue.pop(index)
            await channel.send('Removed {} from {}'.format(player.title, dj))
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
        current_voice_channel.resume()
        await client.change_presence(status=discord.Status.online, activity=current_status)
        await channel.send(formatResponse('Resumed'))


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
        
        current_voice_channel.stop()
        await channel.send(formatResponse('Skipped'))

    elif checkBotCommand(message,'queue','q','list','ls'):
        
        if len(song_queue)==0:
            await channel.send("`The song queue is empty`")
            return
        
        await channel.send(formatQueueList(song_queue, current_voice_channel))

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
            await channel.send('flg_stop'+ str(flg_stop))
            await channel.send('queue'+ str(len(song_queue)))
            await channel.send('is playing'+ str(current_voice_channel.is_playing()))
            await channel.send('is pause'+ str(current_voice_channel.is_paused()))

client.run(const.BOT_TOKEN)
