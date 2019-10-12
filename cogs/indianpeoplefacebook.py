from discord.ext import commands
import requests
import discord
import json

class IndianPeopleFacebook(commands.Cog):
	'''
		Fetches a random post from r/indianpeoplefacebook
	'''
	def __init__(self, bot):
		self.bot = bot

	async def on_ready(self):
		print("IndianPeopleFacebook command loaded")

	@commands.command(aliases=["ipf"])
	async def indianpeoplefacebook(self, ctx):
		r = requests.get("https://www.reddit.com/r/indianpeoplefacebook/random.json", headers={"User-Agent": "Mozilla/5.0"})
		data = json.loads(r.text)[0]["data"]["children"][0]["data"]

		title = data["title"]
		image_link = data["url"]
		upvotes = data["ups"]

		embed = discord.Embed(color=0x0de358, title=title)
		embed.set_image(url=image_link)
		embed.set_footer(text="%s upvotes" % (upvotes))

		await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(IndianPeopleFacebook(bot))