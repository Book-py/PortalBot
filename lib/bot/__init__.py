import traceback
from asyncio import sleep
from datetime import datetime
from glob import glob

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import DMChannel, Embed, Intents
from discord.errors import Forbidden, HTTPException
from discord.ext.commands import BadArgument
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import (BotMissingPermissions, CheckFailure,
								  CommandNotFound, CommandOnCooldown, Context,
								  ExpectedClosingQuoteError,
								  InvalidEndOfQuotedStringError,
								  MissingPermissions, MissingRequiredArgument,
								  NotOwner, TooManyArguments, UserInputError,
								  when_mentioned_or)

OWNER_IDS = [700336923264155719, 769708895572197437, 380160133172428806]
COGS = [path.split("\\")[-1][:-3] for path in glob('./lib/cogs/*.py')]
ERROR_CHANNEL = 825357854566776832

def get_prefix(bot, message):
	return when_mentioned_or("+")(bot, message)

class Ready(object):
	def __init__(self):
		for cog in COGS:
			setattr(self, cog, False)

	def ready_up(self, cog):
		setattr(self, cog, True)
		print(f'{cog} cog ready!')

	def all_ready(self):
		return all([getattr(self, cog) for cog in COGS])

class Bot(BotBase):
	def __init__(self):
		self.ready = False
		self.cogs_ready = Ready()
		self.scheduler = AsyncIOScheduler()

		super().__init__(
			command_prefix=get_prefix,
			owner_ids=OWNER_IDS,
			intents=Intents.all())

	async def keep_open(self):
		portal = self.get_channel(829961182752407592)
		await portal.send("Keeping this session open")

	def setup(self):
		for cog in COGS:
			self.load_extension(f'lib.cogs.{cog}')
			print(f'{cog} cog loaded')
		print("setup complete")
	
	def run(self, version):
		self.VERSION = version
		print(f'running setup in version {version}...')

		self.setup()

		with open("./lib/bot/token.0", "r") as tf:
			self.TOKEN = tf.read()

		print("Running bot...")
		super().run(self.TOKEN, reconnect=True)

	def prefix(self, guild):
		if guild is not None:
			return "*"

	async def on_connect(self):
		print("Bot connected!")

	async def on_disconnect(self):
		print("Bot disconnected")

	async def on_error(self, event, *args, **kwargs):
		print('py\n%s\n' % traceback.format_exc())
		if event == "on_command_error":
			await args[0].send("Something went wrong.")

		e = Embed(title='Event Error' if event != "on_command_error" else "Command Error", colour=0xa32952)
		e.add_field(name='Event', value=event if event != "on_command_error" else "Command Error")
		e.description = '```py\n%s\n```' % traceback.format_exc()
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

	async def on_command_error(self, ctx, exc):
		if isinstance(exc, CommandNotFound):
			pass

		elif isinstance(exc, MissingRequiredArgument):
			await ctx.send(f"No `{exc.param.name}` argument was passed, despite being required.")

		elif isinstance(exc, BadArgument):
			embed = Embed(
				title="There was a problem",
				description="One or more arguments are invalid.",
				colour=0xFF0000,
				timestamp=datetime.utcnow())
			await ctx.send(embed=embed)

		elif isinstance(exc, TooManyArguments):
			embed = Embed(
				title="There was a problem",
				description="Too many arguments have been passed.",
				colour=0xFF0000,
				timestamp=datetime.utcnow())
			await ctx.send(embed=embed)

		elif isinstance(exc, MissingPermissions):
			embed = Embed(
				title="There was a problem",
				description="You don't have the permissions required to use that command",
				colour=0xFF0000,
				timestamp=datetime.utcnow())
			await ctx.send(embed=embed)

		elif isinstance(exc, BotMissingPermissions):
			embed = Embed(
				title="There was a problem",
				description="I don't have the correct permissions to complete that command",
				colour=0xFF0000,
				timestamp=datetime.utcnow())
			await ctx.send(embed=embed)

		elif isinstance(exc, NotOwner):
			embed = Embed(
				title="There was a problem",
				description="Only BonkBot's owner can use that command. Sorry",
				colour=0xFF0000,
				timestamp=datetime.utcnow())
			await ctx.send(embed=embed)

		elif isinstance(exc, CommandOnCooldown):
			cooldown_texts = {
			"BucketType.user": "You can not use the `{}` command for another {}. seconds",
			"BucketType.guild": "The `{}` command can not be used in this server for another {} seconds.",
			"BucketType.channel": "The `{}` command can not be used in this channel for another {} seconds.",
			"BucketType.member": "You can not use the `{}` command in this server for another {} seconds.",
			"BucketType.category": "The `{}` command can not be used in this category for another {} seconds.",
			}
			await ctx.message.delete()
			embed = Embed(
				title="There was a problem",
				description=cooldown_texts[str(exc.cooldown.type)].format(ctx.command.name, exc.retry_after),
				colour=0xFF0000,
				timestamp=datetime.utcnow())
			await ctx.send(embed=embed)

		elif isinstance(exc, InvalidEndOfQuotedStringError):
			embed = Embed(
				title="There was a problem",
				description=f"Bonk expected a space after the closing quote, but found a(n) `{exc.char}` instead.",
				colour=0xFF0000,
				timestamp=datetime.utcnow())
			await ctx.send(embed=embed)

		elif isinstance(exc, ExpectedClosingQuoteError):
			embed = Embed(
				title="There was a problem",
				description="Bonk expected a closing quote character, but didn't find one.",
				colour=0xFF0000,
				timestamp=datetime.utcnow())
			await ctx.send(embed=embed)

		elif isinstance(exc, UserInputError):
			embed = Embed(
				title="There was a problem",
				description="There was an unhandled user input problem (probably argument passing error).",
				colour=0xFF0000,
				timestamp=datetime.utcnow())
			await ctx.send(embed=embed)

		elif isinstance(exc, CheckFailure):
			embed = Embed(
				title="There was a problem",
				description="There was an unhandled command check error (probably missing privileges).",
				colour=0xFF0000,
				timestamp=datetime.utcnow())
			await ctx.send(embed=embed)

		elif hasattr(exc, "original"):
			if isinstance(exc.original, HTTPException):
				await ctx.send("There was a problem with discord (if muting, probably adding the role failed)")

			if isinstance(exc.original, Forbidden):
				embed = Embed(
					title="There was a problem",
					description="There was an unhandled command check error (probably missing privileges).",
					colour=0xFF0000,
					timestamp=datetime.utcnow())
				await ctx.send(embed=embed)

			else:
				raise exc.original

		else:
			raise exc

	async def on_ready(self):
		if not self.ready:
			self.bot_channel = self.get_channel(782694805720662026)

			await self.bot_channel.send("Now online")
			await self.bot_channel.send("------------------------------------------------------------")

			while not self.cogs_ready.all_ready():
				await sleep(0.1)

			print("Bot ready!")
		else:
			print("Bot connected")
	
	async def on_message(self, message):
		if not message.author.bot:
			if message.guild.id == 777500671922012170:
				# Books server
				if message.channel.id == 829961182752407592:
					# In the correct channel
					embed = Embed(
						title="New message",
						description=message.content,
						colour=message.author.colour,
						timestamp=datetime.utcnow())
					embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)

					books_portal = self.get_channel(829961274279985192)
					await books_portal.send(embed=embed)
			else:
				# Reubens server
				if message.channel.id == 829961274279985192:
					# In the correct channel
					embed = Embed(
						title="New message",
						description=message.content,
						colour=message.author.colour,
						timestamp=datetime.utcnow())
					embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)

					books_portal = self.get_channel(829961182752407592)
					await books_portal.send(embed=embed)

bot = Bot()
