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

    @commands.command(aliases=['h'])
    @commands.check(is_in_same_vc)
    async def _help(self, ctx: commands.Context, *args):
        url = 'yD2FSwTy2lw'
        opt, args = parse_arguments(args)
        await self.music_handler.play_song(ctx, url, opt=opt)
    
    @commands.command()
    @commands.check(is_in_same_vc)
    async def pc(self, ctx: commands.Context, *args):
        url = 'Z0DO0XyS8Ko'
        if ctx.message.id % 13 == 0:
            url = 'OzGVz1ClxIc'
        opt, args = parse_arguments(args)
        await self.music_handler.play_song(ctx, url, opt=opt, metadata={'title':'Sandu Ciorba - Pe cimpoi','duration':128})

    @commands.command()
    @commands.check(is_in_same_vc)
    async def pcc(self, ctx: commands.Context, *args):
        url = '3H6QaUYVsVM' 
        if ctx.message.id % 13 == 0:
            url = 'g1p5eNOsl7I'
        opt, args = parse_arguments(args)
        await self.music_handler.play_song(ctx, url, opt=opt, metadata={'title':'My friends and I thought making a cover of Pe Cimpoi was a good idea but it was not','duration':133})

    @commands.command()
    @commands.check(is_in_same_vc)
    async def wap(self, ctx: commands.Context, *args):
        url = 'hsm4poTWjMs' 
        opt, args = parse_arguments(args)
        await self.music_handler.play_song(ctx, url, opt=opt)

    @commands.command()
    @commands.check(is_in_same_vc)
    async def bd(self, ctx: commands.Context, *args):
        url = 'i63cgUeSsY0' 
        opt, args = parse_arguments(args)
        await self.music_handler.play_song(ctx, url, opt=opt)
        
    @commands.command()
    @commands.check(is_in_same_vc)
    async def dmc(self, ctx: commands.Context, *args):
        url = 'RofLs15xbaE' 
        opt, args = parse_arguments(args)
        await self.music_handler.play_song(ctx, url, opt=opt)
        
    @commands.command()
    @commands.check(is_in_same_vc)
    async def fri(self, ctx: commands.Context, *args):
        url = 'kfVsfOSbJY0' 
        opt, args = parse_arguments(args)
        await self.music_handler.play_song(ctx, url, opt=opt)
        
    @commands.command()
    @commands.check(is_in_same_vc)
    async def date(self, ctx: commands.Context):
        date = datetime.datetime.today().weekday()
        if date == 0:
            url = 'BP2WuMnolYg'
        elif date == 1:
            url = 'glD11w7PNkU'
        elif date == 2:
            url = 'w3HewsbI_8w'
        elif date == 3:
            url = 'YbQ2WPSQVio'
        elif date == 4:
            url = 'https://www.youtube.com/playlist?list=PLz4w0uZ2tPyziejmDGb6es3FzFFi5HRQk'
        elif date == 5:
            url = 'sRA0-t7TChg'
        else:
            url = 'npgdw5Zb7TY'
        await self.music_handler.play_song(ctx, url)