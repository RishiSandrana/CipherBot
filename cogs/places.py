import discord
import aiohttp
from discord import app_commands
from discord.ext import commands

class Places(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

  @app_commands.command(name="places", description="Find all the public places created by a user")
  async def places(self, interaction: discord.Interaction, username: str):
    await interaction.response.defer()

    async with aiohttp.ClientSession() as session:
      url = "https://users.roblox.com/v1/usernames/users"
      async with session.post(url, json={"usernames": [username]}) as response:
        user_data = await response.json()
        userID = user_data['data'][0]['id']

      y = ""
      async with session.get(
              f"https://games.roblox.com/v2/users/{userID}/games?accessFilter=2&limit=50&sortOrder=Asc") as response:
        all_places = await response.json()
        for item in all_places["data"]:
          y += f"Name: {item['name']}\n"
          y += f"Visits: {item['placeVisits']}\n"
          y += f"ID: {item['rootPlace']['id']}\n\n"

    embed = discord.Embed(title="List of places:", description=y, color=0x1ba300)
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
    await interaction.followup.send(embed=embed)

async def setup(client: commands.Bot) -> None:
  await client.add_cog(Places(client))

# import discord
# import requests
# import asyncio
# from discord import app_commands
# from discord.ext import commands
#
# class places(commands.Cog):
#   def __init__(self, client: commands.Bot):
#     self.client = client
#
#   @app_commands.command(name = "places", description = "Find all the public places created by a user")
#   async def places(self, interaction: discord.Interaction, username: str):
#     await interaction.response.defer()
#     await asyncio.sleep(4)
#     url = "https://users.roblox.com/v1/usernames/users"
#     x = requests.post(url, json = {"usernames": [username]})
#     userID = x.json()['data'][0]['id']
#
#     y = ""
#     allPlaces = requests.get("https://games.roblox.com/v2/users/" + str(userID) + "/games?accessFilter=2&limit=50&sortOrder=Asc").json()
#     for item in allPlaces["data"]:
#       y += "Name: " + item['name'] + "\n"
#       y += "Visits: " + str(item['placeVisits']) + "\n"
#       y += "ID: " + str(item['rootPlace']['id']) + "\n\n"
#
#     embed=discord.Embed(title = "List of places: ", description=y, color=0x1ba300)
#     embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
#     await interaction.followup.send(embed=embed)
#
# async def setup(client: commands.Bot) -> None:
#   await client.add_cog(places(client))