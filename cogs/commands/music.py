import asyncio
from discord.ext import commands
from handler import MusicEventHandler
from checks import *
from util import *

class MusicCommands(commands.Cog, name='Music Controls'):
    def __init__(self, bot: commands.Bot, music_handler: MusicEventHandler):
        self.bot = bot
        self.music_handler = music_handler
        
    ######################
    # Play / Loop
    ######################
    @commands.command(aliases=['p'])
    @commands.check(is_in_same_vc)
    async def play(self, ctx: Context, *args):
        if len(args) == 0:
            if is_paused(ctx): # resume if song is paused
                ctx.voice_client.resume()
            elif is_playing_song(ctx): # throw error if song is already playing
                raise SongNotPaused()
            else: # else (stopped), start next song in queue immediately
                await self.music_handler.songStartEvent(ctx)
        else:
            opt, args = parse_arguments(args)
            url = ' '.join(args)
            await self.music_handler.play_song(ctx, url, opt=opt)
    
    @commands.command()
    @commands.check(is_in_same_vc)
    async def loop(self, ctx: Context, *args):
        if len(args) == 0:
            self.music_handler.toggle_loop()
            await ctx.send('Looping: ' + str(self.music_handler.flg_loop))
        else:
            opt, args = parse_arguments(args)
            url = ' '.join(args)
            await self.music_handler.play_song(ctx, url, opt=opt, loop=True)

    ######################
    # Stop / Skip / Pause
    ######################
    @commands.command()
    @commands.check(is_in_same_vc)
    async def stop(self, ctx: Context):
        if ctx.voice_client:
            self.music_handler.set_stop(True)
            ctx.voice_client.stop()
            await ctx.send(formatResponse('Stopped'))
        else:
            await ctx.send('No song to stop')

    @commands.command(aliases=['sk'])
    @commands.check(is_in_same_vc)
    async def skip(self, ctx: Context):
        if ctx.voice_client:
            self.music_handler.set_loop(False)
            ctx.voice_client.stop()
            await ctx.send(formatResponse('Skipped'))
        else:
            await ctx.send('No song to skip')

    @commands.command()
    @commands.check(is_in_same_vc)
    @commands.check(check_is_playing_song)
    async def pause(self, ctx: Context):
        ctx.voice_client.pause()
        await ctx.send(formatResponse('Paused'))

    @commands.command()
    @commands.check(is_in_same_vc)
    @commands.check(check_is_paused)
    async def resume(self, ctx: Context):
        ctx.voice_client.resume()
        await ctx.send(formatResponse('Resumed'))
        
    ######################
    # Query
    ######################         
    @commands.command(aliases=['q', 'ls', 'list'])
    async def queue(self, ctx: Context):
        if len(self.music_handler.song_queue) == 0:
            await ctx.send("`The song queue is empty`")
        else:
            await ctx.send(formatQueueList(self.music_handler.song_queue, ctx.voice_client))

    @commands.command(name='np',aliases=['now'])
    async def now_playing(self, ctx: Context):
        if len(self.music_handler.song_queue) > 0:
            song = self.music_handler.get_top_song()
            await ctx.send(formatNowPlaying(song['title'], song['duration'], song['dj'], self.music_handler.flg_loop))
        else:
            await ctx.send('Currently not playing any song')

    ######################
    # Removal
    ######################  
    @commands.command(aliases=['rm', 'dq', 'undo'])
    @commands.check(is_in_same_vc)
    async def pop(self, ctx: Context, index: int = -1):
        if len(self.music_handler.song_queue) > 1:
            song= self.music_handler.pop_queue(index)
            await ctx.send('Removed {} from {}'.format(song['title'], song['dj']))
        else:
            await ctx.send('No song in queue log. To skip current song, use `skip`')

    @commands.command()
    @commands.has_role('admin')
    async def clear(self, ctx: Context):
        print('clearing queue...')
        self.music_handler.set_loop(False)
        self.music_handler.set_stop(True)
        async with ctx.channel.typing():
            if ctx.voice_client:
                ctx.voice_client.stop()
            self.music_handler.clear_queue()
            await asyncio.sleep(5)
        await ctx.send(formatResponse('Cleared Queue'))     