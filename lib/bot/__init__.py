import traceback
from datetime import datetime
from pathlib import Path
import asyncio
import typing

import discord
from discord.ext import commands

OWNER_IDS = [781305692371157034, 700336923264155719]
ERROR_CHANNEL = 931866921266216984
COGS = [p.stem for p in Path(".").glob("./lib/cogs/*.py")]


def get_prefix(bot, message):
    return commands.when_mentioned_or("+")(bot, message)


class Ready:
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f" {cog} cog ready")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class Bot(commands.Bot):
    def __init__(self):
        self.ready = False
        self.cogs_ready = Ready()

        super().__init__(
            command_prefix=get_prefix,
            owner_ids=OWNER_IDS,
            intents=discord.Intents.all(),
        )

    def run(self, version):
        self.VERSION = version
        print(f"running setup in version {version}...")

        with open("./lib/bot/token.0", "r") as tf:
            self.TOKEN = tf.read()

        print("Running bot...")
        self.setup()
        super().run(self.TOKEN, reconnect=True)

    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f" {cog} cog loaded")

    async def on_connect(self):
        print("Bot connected!")

    async def on_disconnect(self):
        print("Bot disconnected")

    async def on_error(self, event, *args, **kwargs):
        print("py\n%s\n" % traceback.format_exc())
        if event == "on_command_error":
            await args[0].send("Something went wrong.")

        e = discord.Embed(
            title="Event Error" if event != "on_command_error" else "Command Error",
            colour=0xA32952,
        )
        e.add_field(
            name="Event",
            value=event if event != "on_command_error" else "Command Error",
        )
        e.description = "```py\n%s\n```" % traceback.format_exc()
        try:
            big_xd = f"Name: {args[0].guild.name}\nID: {args[0].guild.id}"
            e.add_field(name="location", value=big_xd)
        except:
            pass

        e.timestamp = datetime.utcnow()
        ch = self.get_channel(ERROR_CHANNEL)
        try:
            await ch.send(embed=e)
        except:
            await ch.send("tried sending an error but no xd")

    async def on_command_error(
        self, ctx: commands.Context, error
    ) -> typing.Coroutine[any, any, None]:
        if isinstance(error, commands.NotOwner):
            return await ctx.send("That command can only be used by a bot owner")
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send("You are missing at least 1 required argument")
        if isinstance(error, commands.CommandNotFound):
            pass

        if hasattr(error, "original"):
            if isinstance(error.original, ValueError):
                return await ctx.send("That is not a valid status type")
            else:
                raise error.original

        raise error

    async def on_ready(self):
        if not self.ready:
            self.log_channel = self.get_channel(931866921266216984)

            while not self.cogs_ready.all_ready():
                await asyncio.sleep(0.5)

            await self.log_channel.send("Now online")
            await self.log_channel.send(
                "------------------------------------------------------------"
            )

            print("Bot ready!")
            self.ready = True

            misc = self.get_cog("misc")
            await misc.set()
        else:
            print("Bot connected")


bot = Bot()
