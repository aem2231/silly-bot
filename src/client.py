import discord
from discord import app_commands
from discord.ext import commands
import config
import os

cogs_path = "./src/cogs"
token = config.discordToken
giphyToken = config.giphyToken

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)
tree = client.tree

def setup_config():
  if not os.path.exists("data/"):
    os.mkdir("data")
setup_config()

@client.event
async def on_ready():
  print("Client is running!")
  cog_list = os.listdir(cogs_path)
  for cog in cog_list: # load all cogs in cogs/ directory
    if cog.endswith(".py"):
      try:
        await client.load_extension(f"cogs.{cog[:-3]}")
        print(f"{cog[:-3]} cog loaded successfully.")
      except Exception as e:
        print(f"Failed to load {cog[:-3]} cog: {e}")
  _ = await tree.sync()

@client.tree.command(name="echo", description="Echoes a message.")
@app_commands.describe(message="The message to echo.")
async def echo(interaction: discord.Interaction, message: str) -> None:
  _ = await interaction.response.send_message(message)

client.run(config.discordToken)
