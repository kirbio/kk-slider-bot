import asyncio
import sys
import traceback

from discord import Game, Status, VoiceChannel
from discord.ext.commands import Context
from discord.ext.commands.errors import CommandError

import youtubestreaming as yt
from util import *


class MusicEventHandler():

    def __init__(self, bot):
        self.bot = bot
        self.song_queue = []
        self.flg_stop = False
        self.flg_loop = False
        
    def set_stop(self, val):
        self.flg_stop = val
        
    def set_loop(self, val):
        self.flg_loop = val
    
    def toggle_loop(self):
        self.flg_loop = not self.flg_loop
        
    def get_top_song(self):
        return self.song_queue[0] if len(self.song_queue) > 0 else None
    
    def pop_queue(self, index=-1):
        size = len(self.song_queue)
        if 1 <= index < size or index == -1: # Index can't be 0 (current song)
            return self.song_queue.pop(index)
        else:
            raise CommandError('Index out of range')

    def clear_queue(self):
        while len(self.song_queue) > 0:
            self.song_queue.pop()
        
    #Join voice channel if it has not, otherwise do nothing.
    async def join_voice(self, ctx: Context):
        if ctx.voice_client is None:
            if ctx.author.voice:
                channel: VoiceChannel = ctx.author.voice.channel
                await channel.connect(timeout=10)
            else:
                ctx.send("You are not connecting to VC right now.")
        else:
            print("Already connected to a voice channel")

    def songEndEvent(self, ctx: Context):

        print('ending song...')

        asyncio.run_coroutine_threadsafe(ctx.bot.change_presence(status=Status.idle, activity=None), ctx.bot.loop)

        if not self.flg_loop or self.flg_stop:
            if len(self.song_queue) > 0:
                curr_song = self.song_queue.pop(0)  
                print('removed first item in queue')
        else:
            print('looping...')

        print(len(self.song_queue))

        #if manually called stop, stop advancing the queue, too.
        if self.flg_stop:
            print('force stop')
            self.flg_stop = False
            return

        #if song queue is empty
        if not self.song_queue:
            return
        # print('song start from song end')
        asyncio.run_coroutine_threadsafe(self.songStartEvent(ctx), ctx.bot.loop)

    async def songStartEvent(self, ctx: Context):
        # first, join voice channel 
        await self.join_voice(ctx)

        # print('starting song...')
        #if song queue is empty
        if not self.song_queue:
            await ctx.send('Please queue up some songs first!')
            return

        song = self.song_queue[0]
        print('playing...',song['title'], song['id'])
        if song['loop']:
            print('loop this song')
            self.flg_loop = True

        player = await yt.YTDLSource.from_url(song['id'],stream=True,options=song['opt'])
        # print('playing: {} from {}'.format(player.title, dj))
        ctx.bot.voice_clients[0].play(player, after=lambda e: self.songEndEvent(ctx))

        await ctx.send(formatNowPlaying(song['title'], song['duration'], song['dj'], self.flg_loop))

        # set bot status
        await ctx.bot.change_presence(status=Status.online, activity=Game(name=song['title']))
        
    async def play_song(self, ctx: Context, url, loop=False, metadata=None, opt=None):  
        print('queueing...')
        await ctx.send('Queueing...',delete_after=2)
        async with ctx.channel.typing():
            songs = yt.extract_info(url)              
            len_before = len(self.song_queue)
    
            if len(songs) <= 0:
                await ctx.send('No videos found')
                return
            
            # queue a song / playlist
            for s in songs:
                song_item = {'title':s['title'],
                            'duration':s['duration'],
                            'id':s['id'],
                            'dj':ctx.author.display_name,
                            'opt':opt,
                            'loop':loop}
                if metadata:
                    for k,v in metadata.items():
                        song_item[k] = v
                self.song_queue.append(song_item)
                print(song_item)
            del songs #garbage collection

        if len_before == 0:     #if queue empty before, start now          
            await self.songStartEvent(ctx)
        else:                   #else send a queue message
            await ctx.send(formatQueueing(song_item['title'], song_item['duration'], song_item['dj'], len(self.song_queue)-1, song_item['loop']))