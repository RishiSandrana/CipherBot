import asyncio
import aiohttp
import random
import os
import logging

import discord
from discord import app_commands
from discord.ext import commands
from keep_alive import keep_alive

keep_alive()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

token = os.environ.get('token')

client = commands.Bot(command_prefix = "", intents = discord.Intents.default())

@client.event
async def on_ready():
  logger.info("We have logged in as %s", client.user)
  # print("We have logged in as {0.user}".format(client))
  # activeservers = client.guilds
  # for guild in activeservers:
  #   print(guild.name)
  try:
    synced = await client.tree.sync()
    # print(f"Synced {len(synced)} commands")
    logger.info("Synced %d commands", len(synced))
  except Exception as e:
    # print(e)
    logger.exception("Error syncing commands: %s", e)

@client.tree.command(name = "help", description = "Document with all the commands!")
async def help(interaction: discord.Interaction):
  await interaction.response.send_message("https://docs.google.com/document/d/1jOs-9klLJfeVkBwajwTBeUbqumI_U8bP8oFuUKnNuKA/edit?usp=sharing")

async def load():
  for file in os.listdir("./cogs"):
    if file.endswith(".py"):
      await client.load_extension(f'cogs.{file[:-3]}')

async def main():
  await load()
  await client.start(token)

asyncio.run(main())
