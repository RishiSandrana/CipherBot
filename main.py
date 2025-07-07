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

@client.tree.command(name = "ship", description = "<3")
async def ship(interaction: discord.Interaction):
  randNumber = random.randint(1, 4)

  if randNumber == 1:
    await interaction.response.send_message("https://cdn.discordapp.com/attachments/901665700333097081/1066615229246615643/image.png")

  elif randNumber == 2:
    await interaction.response.send_message("https://cdn.discordapp.com/attachments/782641749574549544/1112649214615359530/Untitled425_20230529125014.png")

  elif randNumber == 3:
    await interaction.response.send_message("https://cdn.discordapp.com/attachments/773997636545544222/959319246855372840/image0.png")

  elif randNumber == 4:
    await interaction.response.send_message("https://cdn.discordapp.com/attachments/949016494308749392/1278204526813515776/Untitled120_20240828000758.png?ex=66f1927b&is=66f040fb&hm=a8d8aa9cbfcb09ae6f0df15f2d89acf11049c7681d9372495573e8820b259682&")

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
