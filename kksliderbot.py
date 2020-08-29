import discord
import const
import util
import youtubestreaming as yt

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

def check_queue():
    global song_queue

    #if song queue is empty
    if not song_queue:
        return

    #async with channel.typing():
        player = song_queue.pop(0)
        print('playing: {}'.format(player.title))
        #player.start()
        current_voice_channel.play(player, after=lambda e: check_queue())
    #return channel.send('Now playing: {}'.format(player.title))

async def playNextSongInQueue(channel):
    global song_queue

    #if song queue is empty
    if not song_queue:
        await channel.send('Please queue up some songs first!')
        return
    
    async with channel.typing():
        player = song_queue.pop(0)
        print('playing: {}'.format(player.title))
        current_voice_channel.play(player, after=lambda e: check_queue())

    await channel.send('Now playing: {}'.format(player.title))

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
    global current_voice_channel, song_queue
    
    # bot message
    if message.author == client.user:
        return

    #If the message does not start with prefix, ignore
    if not message.content.startswith(util.BOT_PREFIX):
        return

    params = parse_parameters(message.content)

    channel = message.channel

    if util.checkBotCommand(message,'grandad'):
        await channel.send('fleentstones')

    elif util.checkBotCommand(message,'play'):
        currentdj = message.author

        result = await joinVoiceChannel(message,currentdj)

        #Not connected to VC
        if not result:
            return

        await playNextSongInQueue(channel)

        
    elif util.checkBotCommand(message,'pause'):

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
        

    elif util.checkBotCommand(message,'resume'):
        
        if current_voice_channel==None:
            await channel.send('Currently not connect to Voice Channel.')
            return

        if not current_voice_channel.is_paused():
            await channel.send('Currently not paused.')
            return
        current_voice_channel.resume()
    elif util.checkBotCommand(message,'stop'):
        
        if current_voice_channel==None:
            await channel.send('Currently not connect to Voice Channel.')
            return

        current_voice_channel.stop()

    elif util.checkBotCommand(message,'queue'):
        
        if len(params)==0:
            result = "Song List\n```"
            for i in range(0,len(song_queue)):
                result = result+"\n"+str(i+1)+") "+song_queue[i].title
            if len(song_queue)==0:
                result = result+"The song queue is empty."
            result = result+"```"
            await channel.send(result)
            return
        
        url = params[0]
        player = await yt.YTDLSource.from_url(url,stream=True)
        song_queue.append(player)
        await channel.send('Queued :**'+player.title+"**")
        
        
    elif util.checkBotCommand(message,'disconnect','dc'):
        server = message.guild.voice_client
        await server.disconnect(force=True)
        current_voice_channel=None
        print ('disconnected from vc')

    elif util.checkBotCommand(message,'logout'):
        if False:#util.isAdminMessage(message):
            await channel.send('This command can only be invoked by administrator.\nPlease call @Kirbio or @Sunny for help.')
        else:
            await client.logout()

    # Simple test command to check if the bot is not dead
    elif util.checkBotCommand(message,'ping','ping2'):
        await channel.send('pong')


client.run(const.BOT_TOKEN)
