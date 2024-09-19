import discord
from discord import app_commands
from discord.ext import commands

morseDict = {'A':'.-', 'B':'-...', 'C':'-.-.', 'D':'-..', 'E':'.', 'F':'..-.', 'G':'--.', 'H':'....', 'I':'..', 'J':'.---', 'K':'-.-', 'L':'.-..', 'M':'--', 'N':'-.','O':'---', 'P':'.--.', 'Q':'--.-','R':'.-.', 'S':'...', 'T':'-', 'U':'..-', 'V':'...-', 'W':'.--', 'X':'-..-', 'Y':'-.--', 'Z':'--..', '1':'.----', '2':'..---', '3':'...--', '4':'....-', '5':'.....', '6':'-....', '7':'--...', '8':'---..', '9':'----.','0':'-----', ', ':'--..--', '.':'.-.-.-', '?':'..--..', '/':'-..-.', '-':'-....-', '(':'-.--.', ')':'-.--.-'}

class morse(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

  @app_commands.command(name = "morse", description = "Encode/Decode a message in Morse Code")
  @app_commands.describe(type="Would you like to encode or decode?")
  @app_commands.choices(type = [
    discord.app_commands.Choice(name="Encode", value="Encode"),
    discord.app_commands.Choice(name="Decode", value="Decode")
  ])
  async def morse(self, interaction: discord.Interaction, message: str, type: str):
    if type == "Decode":
      message = message.split()
      decrypted = []

      for element in message:
        if element == "/":
          decrypted.append(" ")
        else:
          for key, value in morseDict.items():
            if element == value:
              decrypted.append(key)

      decrypted = ''.join(decrypted)
      embed=discord.Embed(title="The decoded message is:", description=decrypted, color=0x1ba300)
      embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
      await interaction.response.send_message(embed=embed)

    if type == "Encode":
      encoded = []

      for char in message:
        if char.upper() in morseDict:
          encoded.append(morseDict[char.upper()])
          encoded.append(" ")

      encoded_message = ''.join(encoded)
      embed = discord.Embed(title="The encoded message is:", description=encoded_message, color=0x1ba300)
      embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
      await interaction.response.send_message(embed=embed)

async def setup(client: commands.Bot) -> None:
  await client.add_cog(morse(client))