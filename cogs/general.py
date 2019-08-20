import discord
from discord.ext import commands
import requests
import json

class General(commands.Cog):
	"""General commands"""
	def __init__(self, bot):
		self.bot = bot

	async def on_ready(self):
		print("General commands loaded")

	@commands.command()
	async def say(self, *, message):
		await self.bot.say(message)

	# Fetch Bitcoin price
	@commands.command()
	async def btc(self):
		api = "http://preev.com/pulse/units:btc+usd/sources:bitstamp+kraken"

		r = requests.get(api)
		data = json.loads(r.text)

		price = data["btc"]["usd"]["bitstamp"]["last"]
		price = "${:,}".format(float(price))

		embed=discord.Embed(title="Current Bitcoin price", description=price, color=0x0de358)
		await self.bot.say(embed=embed)

def setup(bot):
	bot.add_cog(General(bot))