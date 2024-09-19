import discord
from discord import app_commands
from discord.ext import commands

class hexadecimal(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

  @app_commands.command(name = "hexadecimal", description = "Encode/Decode a message in hexadecimal")
  @app_commands.describe(type="Would you like to encode or decode?")
  @app_commands.choices(type = [
    discord.app_commands.Choice(name="Encode", value="Encode"),
    discord.app_commands.Choice(name="Decode", value="Decode")
  ])
  async def hexadecimal(self, interaction: discord.Interaction, message: str, type: str):
    if type == "Decode":
      end_text = ""
      hexa_table = {'A':'10', 'B':'11', 'C':'12', 'D':'13', 'E':'14', 'F':'15'}
      hexa_table2 = {'a':'10', 'b':'11', 'c':'12', 'd':'13', 'e':'14', 'f':'15'}
      for letter in message.split():
        index = -1
        base10_list = []
        for digit in reversed(letter):
          index += 1
          if digit.isupper() == True:
            digit = hexa_table[digit]
          elif digit.islower() == True:
            digit = hexa_table2[digit]
          base10_char = 16**index*int(digit)
          base10_list.append(base10_char)
        base10_sum = sum(base10_list)
        end_text += chr(base10_sum)

      embed=discord.Embed(title="The decoded message is:", description=end_text, color=0x1ba300)
      embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
      await interaction.response.send_message(embed=embed)

    if type == "Encode":
      end_text = ""
      for char in message:
        end_text += hex(ord(char))[2:] + " "

      embed=discord.Embed(title="The encoded message is:", description=end_text, color=0x1ba300)
      embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
      await interaction.response.send_message(embed=embed)

async def setup(client: commands.Bot) -> None:
  await client.add_cog(hexadecimal(client))