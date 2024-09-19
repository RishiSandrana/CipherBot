import discord
from discord import app_commands
from discord.ext import commands

class octal(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

  @app_commands.command(name = "octal", description = "Encode/Decode a message in octal")
  @app_commands.describe(type="Would you like to encode or decode?")
  @app_commands.choices(type = [
    discord.app_commands.Choice(name="Encode", value="Encode"),
    discord.app_commands.Choice(name="Decode", value="Decode")
  ])
  async def octal(self, interaction: discord.Interaction, message: str, type: str):
    if type == "Decode":
      end_text = ""
      for letter in message.split():
        decimal_value = int(letter, 8)
        character = chr(decimal_value)
        end_text += character

      embed=discord.Embed(title="The decoded message is:", description=end_text, color=0x1ba300)
      embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
      await interaction.response.send_message(embed=embed)

    elif type == "Encode":
      end_text = ""
      for char in message:
        end_text += oct(ord(char))[2:] + " "

      embed=discord.Embed(title="The encoded message is:", description=end_text, color=0x1ba300)
      embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
      await interaction.response.send_message(embed=embed)

async def setup(client: commands.Bot) -> None:
  await client.add_cog(octal(client))