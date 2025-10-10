import discord
from discord.ext import commands
import config as config
import os

cogs_path = "./src/cogs"
token = config.discordToken
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(intents=intents, command_prefix="?", description="I just got so emo I fell apart.")

def config():
    if os.path.exists("data/") == False:
        os.mkdir("data")

config()

@client.event
async def on_ready():
    print("Client is running!")
    await loadCogs()

#try:
client.run(token)
#except:
    #print("Plase paste your tokens and api keys in the tokens.json file")

#i use nixOS btw
