from discord.ext.commands import Bot

import const
from checks import *
from cogs.commands.basic import BasicCommands
from cogs.commands.memes import MemeCommands
from cogs.commands.music import MusicCommands
from cogs.listener import BotEventListener
from handler import MusicEventHandler
from util import *

bot = Bot(command_prefix='!')
handler = MusicEventHandler(bot)

# cogs
bot.add_cog(BotEventListener(bot))
bot.add_cog(BasicCommands(bot))
bot.add_cog(MusicCommands(bot, handler))
bot.add_cog(MemeCommands(bot, handler))

if __name__ == "__main__":
    bot.run(const.BOT_TOKEN)
