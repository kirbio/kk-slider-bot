import discord
import const
import sys
import traceback
import asyncio
import youtubestreaming as yt
from youtube_dl.utils import DownloadError
from discord.ext.commands.errors import CommandInvokeError
from discord import Status, Game, FFmpegPCMAudio


from util import *
from events import *


# client = discord.Client()

current_voice_channel = None
current_status = None
song_queue = []
flg_stop = False
flg_loop = False

from discord.ext import commands
from discord.ext.commands import Bot, Context
from discord.voice_client import VoiceClient

bot = commands.Bot(command_prefix='!')


def is_admin(ctx):
    return ctx.author.display_name in const.ADMIN_LIST

def is_in_same_vc(ctx):
    if ctx.voice_client: # if bot has joined VC
        if ctx.author.voice and ctx.author.voice.channel == ctx.voice_client.channel:
            return True
    else:
        return True
    return False

@bot.event
async def on_connect():
    # raidful.updateLocal()
    # client.loop.create_task(sync_db())
    print('Connected')


@bot.event
async def on_disconnect():
    print('Disconnected')


@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('You have to be in the same VC as the bot.')
    else:
        print(error)

@bot.command()
async def ping(ctx: Context):
    await ctx.send("Pong")


@bot.command(name='dc')
@commands.check(is_admin)
async def disconnect(ctx: Context):
    await bot.change_presence(status=discord.Status.offline, activity=None)
    if bot.voice_clients:
        await bot.voice_clients[0].disconnect()
    await bot.logout()

@bot.command(aliases=['q', 'ls', 'list'])
async def queue(ctx: Context):
    if len(song_queue) == 0:
        await ctx.send("`The song queue is empty`")
    else:
        await ctx.send(formatQueueList(song_queue, ctx.voice_client))

@bot.command(aliases=['p'])
@commands.check(is_in_same_vc)
async def play(ctx: Context, *args):
    if len(args) == 0:
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
        elif ctx.voice_client.is_playing():
            await ctx.send('Already playing an audio')
        else:
            await songStartEvent(ctx, song_queue)
    else:
        url = ' '.join(args)
        await play_song(ctx, url, song_queue)

@bot.command()
@commands.check(is_in_same_vc)
async def stop(ctx: Context):
    global flg_stop
    flg_stop = True
    ctx.voice_client.stop()
    await ctx.send(formatResponse('Stopped'))

@bot.command(aliases=['sk'])
@commands.check(is_in_same_vc)
async def skip(ctx: Context):
    global flg_loop
    ctx.voice_client.stop()
    flg_loop = False
    await ctx.send(formatResponse('Skipped'))

@bot.command()
@commands.check(is_in_same_vc)
async def pause(ctx: Context):
    if ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send(formatResponse('Paused'))
    else:
        await ctx.send('Currently not played any songs')

@bot.command()
@commands.check(is_in_same_vc)
async def resume(ctx: Context):
    if ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send(formatResponse('Resumed'))
    else:
        await ctx.send('Currently not paused')

@bot.command()
@commands.check(is_in_same_vc)
async def loop(ctx: Context, *args):
    global flg_loop
    if len(args) == 0:
        flg_loop = not flg_loop
        await ctx.send('Looping: ' + str(flg_loop))
    else:
        url = ' '.join(args)
        await play_song(ctx, url, song_queue, loop=True)

@bot.command(aliases=['now','np'])
async def now_playing(ctx: Context):
    if len(song_queue) > 0:
        song, dj = song_queue[0]
        await ctx.send(formatNowPlaying(song['title'], song['duration'], dj, flg_loop))
    else:
        await ctx.send('Currently not playing any song')

@bot.command(aliases=['rm', 'dq', 'undo'])
@commands.check(is_in_same_vc)
async def pop(ctx: Context, index: int = -1):
    if len(song_queue) > 1:
        song, dj = song_queue.pop(index)
        await ctx.send('Removed {} from {}'.format(song['title'], dj))
    else:
        await ctx.send('No song in queue log')

@bot.command()
@commands.check(is_admin)
async def clear(ctx: Context):
    flg_stop = True
    flg_loop = False
    async with ctx.channel.typing():
        ctx.voice_client.stop()
        while len(song_queue) > 0:
            song_queue.pop()

    await ctx.send(formatResponse('Cleared Queue'))     

# MEME
@bot.command()
@commands.check(is_in_same_vc)
async def rip(ctx: Context, *args):
    url = ' '.join(args) + ' siivagunner'
    await play_song(ctx, url, song_queue)

@bot.command(aliases=['h'])
@commands.check(is_in_same_vc)
async def _help(ctx: Context, *args):
    url = 'yD2FSwTy2lw'
    await play_song(ctx, url, song_queue)

@bot.command()
@commands.check(is_in_same_vc)
async def pc(ctx: Context, *args):
    url = 'Z0DO0XyS8Ko'
    song = yt.extract_info(url)[0]
    await play_song(ctx, url, song_queue, metadata={'title':song['title'],'duration':song['duration']})

@bot.command()
@commands.check(is_in_same_vc)
async def pcc(ctx: Context, *args):
    url = '3H6QaUYVsVM' 
    song = yt.extract_info(url)[0]
    await play_song(ctx, url, song_queue, metadata={'title':song['title'],'duration':song['duration']})

#Join voice channel if it has not, otherwise do nothing.
async def join_voice(ctx):
    if ctx.voice_client is None:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            voice_client = await channel.connect()
            print(voice_client.channel)
        else:
            ctx.send("You are not connecting to VC right now.")
    else:
        print("Already connected to a voice channel")

def songEndEvent(ctx, song_queue):
    # global song_queue, flg_stop, flg_loop, client
    global flg_stop, flg_loop

    print('ending song...')

    asyncio.run_coroutine_threadsafe(ctx.bot.change_presence(status=Status.idle, activity=None), ctx.bot.loop)

    if not flg_loop or flg_stop:
        if len(song_queue) > 0:
            curr_song = song_queue.pop(0)  
            print('removed first item in queue')
    else:
        print('looping...')

    print(len(song_queue))

    #if manually called stop, stop advancing the queue, too.
    if flg_stop:
        print('force stop')
        flg_stop = False
        return

    #if song queue is empty
    if not song_queue:
        return
    # print('song start from song end')
    asyncio.run_coroutine_threadsafe(songStartEvent(ctx, song_queue), ctx.bot.loop)

async def songStartEvent(ctx, song_queue):
    # global song_queue, current_status, flg_loop
    global flg_loop

    # first, join voice channel 
    await join_voice(ctx)

    # print('starting song...')
    #if song queue is empty
    if not song_queue:
        await ctx.send('Please queue up some songs first!')
        return

    song, dj = song_queue[0]
    print('playing...',song['title'], song['id'])
    if song['loop']:
        print('loop this song')
        flg_loop = True

    player = await yt.YTDLSource.from_url(song['id'],stream=True)
    # print('playing: {} from {}'.format(player.title, dj))
    ctx.bot.voice_clients[0].play(player, after=lambda e: songEndEvent(ctx, song_queue))

    async with ctx.channel.typing():
        await ctx.send(formatNowPlaying(song['title'], song['duration'], dj, flg_loop))

    # set bot status
    await ctx.bot.change_presence(status=Status.online, activity=Game(name=song['title']))
    
async def play_song(ctx, url, song_queue, loop=False, metadata=None):
    try:
        print('queueing...')
        # await ctx.send('Queueing...',delete_after=3)

        song_list = yt.extract_info(url)
        '''
        song keys : (['id', 'uploader', 'uploader_id', 'uploader_url', 'channel_id', 'channel_url', 'upload_date', 'license', 'creator', 'title', 'alt_title', 'thumbnails', 'description', 'categories', 'tags', 'subtitles', 'automatic_captions', 'duration', 'age_limit', 'annotations', 'chapters', 'webpage_url', 'view_count', 'like_count', 'dislike_count', 'average_rating', 'formats', 'is_live', 'start_time', 'end_time', 'series', 'season_number', 'episode_number', 'track', 'artist', 'album', 'release_date', 'release_year', 'extractor', 'webpage_url_basename', 'extractor_key', 'n_entries', 'playlist', 'playlist_id', 'playlist_title', 'playlist_uploader', 'playlist_uploader_id', 'playlist_index', 'thumbnail', 'display_id', 'requested_subtitles', 'format_id', 'url', 'player_url', 'ext', 'format_note', 'acodec', 'abr', 'container', 'asr', 'filesize', 'fps', 'height', 'tbr', 'width', 'vcodec', 'downloader_options', 'format', 'protocol', 'http_headers'])
        '''

        # queue a song / playlist
        len_before = len(song_queue)
        for song in song_list:
            print('queued', song['title'], song['duration'])
            song['loop'] = loop
            if metadata:
                for k,v in metadata.items():
                    song[k] = v
            song_queue.append((song, ctx.author.display_name))

        if len(song_list) <= 0:
            await ctx.send('Playlist is empty')
            return

        #garbage collection
        del song_list

        #if queue empty before, start now
        #else send a queue message
        if len_before == 0:          
            await songStartEvent(ctx, song_queue)
        else:
            await ctx.send(formatQueueing(song['title'], song['duration'], ctx.author.display_name, len(song_queue)-1, song['loop']))

    except:
        await ctx.send('Unexpected Error : ' + sys.exc_info()[0].__name__)
        print(traceback.print_exc())

# async def resumeEvent(channel):
#     current_voice_channel.resume()
#     await client.change_presence(status=Status.online, activity=current_status)
#     await channel.send(formatResponse('Resumed'))

# @client.event
# async def on_message(message):
#     global current_voice_channel, song_queue, flg_loop, flg_stop, current_status

#     params = parse_parameters(message.content)
#     channel = message.channel
#     currentdj = message.author

#     # bot message
#     if message.author == client.user:
#         return

#     #If the message does not start with prefix, ignore
#     if not message.content.startswith(BOT_PREFIX):
#         return

#     #If the caller is not in the same VC as the bot, unless an admin
#     if not currentdj.voice is None:
#         if not current_voice_channel is None:
#             # print(currentdj.voice.channel)
#             # print(current_voice_channel.channel)
#             if currentdj.voice.channel != current_voice_channel.channel:
#                 await message.channel.send('You are not in the same VC with the bot.')
#                 return
#         else:
#             #If bot has not join VC yet, do it now (and should be called once)
#             await joinVoiceChannel(message,currentdj)
#     else:
#         await message.channel.send('You are not connecting to VC right now.')
#         return

#     # COMMANDS

#     if checkBotCommand(message,'grandad'):
#         await channel.send(formatResponse('Fleentstones'))

#     elif checkBotCommand(message,'play',HQRIP_COMMAND):

#         if len(params) == 0:
#             if current_voice_channel.is_playing():
#                 await channel.send('Currently playing audio. Please use `stop` to stop current song or `skip` to start next song immediately')
#             elif current_voice_channel.is_paused():
#                 await resumeEvent(channel)
#             else:
#                 await songStartEvent(channel)
#         else:
#             url = ' '.join(params)
#             if checkBotCommand(message,HQRIP_COMMAND):
#                 url += ' siivagunner'
#             await playEvent(channel, url, currentdj.display_name)


#     elif checkBotCommand(message, 'loop'):
#         if len(params) > 0: #loop <URL> - play <URL> with loop
#             url = ' '.join(params)
#             await playEvent(channel, url, currentdj.display_name, loop=True)
#         else:
#             flg_loop = not flg_loop
#             await channel.send('Loop current song: {}'.format(flg_loop))
#             print('flg_loop:',flg_loop)


#     elif checkBotCommand(message, 'now', 'np', 'nowplaying'):
#         if len(song_queue) > 0:
#             song, dj = song_queue[0]
#             await channel.send(formatNowPlaying(song['title'], song['duration'], dj, flg_loop))
#         else:
#             await channel.send('Currently not playing any song')

#     elif checkBotCommand(message, 'link', 'info'):
#         if len(song_queue) > 0:
#             song, dj = song_queue[0]
#             print(song)
#             await channel.send(song['webpage_url'])
#         else:
#             await channel.send('Currently not playing any song')

#     elif checkBotCommand(message, 'undo', 'dequeue', 'dq'):
#         if len(song_queue) > 1:
#             song_queue.pop()
#             await channel.send('Removed last song in queue')
#         else:
#             await channel.send('No song in queue log')

#     elif checkBotCommand(message, 'pop', 'remove'):
#         if len(params) > 0:
#             try:
#                 index = int(params[0])
#             except ValueError:
#                 await channel.send('Invalid index')
#                 return

#             if index < 1:
#                 await channel.send('Invalid index')
#                 return
#             elif index > len(song_queue):
#                 index = -1
#         else:
#             index = -1

#         if len(song_queue) > 1:
#             song, dj = song_queue.pop(index)
#             await channel.send('Removed {} from {}'.format(song['title'], dj))
#         else:
#             await channel.send('No song in queue log')


#     elif checkBotCommand(message,'pause'):

#         if current_voice_channel==None:
#             await channel.send('Currently not connect to Voice Channel')
#             return

#         if current_voice_channel.is_paused():
#             await channel.send('Currently already paused')
#             return

#         if not current_voice_channel.is_playing():
#             await channel.send('Currently not playing any song')
#             return

#         current_voice_channel.pause()
#         await client.change_presence(status=discord.Status.do_not_disturb, activity=current_status)
#         await channel.send(formatResponse('Paused'))

#     elif checkBotCommand(message,'resume'):

#         if current_voice_channel==None:
#             await channel.send('Currently not connect to Voice Channel')
#             return

#         if not current_voice_channel.is_paused():
#             await channel.send('Currently not paused')
#             return
#         await resumeEvent(channel)

#     elif checkBotCommand(message,'stop'):
#         print('stopping...')
#         if current_voice_channel==None:
#             await channel.send('Currently not connect to Voice Channel')
#             return

#         flg_stop = True
#         current_voice_channel.stop()
#         await channel.send(formatResponse('Stopped'))

#     elif checkBotCommand(message,'skip','sk'):
#         print('skipping...')
#         if current_voice_channel==None:
#             await channel.send('Currently not connect to Voice Channel')
#             return
#         if flg_loop:
#             flg_loop = False
#         current_voice_channel.stop()
#         await channel.send(formatResponse('Skipped'))

#     elif checkBotCommand(message,'queue','q','list','ls'):

#         if len(song_queue)==0:
#             await channel.send("`The song queue is empty`")
#             return

#         await channel.send(formatQueueList(song_queue, current_voice_channel, flg_loop))

#     elif checkBotCommand(message, 'clear', 'flush'):
#         print('clearing...')
#         if current_voice_channel==None:
#             await channel.send('Currently not connect to Voice Channel.')
#             return

#         flg_stop = True

#         async with channel.typing():
#             current_voice_channel.stop()
#             while len(song_queue) > 0:
#                 song_queue.pop()

#         await channel.send(formatResponse('Cleared Queue'))

#     # Meme shortcut command
#     elif checkBotCommand(message, 'help'):
#         //no one to help
#         await playEvent(channel, 'https://www.youtube.com/watch?v=yD2FSwTy2lw', currentdj.display_name)

#     elif checkBotCommand(message, 'pc'):
#         //pe cimpoi
#         await playEvent(channel, 'https://www.youtube.com/watch?v=Z0DO0XyS8Ko', currentdj.display_name)

#     elif checkBotCommand(message, 'pcc'):
#         //pe cimpoi cover
#         await playEvent(channel, 'https://www.youtube.com/watch?v=3H6QaUYVsVM', currentdj.display_name)


#     elif checkBotCommand(message,'disconnect','dc','logout'):
#         if isAdminMessage(message):
#             server = message.guild.voice_client
#             await client.change_presence(status=discord.Status.offline, activity=None)
#             await server.disconnect(force=True)
#             current_voice_channel=None
#             print('disconnected from vc')
#             await client.logout()
#             await client.close()
#             print('logout')
#         else:
#             await channel.send('This command can only be invoked by administrator.\nPlease call @Kirbio or @Sunny for help.')

#     # Simple test command to check if the bot is not dead
#     elif checkBotCommand(message,'ping','ping2'):
#         await channel.send(formatResponse('Pong'))

#     elif checkBotCommand(message,'status'):
#         if isAdminMessage(message):
#             await channel.send('flg_loop'+ str(flg_loop))
#             await channel.send('flg_stop'+ str(flg_stop))
#             await channel.send('queue'+ str(len(song_queue)))
#             await channel.send('is playing'+ str(current_voice_channel.is_playing()))
#             await channel.send('is pause'+ str(current_voice_channel.is_paused()))

#     else:
#         print('unknown command')

bot.run(const.BOT_TOKEN)
