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
		self.coin_ids = {}

		r = requests.get("https://api.coingecko.com/api/v3/coins/list")
		data = r.json()

		for coin in data:
			self.tickers[coin["symbol"]] = coin["id"]
			self.coin_ids[coin["id"]] = coin["symbol"]

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

		if not ticker in self.tickers and not ticker in self.coin_ids:
			print("Invalid ticker")
			return

		if ticker in self.tickers:
			coin_id = self.tickers[ticker]
		else:
			coin_id = ticker
		
		r = requests.get("https://api.coingecko.com/api/v3/coins/"+coin_id)
		data = r.json()

		current_price = "$"+format(data["market_data"]["current_price"]["usd"], ",f")
		image = data["image"]["thumb"]

		price_change = round(data["market_data"]["price_change_percentage_24h"], 2)

		color = 0x0de358 if price_change > 0 else 0xff0000

		current_price += " ("+str(price_change)+"%)"

		symbol = data["symbol"].upper()

		embed=discord.Embed(title=current_price, color=color)
		embed.set_author(name=symbol, icon_url=image)
		await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(General(bot))