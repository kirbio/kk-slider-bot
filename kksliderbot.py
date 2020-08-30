import discord
import const
import asyncio 

import youtubestreaming as yt
from util import *
from youtube_dl.utils import DownloadError

client = discord.Client()

prefix = '$'

current_voice_channel = None

song_queue = []

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

flg_stop = False

def songEndEvent(channel):
    global song_queue, flg_stop, client

    print('ending song...')
    print(len(song_queue),flg_stop)
    song_queue.pop(0)

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
    global song_queue

    print('starting song...')
    #if song queue is empty
    if not song_queue:
        await channel.send('Please queue up some songs first!')
        return
    

    async with channel.typing():
        player, dj = song_queue[0]
        print('playing: {} from {}'.format(player.title, dj))
        current_voice_channel.play(player, after=lambda e: songEndEvent(channel))
        # current_voice_channel.play(player)
    
    await channel.send(formatNowPlaying(player.title, dj))
    

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
    global current_voice_channel, song_queue, flg_stop
    
    # bot message
    if message.author == client.user:
        return

    #If the message does not start with prefix, ignore
    if not message.content.startswith(BOT_PREFIX):
        return

    params = parse_parameters(message.content)

    channel = message.channel

    if checkBotCommand(message,'grandad'):
        await channel.send('fleentstones')

    elif checkBotCommand(message,'play'):
        currentdj = message.author

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
        
            try:
                print('queueing...')
                player = await yt.YTDLSource.from_url(url,stream=True)
                song_queue.append((player,currentdj.display_name))

                if len(song_queue) <= 1:          
                    await songStartEvent(channel)
                else:
                    await channel.send(formatQueueing(player.title, currentdj.display_name))
            except:
                await channel.send('Video not found or the player could not play this video')
        
            
        
    elif checkBotCommand(message,'pause'):

        if current_voice_channel==None:
            await channel.send('Currently not connect to Voice Channel.')
            return

        if current_voice_channel.is_paused():
            await channel.send('Currently already paused.')
            return

        if not current_voice_channel.is_playing():
            await channel.send('Currently not playing any audio.')
            return
        
        current_voice_channel.pause()
        

    elif checkBotCommand(message,'resume'):
        
        if current_voice_channel==None:
            await channel.send('Currently not connect to Voice Channel.')
            return

        if not current_voice_channel.is_paused():
            await channel.send('Currently not paused.')
            return
        current_voice_channel.resume()
    elif checkBotCommand(message,'stop'):
        print('stopping...')
        if current_voice_channel==None:
            await channel.send('Currently not connect to Voice Channel.')
            return
        
        flg_stop = True
        current_voice_channel.stop()
    elif checkBotCommand(message,'skip'):
        print('skipping...')
        if current_voice_channel==None:
            await channel.send('Currently not connect to Voice Channel.')
            return
        
        current_voice_channel.stop()
        

    elif checkBotCommand(message,'queue'):

        if len(song_queue)==0:
            result = "`The song queue is empty`"
        else:
            result = formatQueueList(song_queue, current_voice_channel)
        
        await channel.send(result)
        
    elif checkBotCommand(message,'disconnect','dc'):
        server = message.guild.voice_client
        await server.disconnect(force=True)
        current_voice_channel=None
        print ('disconnected from vc')

    elif checkBotCommand(message,'logout'):
        if False:#isAdminMessage(message):
            await channel.send('This command can only be invoked by administrator.\nPlease call @Kirbio or @Sunny for help.')
        else:
            await client.logout()

    # Simple test command to check if the bot is not dead
    elif checkBotCommand(message,'ping','ping2'):
        await channel.send('pong')

    elif checkBotCommand(message,'status'):
        await channel.send('flg_stop'+ str(flg_stop))
        await channel.send('queue'+ str(len(song_queue)))
        await channel.send('is playing'+ str(current_voice_channel.is_playing()))
        await channel.send('is pause'+ str(current_voice_channel.is_paused()))

client.run(const.BOT_TOKEN)
