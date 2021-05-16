from discord.ext import commands
from handler import MusicEventHandler 
from checks import *
from util import parse_arguments
import datetime

class MemeCommands(commands.Cog, name='Meme'):
    def __init__(self, bot: commands.Bot, music_handler: MusicEventHandler):
        self.bot = bot
        self.music_handler = music_handler

    # MEME
    @commands.command()
    @commands.check(is_in_same_vc)
    async def rip(self, ctx: commands.Context, *args):
        url = ' '.join(args) + ' siivagunner'
        opt, args = parse_arguments(args)
        await self.music_handler.play_song(ctx, url, opt=opt)

    @commands.command(aliases=['h','bug'])
    @commands.check(is_in_same_vc)
    async def _help(self, ctx: commands.Context, *args):
        url = 'yD2FSwTy2lw'
        opt, args = parse_arguments(args)
        await self.music_handler.play_song(ctx, url, opt=opt)
    
    @commands.command()
    @commands.check(is_in_same_vc)
    async def believe(self, ctx: commands.Context, *args):
        url = 'prw2B_03IzY'
        opt, args = parse_arguments(args)
        await self.music_handler.play_song(ctx, url, opt=opt)