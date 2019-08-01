import discord
from discord.ext import commands
from glob import glob

bot = commands.Bot(command_prefix="!", description="Bot")

@bot.event
async def on_ready():
	print('Logged in as {0.user}'.format(bot))
	print(discord.__version__)

# Loads all commands from the cogs directory
for cog in glob("cogs/*.py"):
	cog = cog.split("cogs\\")[1].split(".py")[0]
	bot.load_extension("cogs.{0}".format(cog))

login_file = open("login.txt", "r")
username, password = login_file.read().strip("\n").split(":")
login_file.close()

bot.run(username, password, bot=False)