import discord
import aiohttp
from discord import app_commands
from discord.ext import commands

class Universe(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

  @app_commands.command(name="universe", description="Find all the subplaces within a Roblox game")
  async def universe(self, interaction: discord.Interaction, place_id: str):
    await interaction.response.defer()

    async with aiohttp.ClientSession() as session:
      universeID = await self.fetch_universe_id(session, place_id)
      all_places = await self.fetch_all_places(session, universeID)
      places_text = self.format_places(all_places)

    embed = discord.Embed(title="List of places:", description=places_text, color=0x1ba300)
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
    await interaction.followup.send(embed=embed)

  async def fetch_universe_id(self, session, place_id: str) -> str:
    url = f"https://apis.roblox.com/universes/v1/places/{place_id}/universe"
    async with session.get(url) as response:
      data = await response.json()
      return str(data["universeId"])

  async def fetch_all_places(self, session, universe_id: str) -> list:
    url = f"https://develop.roblox.com/v1/universes/{universe_id}/places?isUniverseCreation=false&limit=100&sortOrder=Asc"
    async with session.get(url) as response:
      data = await response.json()
      return data["data"]

  def format_places(self, places: list) -> str:
    formatted_text = ""
    for item in places:
      formatted_text += f"Name: {item['name']}\n"
      formatted_text += f"ID: {item['id']}\n\n"
    return formatted_text

async def setup(client: commands.Bot) -> None:
  await client.add_cog(Universe(client))

# import discord
# import requests
# import asyncio
# from discord import app_commands
# from discord.ext import commands
#
# class universe(commands.Cog):
#   def __init__(self, client: commands.Bot):
#     self.client = client
#
#   @app_commands.command(name = "universe", description = "Find all the subplaces within a Roblox game")
#   async def universe(self, interaction: discord.Interaction, place_id: str):
#     await interaction.response.defer()
#     await asyncio.sleep(4)
#     x = ""
#     universeID = requests.get("https://apis.roblox.com/universes/v1/places/" +
#                           place_id + "/universe").json()["universeId"]
#     universeID = str(universeID)
#     allPlaces = requests.get("https://develop.roblox.com/v1/universes/" + universeID + "/places?isUniverseCreation=false&limit=100&sortOrder=Asc").json()
#     for item in allPlaces["data"]:
#       x += "Name: " + item['name'] + "\n"
#       x += "ID: " + str(item['id']) + "\n\n"
#
#     embed=discord.Embed(title = "List of places: ", description=x, color=0x1ba300)
#     embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
#     await interaction.followup.send(embed=embed)
#
# async def setup(client: commands.Bot) -> None:
#   await client.add_cog(universe(client))