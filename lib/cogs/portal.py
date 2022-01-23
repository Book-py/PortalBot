from discord.ext import commands
import discord
import datetime as dt


class portal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channels = [934748923740950569, 934748891788754965]

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("portal")
            print("Portal loaded")
            await self.bot.log_channel.send("Portal loaded!")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if (
            message.channel.id in self.channels
            and message.content
            and not message.author.bot
        ):
            embed = discord.Embed(
                title="New message",
                description=message.content,
                colour=message.author.colour,
                timestamp=dt.datetime.utcnow(),
            )
            embed.set_author(
                name=message.author.name, icon_url=message.author.avatar_url
            )
            embed.set_footer(
                text=f"Message from: {message.guild.name}",
                icon_url=message.guild.icon_url,
            )

            for portal_channel_id in self.channels:
                if portal_channel_id != message.channel.id:
                    portal_channel = self.bot.get_channel(portal_channel_id)
                    await portal_channel.send(embed=embed)


def setup(bot):
    bot.add_cog(portal(bot))
