import discord
from discord import app_commands
from discord.ext import commands
import pandas as pd
import numpy as np
import itertools
import string

english_words_set = set(line.strip() for line in open('EnglishWords.txt'))

def decrypt(key, message):
  global count
  message = message.replace(" ", "·")
  cyclesList = []
  blankList = [''] * len(message)
  generator = itertools.chain(range(key),range(key-2,0,-1))

  for i, x in enumerate(itertools.cycle(generator)):
    cyclesList.append(x)
    if i == len(message):
      break

  blank_array = np.full((key, len(message)), " ", dtype=str) 

  for i in range(len(message)):
    blank_array[cyclesList[i]][i] = "-" 

  count = 0
  def fill(row):
    global count
    for i in range(len(message)):
      if blank_array[row][i] == "-": 
        blank_array[row][i] = message[count]
        count += 1

  for i in range(key): 
    fill(i)

  initial_dataframe = pd.DataFrame(blank_array, columns=blankList) 
  initial_dataframe = initial_dataframe.to_string()

  decoded = ""
  for i in range(len(message)):
    decoded = decoded + blank_array[cyclesList[i]][i] 

  decoded = decoded.replace("·", " ")
  return decoded, initial_dataframe


class railfence(commands.Cog):
  def __init__(self, client):
    self.client = client

  @app_commands.command(name = "railfence", description = "Encode/Decode a message in Railfence Cipher")
  @app_commands.describe(type="Would you like to encode or decode?")
  @app_commands.choices(type = [
    discord.app_commands.Choice(name="Encode", value="Encode"),
    discord.app_commands.Choice(name="Decode", value="Decode")
  ])
  async def railfence(self, interaction: discord.Interaction, message: str, type: str, key: int = 0):
    if type == "Encode" and key > 0:
      message = message.replace(" ", "·")
      cyclesList = []
      blankList = [''] * len(message)
      generator = itertools.chain(range(key),range(key-2,0,-1))

      for i, x in enumerate(itertools.cycle(generator)):
        cyclesList.append(x)
        if i == len(message):
          break

      blank_array = np.full((key, len(message)), " ", dtype=str)

      for i in range(len(message)):
        blank_array[cyclesList[i]][i] = message[i]

      initial_dataframe = pd.DataFrame(blank_array, columns=blankList)
      initial_dataframe = initial_dataframe.to_string()

      encoded = blank_array.tolist() # 2d numpy array to 2d list
      encoded = [item for elem in encoded for item in elem]  # 2d list to 1d list
      encoded = ''.join(encoded)
      encoded = encoded.replace(" ", "")

      await interaction.response.send_message("**The encoded messsage is: **\n" + encoded + "```\n" + initial_dataframe + "```")

    elif type == "Encode" and key <= 0:
      error_embed = discord.Embed(title="You need a key to encode!", color=0xff0000)
      error_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
      await interaction.response.send_message(embed=error_embed)

    elif type == "Decode" and key > 0:
      decoded, initial_dataframe = decrypt(key, message)
      embed=discord.Embed(title="The decoded message is: ", description=decoded, color=0x1ba300)
      embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
      await interaction.response.send_message(content = "```" + initial_dataframe + "```", embed=embed)

    elif type == "Decode" and key == 0:
      found = False
      for i in range(1, len(message)):
        decoded, initial_dataframe = decrypt(i, message)
        decodedList = list(decoded.split())

        word_count = 0
        for word in decodedList:
          word = word.lower() 
          for character in string.punctuation:
            word = word.replace(character, '')
          if word in english_words_set:
            word_count += 1 

        if (word_count/len(decodedList)) >= 0.5:
          found = True
          break

      if found == True:
        embed=discord.Embed(title="The decoded message is: ", description=decoded, color=0x1ba300)
        embed.set_footer(text="The key was: " + str(i))
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
        await interaction.response.send_message(content = "```" + initial_dataframe + "```", embed=embed)
      else:
        error_embed = discord.Embed(title="No match in railfence could be found! It is possible that the decrypted message does not contain English words.", color=0xff0000)
        error_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
        await interaction.response.send_message(embed=error_embed)

async def setup(client):
  await client.add_cog(railfence(client))