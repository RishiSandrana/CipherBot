import discord
from discord import app_commands
from discord.ext import commands

class a1z26(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

  @app_commands.command(name = "a1z26", description = "Encode/Decode a message in A1Z26")
  @app_commands.describe(type="Would you like to encode or decode?")
  @app_commands.choices(type = [
    discord.app_commands.Choice(name="Encode", value="Encode"),
    discord.app_commands.Choice(name="Decode", value="Decode")
  ])
  async def a1z26(self, interaction: discord.Interaction, message: str, type: str):
    if type == "Decode":
      end_text = ""
      for char in message.split():
        if char.isdigit() and char != "26":
          num = ((int(char) % 26) + 96)
          char = chr(num)
          end_text += char
        elif char.isdigit() and char == "26":
          end_text += "z"
        else:
          end_text += char

      embed=discord.Embed(title="The decoded message is:", description=end_text, color=0x1ba300)
      embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
      await interaction.response.send_message(embed=embed)

    elif type == "Encode":
      end_text = ""
      for char in message:
        if char.isalpha():
          num = ord(char.lower()) - 96
          if 1 <= num <= 26:
            end_text += str(num) + " "
        else:
            end_text += char

      embed=discord.Embed(title="The encoded message is:", description=end_text, color=0x1ba300)
      embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
      await interaction.response.send_message(embed=embed)

async def setup(client: commands.Bot) -> None:
  await client.add_cog(a1z26(client))