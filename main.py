import discord
from discord.ext import commands
from glob import glob
import os

bot = commands.Bot(command_prefix="!", description="Bot")

@bot.event
async def on_ready():
	print('Logged in as {0.user}'.format(bot))
	print(discord.__version__)

# Loads all commands from the cogs directory
cogs = [i for i in os.listdir("cogs") if i.endswith(".py")]

for cog in cogs:
	cog_name = cog.split(".py")[0]
	bot.load_extension("cogs.{0}".format(cog_name))


token_file = open("token.txt", "r")
token = token_file.read().strip("\n")
token_file.close()

# bot.run(username, password, bot=False)
bot.run(token, bot=False)