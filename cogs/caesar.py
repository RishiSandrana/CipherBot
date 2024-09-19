import discord
import re
from discord import app_commands
from discord.ext import commands

from caesarcipher import CaesarCipher

english_words_set = set(line.strip() for line in open('EnglishWords.txt'))

alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
            'w', 'x', 'y', 'z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r',
            's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

alphabet2 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
             'W', 'X', 'Y', 'Z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
             'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

class caesar(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

  @app_commands.command(name = "caesar", description = "Encode/Decode a message in Caesar Cipher (ROT)")
  @app_commands.describe(type="Would you like to encode or decode?")
  @app_commands.choices(type = [
    discord.app_commands.Choice(name="Encode", value="Encode"),
    discord.app_commands.Choice(name="Decode", value="Decode")
  ])
  async def caesar(self, interaction: discord.Interaction, message: str, type: str, shift_number: int = -1):
    if type == "Decode" and shift_number == -1:
      counter_list = []
      total_list_to_check = []
      error_list = []

      for x in range(0,26):
        y = 0
        shift = x
        end_text = ""

        for char in message:
          if char in alphabet:
            position = alphabet.index(char)
            new_position = position - shift
            end_text += alphabet[new_position]
          elif char in alphabet2:
            position = alphabet2.index(char)
            new_position = position - shift
            end_text += alphabet2[new_position]
          else:
            end_text += char

          list_to_check = str.split(end_text)

        for word in list_to_check:
          res = re.sub(r'[^\w\s]', '', word)
          if res.isalpha() == True:
            word2 = res.lower()
            if word2 in english_words_set:
              y += 1
        counter_list.append(y)
        total_list_to_check.append(list_to_check)

      maximum_number = max(counter_list)
      z = -1
      error = True

      for num in counter_list:
        z += 1
        if num == maximum_number and num != 0:
          error = False
          embed=discord.Embed(title="The decoded message is:", description=' '. join(total_list_to_check[z]), color=0x1ba300)
          embed.set_footer(text="The shift number is: " + str(z))
          embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
          await interaction.response.send_message(embed=embed)
        else:
          error_list.append((' '. join(total_list_to_check[z])))

      if error == True:
        error_embed=discord.Embed(title="No match in Caesar was found! Here are all the possible outcomes: \n", description=('\n'.join(error_list)), color=0xff0000)
        error_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
        await interaction.response.send_message(embed=error_embed)

    elif type == "Decode" and shift_number != -1:
      cipher = CaesarCipher(message, offset=shift_number)

      embed=discord.Embed(title="The decoded message is:", description=cipher.decoded, color=0x1ba300)
      embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
      await interaction.response.send_message(embed=embed)

    elif type == "Encode" and shift_number > -1:
      cipher = CaesarCipher(message, offset=shift_number)

      embed=discord.Embed(title="The encoded message is:", description=cipher.encoded, color=0x1ba300)
      embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
      await interaction.response.send_message(embed=embed)

    elif type == "Encode" and shift_number <= -1:
      error_embed = discord.Embed(title="You need a key to encode!", color=0xff0000)
      error_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
      await interaction.response.send_message(embed=error_embed)

async def setup(client: commands.Bot) -> None:
  await client.add_cog(caesar(client))