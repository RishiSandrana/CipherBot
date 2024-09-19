import discord
from discord import app_commands
from discord.ext import commands
import pandas as pd
import re

class polybius(commands.Cog):
  def __init__(self, client):
    self.client = client

  @app_commands.command(name = "polybius", description = "Encode/Decode a message in Polybius Square Cipher")
  @app_commands.describe(type="Would you like to encode or decode?")
  @app_commands.choices(type = [
    discord.app_commands.Choice(name="Encode", value="Encode"),
    discord.app_commands.Choice(name="Decode", value="Decode")
  ])
  async def polybius(self, interaction: discord.Interaction, message: str, type: str):
    if type == "Encode":
      arg = message.split()

      df = pd.DataFrame({'1': ["A", "B", "C", "D", "E"],
                       '2': ["F", "G", "H", "I/J", "K"],
                       '3': ["L", "M", "N", "O", "P"],
                       '4': ["Q", "R", "S", "T", "U"],                         
                        '5': ["V", "W", "X", "Y", "Z"]},
                      index=['1', '2', '3', '4', '5'])

      df = df.transpose()
      encoded = ""
      for l in arg:
        for char in l:
          if char == "j" or char == "J":
            encoded = encoded + "24"
          elif char == "i" or char == "I":
            encoded = encoded + "24"
          else:
            char = char.upper()
            series = df[df.isin([char])].stack()
            series = series.to_string()
            series = re.sub("[^0-9]", "", series)
            encoded = encoded + series
          encoded += " "
        encoded += "  "

      embed=discord.Embed(title="The encoded message is:",description=encoded, color=0x1ba300)
      embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
      await interaction.response.send_message(embed=embed)

    elif type == "Decode":
      message = message.replace(" ", "")
      n = 2
      message = [message[i:i+n] for i in range(0, len(message), n)]
      df = pd.DataFrame({'1': ["A", "B", "C", "D", "E"],
                       '2': ["F", "G", "H", "I/J", "K"],
                       '3': ["L", "M", "N", "O", "P"],
                       '4': ["Q", "R", "S", "T", "U"],                           
                       '5': ["V", "W", "X", "Y", "Z"]},
                      index=['1', '2', '3', '4', '5'])

      df = df.transpose()

      def decrypt(letter):
        decoded = ""
        for element in message:
          if element == "24":
            decoded += letter
          else:
            row = element[0]
            column = element[1]
            pos = df.iat[int(row)-1, int(column)-1]
            decoded += pos
        return decoded

      decoded1 = decrypt("I")
      decoded2 = decrypt("J")

      embed=discord.Embed(title="Your possible decryptions: ", description=decoded1 + "\n" + decoded2, color=0x1ba300)
      embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
      await interaction.response.send_message(embed=embed)

async def setup(client: commands.Bot) -> None:
  await client.add_cog(polybius(client))  