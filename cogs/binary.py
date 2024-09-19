import discord
from discord import app_commands
from discord.ext import commands

import binascii

class binary(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

  @app_commands.command(name = "binary", description = "Encode/Decode a message in binary")
  @app_commands.describe(type="Would you like to encode or decode?")
  @app_commands.choices(type = [
    discord.app_commands.Choice(name="Encode", value="Encode"),
    discord.app_commands.Choice(name="Decode", value="Decode")
  ])
  async def binary(self, interaction: discord.Interaction, message: str, type: str):
    if type == "Decode":
      binary_string = message.replace(" ", "")
      binary_bytes = binascii.unhexlify('%x' % int(binary_string, 2))
      end_text = binary_bytes.decode('utf-8')

      embed=discord.Embed(title="The decoded message is:", description=end_text, color=0x1ba300)
      embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
      await interaction.response.send_message(embed=embed)

    elif type == "Encode":
      encoded_bytes = message.encode('utf-8')
      binary_string = bin(int(binascii.hexlify(encoded_bytes), 16))[2:]
      binary_string = ' '.join([binary_string[i:i+8] for i in range(0, len(binary_string), 8)])

      embed=discord.Embed(title="The encoded message is:", description=binary_string, color=0x1ba300)
      embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
      await interaction.response.send_message(embed=embed)

async def setup(client: commands.Bot) -> None:
  await client.add_cog(binary(client))