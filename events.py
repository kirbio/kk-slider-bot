import asyncio
import sys
import traceback

from discord import Game, Status
from discord.ext.commands import Context

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
        return self.song_queue.pop(index)
    
    def clear_queue(self):
        while len(self.song_queue) > 0:
            self.song_queue.pop()
        
    #Join voice channel if it has not, otherwise do nothing.
    async def join_voice(self, ctx: Context):
        if ctx.voice_client is None:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                voice_client = await channel.connect()
                print(voice_client.channel)
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

        song, dj = self.song_queue[0]
        print('playing...',song['title'], song['id'])
        if song['loop']:
            print('loop this song')
            self.flg_loop = True

        player = await yt.YTDLSource.from_url(song['id'],stream=True)
        # print('playing: {} from {}'.format(player.title, dj))
        ctx.bot.voice_clients[0].play(player, after=lambda e: self.songEndEvent(ctx))

        await ctx.send(formatNowPlaying(song['title'], song['duration'], dj, self.flg_loop))

        # set bot status
        await ctx.bot.change_presence(status=Status.online, activity=Game(name=song['title']))
        
    async def play_song(self, ctx: Context, url, loop=False, metadata=None):
        try:
            print('queueing...')
            # await ctx.send('Queueing...',delete_after=3)
            async with ctx.channel.typing():
                song_list = yt.extract_info(url)
                '''
                song keys : (['id', 'uploader', 'uploader_id', 'uploader_url', 'channel_id', 'channel_url', 'upload_date', 'license', 'creator', 'title', 'alt_title', 'thumbnails', 'description', 'categories', 'tags', 'subtitles', 'automatic_captions', 'duration', 'age_limit', 'annotations', 'chapters', 'webpage_url', 'view_count', 'like_count', 'dislike_count', 'average_rating', 'formats', 'is_live', 'start_time', 'end_time', 'series', 'season_number', 'episode_number', 'track', 'artist', 'album', 'release_date', 'release_year', 'extractor', 'webpage_url_basename', 'extractor_key', 'n_entries', 'playlist', 'playlist_id', 'playlist_title', 'playlist_uploader', 'playlist_uploader_id', 'playlist_index', 'thumbnail', 'display_id', 'requested_subtitles', 'format_id', 'url', 'player_url', 'ext', 'format_note', 'acodec', 'abr', 'container', 'asr', 'filesize', 'fps', 'height', 'tbr', 'width', 'vcodec', 'downloader_options', 'format', 'protocol', 'http_headers'])
                '''
                
                # queue a song / playlist
                len_before = len(self.song_queue)
                for song in song_list:
                    song_item = {'title':song['title'],
                                 'duration':song['duration'],
                                 'id':song['id'],
                                 'loop':loop}
                    print('queued', song_item['title'], song_item['duration'])
                    if metadata:
                        for k,v in metadata.items():
                            song_item[k] = v
                    self.song_queue.append((song_item, ctx.author.display_name))
                    print(song_item)
                       
            if len(song_list) <= 0:
                await ctx.send('Playlist is empty')
                return
            
            #garbage collection
            del song_list

            if len_before == 0:     #if queue empty before, start now          
                await self.songStartEvent(ctx)
            else:                   #else send a queue message
                await ctx.send(formatQueueing(song_item['title'], song_item['duration'], ctx.author.display_name, len(self.song_queue)-1, song_item['loop']))

        except:
            await ctx.send('Unexpected Error : ' + sys.exc_info()[0].__name__)
            print(traceback.print_exc())
