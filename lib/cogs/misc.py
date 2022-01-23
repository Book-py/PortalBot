from discord.ext import commands
import discord
import datetime as dt


class misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._message = (
            "watching +help | connecting {users:,} users in {guilds:,} servers"
        )

    @property
    def message(self):
        return self._message.format(
            users=len(self.bot.users), guilds=len(self.bot.guilds)
        )

    @message.setter
    def message(self, value):
        if value.split(" ")[0] not in ("playing", "watching", "listening", "streaming"):
            raise ValueError("Invalid activity type.")

        self._message = value

    async def set(self):
        _type, _name = self.message.split(" ", maxsplit=1)

        await self.bot.change_presence(
            activity=discord.Activity(
                name=_name,
                type=getattr(discord.ActivityType, _type, discord.ActivityType.playing),
            )
        )

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("misc")
            print("misc loaded")
            await self.bot.log_channel.send("misc loaded!")

    @commands.is_owner()
    @commands.command("set-status")
    async def set_status_cmd(self, ctx: commands.Context, *, status: str) -> None:
        """Set the status of the bot."""
        self.message = status
        await self.set()

    @commands.command("info")
    async def info_cmd(self, ctx: commands.Context) -> None:
        """See the information for me"""

        embed = discord.Embed(
            title="Bot information",
            description="I am a bot which connects channels in servers together",
            timestamp=dt.datetime.utcnow(),
        )

        fields = [
            ("Github repository", "https://github.com/Book-py/PortalBot", True),
            ("Developers", "<@781305692371157034> and <@700336923264155719>", True),
            (
                "Bot invite",
                "https://discord.com/api/oauth2/authorize?client_id=932476341977223170&permissions=378944&scope=bot",
                True,
            ),
            ("Server invite", "https://discord.gg/FHXKUVN8Sp", True),
        ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(misc(bot))
