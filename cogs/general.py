from discord.ext import commands

class General(object):
	"""General commands"""
	def __init__(self, bot):
		self.bot = bot

	async def on_ready(self):
		print("General commands loaded")

	@commands.command()
	async def ping(self):
		await self.bot.say("Test!")

def setup(bot):
	bot.add_cog(General(bot))