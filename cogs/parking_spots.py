from discord.ext import commands
import discord
from bs4 import BeautifulSoup as bs
import urllib.request as urllib

class ParkingSpots(commands.Cog):
	'''
		Loads avaliable parking spots in the UTD parking structures
	'''
	def __init__(self, bot):
		self.bot = bot

	async def on_ready(self):
		print("ParkingSpots commands loaded")

	@commands.command(aliases=["park"])
	async def parking(self, ctx):
		data = urllib.urlopen(urllib.Request("https://www.utdallas.edu/services/transit/garages/_code.php", headers={"User-Agent": "Mozilla/5.0"})).read()

		soup = bs(data, features="html5lib")

		parking_structures = soup.findAll("table")

		embed = discord.Embed(color=0x0de358)

		for ps in parking_structures:
			body = ps.findAll("tbody")[0]
			spots = body.findAll("td")

			ps_name = ps.findAll("caption")[0].text

			green_level_5 = spots[2].text

			gold_level_4 = spots[5].text
			gold_level_3 = spots[8].text

			orange_level_3 = spots[11].text
			orange_level_2 = spots[14].text

			output = (
						"Level 5 Green: " + green_level_5 + "\n"
						"Level 4 Gold: " + gold_level_4 + "\n"
						"Level 3 Gold: " + gold_level_3 + "\n"
						"Level 3 Orange: " + orange_level_3 + "\n"
						"Level 2 Orange: " + orange_level_2 + "\n"
					)

			embed.add_field(name=ps_name, value=output, inline=True)

		await ctx.send(embed=embed)




def setup(bot):
	bot.add_cog(ParkingSpots(bot))