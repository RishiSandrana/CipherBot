import discord
from discord import app_commands
from discord.ext import commands

class atbash(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

  @app_commands.command(name = "atbash", description = "Convert a message in atbash")
  async def atbash(self, interaction: discord.Interaction, message: str):
    end_message = ""
    lookup_table1 = {'A' : 'Z', 'B' : 'Y', 'C' : 'X', 'D' : 'W', 'E' : 'V',
        'F' : 'U', 'G' : 'T', 'H' : 'S', 'I' : 'R', 'J' : 'Q',
        'K' : 'P', 'L' : 'O', 'M' : 'N', 'N' : 'M', 'O' : 'L',
        'P' : 'K', 'Q' : 'J', 'R' : 'I', 'S' : 'H', 'T' : 'G',
        'U' : 'F', 'V' : 'E', 'W' : 'D', 'X' : 'C', 'Y' : 'B', 'Z' : 'A'}
    lookup_table2 = {'a' : 'z', 'b' : 'y', 'c' : 'x', 'd' : 'w', 'e' : 'v',
        'f' : 'u', 'g' : 't', 'h' : 's', 'i' : 'r', 'j' : 'q',
        'k' : 'p', 'l' : 'o', 'm' : 'n', 'n' : 'm', 'o' : 'l',
        'p' : 'k', 'q' : 'j', 'r' : 'i', 's' : 'h', 't' : 'g',
        'u' : 'f', 'v' : 'e', 'w' : 'd', 'x' : 'c', 'y' : 'b', 'z' : 'a'}

    for char in message:
      if char in lookup_table1:
        end_message = end_message + lookup_table1[char]
      elif char in lookup_table2:
        end_message = end_message + lookup_table2[char]
      else:
        end_message = end_message + char

    embed=discord.Embed(title="The converted message is:", description=end_message, color=0x1ba300)
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
    await interaction.response.send_message(embed=embed)

async def setup(client: commands.Bot) -> None:
  await client.add_cog(atbash(client))