import discord
from discord.ext import commands
import config
import os

cogs_path = "./src/cogs"
token = config.discordToken
giphyToken = config.giphyToken
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(intents=intents, command_prefix="?", description="I just got so emo I fell apart.")

def config():
    if not os.path.exists("data/"):
        os.mkdir("data")
config()

@client.event
async def on_ready():
    print("Client is running!")
    for guild in client.guilds:
        for channel in guild.text_channels:
            if channel.name == 'general':
                await channel.send('Hello world!')
                break

client.run(token)
