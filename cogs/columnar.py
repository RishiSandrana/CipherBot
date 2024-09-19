import discord
import pandas as pd
import math
import numpy as np
import itertools
import asyncio
from discord import app_commands
from discord.ext import commands

english_words_set = set(line.strip() for line in open('EnglishWords.txt'))
punc = '''!()-[]{};:'"<>/@#$%^&*_~'''

def numberSorter(wordList):
      count = 1
      sortedList = sorted(wordList)
      splitList = [[el] for el in sortedList]

      for l in splitList:
        l.insert(0, count)
        count += 1

      numberSorter.numberList = []
      for char in wordList:
        for l in splitList:
          if char in set(l):
            numberSorter.numberList.append(l[0])
            splitList.remove(l)

def columnSearcher(num, length1, length2, array, l): 
      for i in range(length1):
        if array[0][i] == str(num):
          for x in range(1, length2 + 1):
            for index, value in enumerate(l):
              if array[x][i] == "":
                array[x][i] = l[index]
                l.pop(index)

def checkKey(bigList, message): 
  final_decoded = None
  possibleKeys = []
  totalCount = 0

  for thing in bigList:
    initial_dataframe = None
    totalCount += 1 

    if type(thing) == type("str"):
      if len(thing) <= 7:
        continue
      numberSorter(thing)
      thing = numberSorter.numberList

    #print("The program has run through this many keys: " + str(totalCount), end = "\r")
    smallList = list(thing)
    columnLength = len(smallList)
    rowLength = math.ceil(len(message) / len(smallList))
    messageList = list(message)

    blank_array = np.empty([rowLength, columnLength], dtype=str)
    blank_array = np.insert(blank_array, 0, smallList, axis=0)

    for i in range(rowLength * columnLength - len(messageList)):
      index = columnLength - i
      blank_array[rowLength][index - 1] = "*"

    for i in range(columnLength):
      columnSearcher(i + 1, columnLength, rowLength, blank_array, messageList)

    blank_array = np.delete(blank_array, 0, axis=0)
    decoded = blank_array.tolist()  # 2d numpy array to 2d list
    decoded = [item for elem in decoded for item in elem]  # 2d list to 1d list
    decoded = [value for value in decoded if value != '*']
    decoded = ''.join(decoded)
    decoded_list = decoded.split()

    # Checks if the decoded message has English words
    word_count = 0
    for word in decoded_list:
      word = word.lower()
      for character in punc:
        word = word.replace(character, '')
      if word in english_words_set:
        word_count += 1
        print(word)
        
    print(decoded_list)
    print(word_count)

    if (word_count / len(decoded_list)) >= 0.75:
      # print(decoded)
      final_decoded = decoded
      break

  if final_decoded is not None:
    for key in english_words_set:
      keyList = list(key)

      numberSorter(keyList)
      if numberSorter.numberList == smallList:
        possibleKeys.append(key)

  return final_decoded, possibleKeys, initial_dataframe

def encode(message, key):
  numberSorter(list(key))
  numberedKeyList = numberSorter.numberList
  keyList = list(key)

  columnLength = len(key)
  rowLength = math.ceil(len(message)/len(key))

  messageList = list(message)

  if len(messageList) != (columnLength*rowLength):
    while True:
        messageList.append("")
        if len(messageList) == columnLength*rowLength:
            break

    np_array = np.array(messageList)
    np_array = np.insert(np_array, 0, keyList, axis = 0)

    reshaped_array = np.reshape(np_array, (rowLength + 1, columnLength))

    master_list = []
    for i in range(columnLength):
        x = reshaped_array[:,i].tolist()
        master_list.append(x)

    for index, l in enumerate(master_list):
      l.insert(0, numberedKeyList[index])

    master_list = sorted(master_list)

    for small_list in master_list: #Removes the corresponding key letter
      small_list.pop(0)
      small_list.pop(0)

    master_list = [item for elem in master_list for item in elem] #Converts nested list into one list
    encoded = ''.join(master_list) #Converts the list into a string

    np_array2 = np.array(messageList)
    reshaped_array2 = np.reshape(np_array2, (rowLength, columnLength))

    initial_dataframe = pd.DataFrame(reshaped_array2, columns = keyList)
    initial_dataframe = initial_dataframe.to_string()

  return encoded, initial_dataframe

class columnar(commands.Cog):
  def __init__(self, client):
    self.client = client

  @app_commands.command(name = "columnar", description = "Encode/Decode a message in Columnar Transposition Cipher")
  @app_commands.describe(type="Would you like to encode or decode?")
  @app_commands.choices(type = [
    discord.app_commands.Choice(name="Encode", value="Encode"),
    discord.app_commands.Choice(name="Decode", value="Decode")
  ])
  async def columnar(self, interaction: discord.Interaction, message: str, type: str, key: str = ""):
    if type == "Encode" and key != "":
      encoded, grid = encode(message, key)
      await interaction.response.send_message("**The encoded messsage is: **\n" + encoded + "```\n" + grid + "```")

    elif type == "Encode" and key == "":
      error_embed = discord.Embed(title="You need a key to encode!", color=0xff0000)
      error_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
      await interaction.response.send_message(embed=error_embed)

    elif type == "Decode":
      await interaction.response.defer()
      await asyncio.sleep(4)

      listOne = list(itertools.permutations([1]))
      listTwo = list(itertools.permutations([1, 2]))
      listThree = list(itertools.permutations([1, 2, 3]))
      listFour = list(itertools.permutations([1, 2, 3, 4]))
      listFive = list(itertools.permutations([1, 2, 3, 4, 5]))
      listSix = list(itertools.permutations([1, 2, 3, 4, 5, 6]))
      listSeven = list(itertools.permutations([1, 2, 3, 4, 5, 6, 7]))
      masterList = listOne + listTwo + listThree + listFour + listFive + listSix + listSeven

      final_decoded, possibleKeys, initial_dataframe = checkKey(masterList, message)

      if final_decoded is None:
        error_embed=discord.Embed(title="No match in Columnar could be found! It's possible that your key is not in the scope of this program.", color=0xff0000)
        error_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
        await interaction.response.send_message(embed=error_embed)
      else:
        embed=discord.Embed(title="The decoded message is: ", description=final_decoded, color=0x1ba300)
        possibleKeys = sorted(possibleKeys)
        embed.set_footer(text="Your list of possible keys: " + str(possibleKeys))
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
        await interaction.followup.send(embed=embed)

async def setup(client):
  await client.add_cog(columnar(client))