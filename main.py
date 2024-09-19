import asyncio
import aiohttp
import random
import os

import discord
from discord import app_commands
from discord.ext import commands

token = "ODk5MTA5MTQzNzQ1NTI3ODI5.GTu-y3.AWA8z-JCWBSpHR4woETH7a6gpOx-GoxwyGPjj0"

client = commands.Bot(command_prefix = "&&", intents = discord.Intents.all())

@client.event
async def on_ready():
  print("We have logged in as {0.user}".format(client))
  # activeservers = client.guilds
  # for guild in activeservers:
  #   print(guild.name)
  try:
    synced = await client.tree.sync()
    print(f"Synced {len(synced)} commands")
  except Exception as e:
    print(e)

@client.tree.command(name = "ship", description = "<3")
async def ship(interaction: discord.Interaction):
  randNumber = random.randint(1, 3)

  if randNumber == 1:
    await interaction.response.send_message("https://cdn.discordapp.com/attachments/901665700333097081/1066615229246615643/image.png")

  elif randNumber == 2:
    await interaction.response.send_message("https://cdn.discordapp.com/attachments/782641749574549544/1112649214615359530/Untitled425_20230529125014.png")

  elif randNumber == 3:
    await interaction.response.send_message("https://cdn.discordapp.com/attachments/773997636545544222/959319246855372840/image0.png")

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