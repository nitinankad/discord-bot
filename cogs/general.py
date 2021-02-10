import discord
from discord.ext import commands
import requests
import json

class General(commands.Cog):
	"""General commands"""
	def __init__(self, bot):
		self.bot = bot

		# Load crypto info
		self.tickers = {}

		r = requests.get("https://api.coingecko.com/api/v3/coins/list")
		data = r.json()

		for coin in data:
			self.tickers[coin["symbol"]] = coin["id"]

	async def on_ready(self):
		print("General commands loaded")

	@commands.command()
	async def say(self, ctx, *, message):
		await ctx.send(message)

	# Fetch Bitcoin price
	@commands.command()
	async def btc(self, ctx):
		api = "http://preev.com/pulse/units:btc+usd/sources:bitstamp+kraken"

		r = requests.get(api)
		data = json.loads(r.text)

		price = data["btc"]["usd"]["bitstamp"]["last"]
		price = "${:,}".format(float(price))

		embed=discord.Embed(title="Current Bitcoin price", description=price, color=0x0de358)
		await ctx.send(embed=embed)

	@commands.command(aliases=["p"])
	async def crypto(self, ctx, *, ticker):
		ticker = ticker.lower()

		if not ticker in self.tickers:
			print("Invalid ticker")
			return

		coin_id = self.tickers[ticker]
		
		r = requests.get("https://api.coingecko.com/api/v3/coins/"+coin_id)
		data = r.json()

		current_price = "$"+format(data["market_data"]["current_price"]["usd"], ",f")
		image = data["image"]["thumb"]

		embed=discord.Embed(title=ticker.upper(), description=current_price, color=0x0de358)
		embed.set_thumbnail(url=image)
		await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(General(bot))