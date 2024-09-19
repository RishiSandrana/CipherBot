import discord
from discord import app_commands
from discord.ext import commands

import base64
import math

class bases(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

  @app_commands.command(name = "bases", description = "Encode/Decode a message in Base64, Base32, or Ascii85")
  @app_commands.describe(type="Would you like to encode or decode?")
  @app_commands.choices(type = [
    discord.app_commands.Choice(name="Decode", value="Decode"),
    discord.app_commands.Choice(name="Encode - Base64", value="Encode - Base64"),
    discord.app_commands.Choice(name="Encode - Base32", value="Encode - Base32"),
    discord.app_commands.Choice(name="Encode - Ascii85", value="Encode - Ascii85")
  ])
  async def bases(self, interaction: discord.Interaction, message: str, type: str):
    if type == "Decode":
      try:
        message_64 = message + "=="
        decoded64 = base64.standard_b64decode(message_64)
        decoded64 = decoded64.decode('UTF-8')
        embed = discord.Embed(title="The decoded message is:", description=decoded64, color=0x1ba300)
        embed.set_footer(text="The cipher is Base64.")
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
        await interaction.response.send_message(embed=embed)
        return True
      except:
        pass 

      try:
        message_32 = message
        length = len(message_32)
        num_padding = (8 * math.ceil(length / 8)) - length

        for char in range(num_padding):
          message_32 += "="

        decoded32 = base64.b32decode(message_32)
        decoded32 = decoded32.decode('UTF-8')

        embed = discord.Embed(title="The decoded message is:", description=decoded32, color=0x1ba300)
        embed.set_footer(text="The cipher is Base32.")
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
        await interaction.response.send_message(embed=embed)
        return True
      except:
        pass

      try:
        decoded85 = base64.a85decode(message)
        decoded85 = decoded85.decode('UTF-8')
        embed = discord.Embed(title="The decoded message is:", description=decoded85, color=0x1ba300) 
        embed.set_footer(text="The cipher is Ascii85.")
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
        await interaction.response.send_message(embed=embed)
        return True
      except:
        error_embed = discord.Embed(title="No message could be found! Please try a different decryption.", color=0xff0000)
        error_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
        await interaction.response.send_message(embed=error_embed)

    elif type == "Encode - Base64":
      encoded64 = base64.b64encode(message.encode('utf-8')).decode('utf-8')
      embed = discord.Embed(title="The encoded message is:", description=encoded64, color=0x1ba300) 
      embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
      await interaction.response.send_message(embed=embed)

    elif type == "Encode - Base32":
      encoded32 = base64.b32encode(message.encode('utf-8')).decode('utf-8')
      embed = discord.Embed(title="The encoded message is:", description=encoded32, color=0x1ba300) 
      embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
      await interaction.response.send_message(embed=embed)

    elif type == "Encode - Ascii85":
      encoded85 = base64.a85encode(message.encode('utf-8')).decode('utf-8')
      embed = discord.Embed(title="The encoded message is:", description=encoded85, color=0x1ba300) 
      embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
      await interaction.response.send_message(embed=embed)

async def setup(client: commands.Bot) -> None:
  await client.add_cog(bases(client))