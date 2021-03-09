import discord
from discord.ext import commands
from discord.ext.commands import Context

class BasicCommands(commands.Cog, name='General'):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        
    @commands.command()
    async def ping(self, ctx: Context):
        await ctx.send("Pong")
        print(ctx.voice_client)
        print(ctx.bot.voice_clients)
        print(self.bot.voice_clients)

    @commands.command(name='dc')
    @commands.has_role('admin')
    async def disconnect(self, ctx: Context):
        await self.bot.change_presence(status=discord.Status.offline, activity=None)
        if self.bot.voice_clients:
            await self.bot.voice_clients[0].disconnect()
        await self.bot.logout()
        
    @commands.command(hidden=True)
    @commands.has_role('admin')
    async def disable(self, ctx: Context, cmd):
        self.bot.get_command(cmd).enabled = False
        
    @commands.command(hidden=True)
    @commands.has_role('admin')
    async def enable(self, ctx: Context, cmd):
        self.bot.get_command(cmd).enabled = True