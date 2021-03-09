from discord.ext import commands
import asyncio

class BotEventListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_connect(self):
        # raidful.updateLocal()
        # client.loop.create_task(sync_db())
        print('Connected')

    @commands.Cog.listener()
    async def on_disconnect(self):
        print('Disconnected')

    @commands.Cog.listener()
    async def on_ready(self):
        print('Logged in as {0.user}'.format(self.bot))

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.send(error)
        elif isinstance(error, asyncio.TimeoutError):
            await ctx.send("The bot couldn't connect to the voice channel you're in")
        elif isinstance(error, commands.CheckFailure):
            print(error)
            await ctx.send(error)
        else:
            print(error, type(error))
            await ctx.send(error)
        