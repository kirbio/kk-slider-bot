from discord.ext import commands
from events import MusicEventHandler 
from checks import *

class Memes(commands.Cog):
    def __init__(self, bot: commands.Bot, music_handler: MusicEventHandler):
        self.bot = bot
        self.music_handler = music_handler

    # MEME
    @commands.command()
    @commands.check(is_in_same_vc)
    async def rip(self, ctx: commands.Context, *args):
        url = ' '.join(args) + ' siivagunner'
        await self.music_handler.play_song(ctx, url)

    @commands.command(aliases=['h'])
    @commands.check(is_in_same_vc)
    async def _help(self, ctx: commands.Context):
        url = 'yD2FSwTy2lw'
        await self.music_handler.play_song(ctx, url)