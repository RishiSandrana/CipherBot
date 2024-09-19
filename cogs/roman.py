import discord
import roman as r
from discord import app_commands
from discord.ext import commands

class roman(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

  @app_commands.command(name = "roman", description = "Encode/Decode a message in Roman Numerals")
  @app_commands.describe(type="Would you like to encode or decode?")
  @app_commands.choices(type = [
    discord.app_commands.Choice(name="Encode", value="Encode"),
    discord.app_commands.Choice(name="Decode", value="Decode")
  ])
  async def roman(self, interaction: discord.Interaction, message: str, type: str):
    if type == "Decode":
      message = message.split()
      end = ""

      for number in message:
        end += str(r.fromRoman(number)) + " "

      embed=discord.Embed(title="The decoded message is:", description=end, color=0x1ba300)
      embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
      await interaction.response.send_message(embed=embed)

    if type == "Encode":
      end = ""

      for number in message.split():
        number = int(number)
        end += str(roman.toRoman(number)) + " "

      embed = discord.Embed(title="The encoded message is:", description=end, color=0x1ba300)
      embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
      await interaction.response.send_message(embed=embed)

async def setup(client: commands.Bot) -> None:
  await client.add_cog(roman(client))