import discord
from discord.ext import commands
from reactionrnn import reactionrnn

# Predicts the mood probabilities of a given input
class React(object):
	def __init__(self, bot):
		self.bot = bot
		self.reaction = reactionrnn()

	async def on_ready(self):
		print("React command loaded")

	@commands.command()
	async def react(self, *, message):
		prediction = self.reaction.predict(message)

		embed = discord.Embed(title="Results", description="Message: %s" % (message), color=0x0de358)

		for mood in prediction:
			embed.add_field(name=mood, value=prediction[mood])

		await self.bot.say(embed=embed)

def setup(bot):
	bot.add_cog(React(bot))