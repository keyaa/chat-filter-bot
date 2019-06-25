import profanity_check as pc
import discord

client = discord.Client()

@client.event
async def on_ready():
  print("Successfully logged in as {0.user}.".format(client))

@client.event
async def on_message(message):
  if message.author == client.user: # don't reply to one's own messages
    return

  # print(str(pc.predict_prob([message.content])[0]))

  if pc.predict([message.content])[0]:
    await message.channel.send("Hey! That's not good " + message.author.mention + "! "+ message.content)
    await message.delete()

with open("bot-token.txt", "r") as tokenfile:
  client.run(tokenfile.read())