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
    if len(handler.song_queue) == 0:
        await ctx.send("`The song queue is empty`")
    else:
        await ctx.send(formatQueueList(handler.song_queue, ctx.voice_client))

@bot.command(aliases=['p'])
@commands.check(is_in_same_vc)
async def play(ctx: Context, *args):
    if len(args) == 0:
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
        elif ctx.voice_client.is_playing():
            await ctx.send('Already playing an audio')
        else:
            await handler.songStartEvent(ctx)
    else:
        url = ' '.join(args)
        await handler.play_song(ctx, url)

@bot.command()
@commands.check(is_in_same_vc)
async def stop(ctx: Context):
    handler.set_stop(True)
    ctx.voice_client.stop()
    await ctx.send(formatResponse('Stopped'))

@bot.command(aliases=['sk'])
@commands.check(is_in_same_vc)
async def skip(ctx: Context):
    ctx.voice_client.stop()
    handler.set_loop(False)
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
    if len(args) == 0:
        handler.toggle_loop()
        await ctx.send('Looping: ' + str(handler.flg_loop))
    else:
        url = ' '.join(args)
        await handler.play_song(ctx, url, loop=True)

@bot.command(aliases=['now','np'])
async def now_playing(ctx: Context):
    if len(handler.song_queue) > 0:
        song, dj = handler.get_top_song()
        await ctx.send(formatNowPlaying(song['title'], song['duration'], dj, handler.flg_loop))
    else:
        await ctx.send('Currently not playing any song')

@bot.command(aliases=['rm', 'dq', 'undo'])
@commands.check(is_in_same_vc)
async def pop(ctx: Context, index: int = -1):
    if len(handler.song_queue) > 1:
        song, dj = handler.pop_queue(index)
        await ctx.send('Removed {} from {}'.format(song['title'], dj))
    else:
        await ctx.send('No song in queue log')

@bot.command()
@commands.check(is_admin)
async def clear(ctx: Context):
    print('clearing queue...')
    handler.set_loop(False)
    handler.set_stop(True)
    async with ctx.channel.typing():
        ctx.voice_client.stop()
        handler.clear_queue()
        await asyncio.sleep(5)
    await ctx.send(formatResponse('Cleared Queue'))     

# cogs
bot.add_cog(Memes(bot, handler))

bot.run(const.BOT_TOKEN)
