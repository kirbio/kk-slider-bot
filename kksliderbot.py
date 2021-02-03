import asyncio
from cogs.memes import Memes
import sys
import traceback

import discord
from discord import FFmpegPCMAudio, Game, Status
from discord.ext import commands
from discord.ext.commands import Bot, Context
from discord.ext.commands.errors import CommandInvokeError
from discord.voice_client import VoiceClient
from youtube_dl.utils import DownloadError

import const
import youtubestreaming as yt
from checks import *
from events import *
from events import MusicEventHandler
from util import *

bot = commands.Bot(command_prefix='!')
handler = MusicEventHandler(bot)

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
    if isinstance(error, commands.MissingRole):
        await ctx.send(error)
    elif isinstance(error, asyncio.TimeoutError):
        await ctx.send("The bot couldn't connect to the voice channel you're in")
    elif isinstance(error, commands.CheckFailure):
        print(error)
        await ctx.send(error)
    else:
        print(error)
        await ctx.send(error)

@bot.command()
async def ping(ctx: Context):
    await ctx.send("Pong")
    print(ctx.voice_client)
    print(ctx.bot.voice_clients)
    print(bot.voice_clients)

@bot.command(name='dc')
@commands.has_role('admin')
async def disconnect(ctx: Context):
    await bot.change_presence(status=discord.Status.offline, activity=None)
    if bot.voice_clients:
        await bot.voice_clients[0].disconnect()
    await bot.logout()

@bot.command(aliases=['q', 'ls', 'list'])
async def queue(ctx: Context):
    if len(handler.song_queue) == 0:
        await ctx.send("`The song queue is empty`")
    else:
        await ctx.send(formatQueueList(handler.song_queue, ctx.voice_client))

@bot.command(aliases=['p'])
@commands.check(is_in_same_vc)
async def play(ctx: Context, *args):
    if len(args) == 0:
        if is_paused(ctx): # resume if song is paused
            ctx.voice_client.resume()
        elif is_playing_song(ctx): # throw error if song is already playing
            raise SongNotPaused()
        else: # else (stopped), start next song in queue immediately
            await handler.songStartEvent(ctx)
    else:
        opt, args = parse_arguments(args)
        url = ' '.join(args)
        await handler.play_song(ctx, url, opt=opt)

@bot.command()
@commands.check(is_in_same_vc)
async def stop(ctx: Context):
    if ctx.voice_client:
        handler.set_stop(True)
        ctx.voice_client.stop()
        await ctx.send(formatResponse('Stopped'))
    else:
        await ctx.send('No song to stop')
        

@bot.command(aliases=['sk'])
@commands.check(is_in_same_vc)
async def skip(ctx: Context):
    if ctx.voice_client:
        handler.set_loop(False)
        ctx.voice_client.stop()
        await ctx.send(formatResponse('Skipped'))
    else:
        await ctx.send('No song to skip')

@bot.command()
@commands.check(is_in_same_vc)
@commands.check(check_is_playing_song)
async def pause(ctx: Context):
    ctx.voice_client.pause()
    await ctx.send(formatResponse('Paused'))

@bot.command()
@commands.check(is_in_same_vc)
@commands.check(check_is_paused)
async def resume(ctx: Context):
    ctx.voice_client.resume()
    await ctx.send(formatResponse('Resumed'))

@bot.command()
@commands.check(is_in_same_vc)
async def loop(ctx: Context, *args):
    if len(args) == 0:
        handler.toggle_loop()
        await ctx.send('Looping: ' + str(handler.flg_loop))
    else:
        opt, args = parse_arguments(args)
        url = ' '.join(args)
        await handler.play_song(ctx, url, opt=opt, loop=True)

@bot.command(aliases=['now','np'])
async def now_playing(ctx: Context):
    if len(handler.song_queue) > 0:
        song = handler.get_top_song()
        await ctx.send(formatNowPlaying(song['title'], song['duration'], song['dj'], handler.flg_loop))
    else:
        await ctx.send('Currently not playing any song')

@bot.command(aliases=['rm', 'dq', 'undo'])
@commands.check(is_in_same_vc)
async def pop(ctx: Context, index: int = -1):
    if len(handler.song_queue) > 1:
        song= handler.pop_queue(index)
        await ctx.send('Removed {} from {}'.format(song['title'], song['dj']))
    else:
        await ctx.send('No song in queue log. To skip current song, use `skip`')

@bot.command()
@commands.has_role('admin')
async def clear(ctx: Context):
    print('clearing queue...')
    handler.set_loop(False)
    handler.set_stop(True)
    async with ctx.channel.typing():
        if ctx.voice_client:
            ctx.voice_client.stop()
        handler.clear_queue()
        await asyncio.sleep(5)
    await ctx.send(formatResponse('Cleared Queue'))     

# cogs
bot.add_cog(Memes(bot, handler))

bot.run(const.BOT_TOKEN)
