from discord.ext.commands import Cog
from discord.ext.commands import command
from discord import Embed
from datetime import datetime

class ExampleCog(Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('ExampleCog')
        print('Example Cog loaded')
        await self.bot.bot_channel.send('Example cog loaded!')

def setup(bot):
    bot.add_cog(ExampleCog(bot))