import discord
import const
import util

client = discord.Client()

prefix = '$'

current_voice_channel = None

def parse_parameters(content):
    return content.strip().lower().split()[1:]

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
    global current_voice_channel
    # bot message
    if message.author == client.user:
        return

    #If the message does not start with prefix, ignore
    if not message.content.startswith(util.BOT_PREFIX):
        return

    if util.checkBotCommand(message,'grandad'):
        await message.channel.send('fleentstones')

    elif util.checkBotCommand(message,'play'):
        currentdj = message.author

        if current_voice_channel is None:
            if currentdj.voice is not None:
                current_voice_channel = currentdj.voice.channel
                await current_voice_channel.connect()
                print('connected to vc')
            else:
                await message.channel.send('You are not connecting to VC right now.')
            
       
        
    elif util.checkBotCommand(message,'disconnect'):
        server = message.guild.voice_client
        await server.disconnect(force=True)
        current_voice_channel=None
        print ('disconnected from vc')

    elif util.checkBotCommand(message,'logout'):
        if False:#util.isAdminMessage(message):
            await message.channel.send('This command can only be invoked by administrator.\nPlease call @Kirbio or @Sunny for help.')
        else:
            await client.logout()

    # Simple test command to check if the bot is not dead
    elif util.checkBotCommand(message,'ping'):
        await message.channel.send('pong')


client.run(const.BOT_TOKEN)
