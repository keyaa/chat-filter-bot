from discord.ext import commands
import profanity_check as pc
from fuzzywuzzy import fuzz
import discord
import asyncio

bot = commands.Bot(command_prefix="+")

def is_profane(message):
  # print(str(pc.predict_prob([message])[0]))
  if pc.predict([message])[0]:
    return True
  return False

@bot.command()
async def bm(ctx, mention_id): # blacklist message from user
  user = discord.utils.get(ctx.guild.members, id=int(mention_id.strip("<>@"))) # try to find user id
  if user == None:
    await ctx.send("User not found!")
  elif user == bot.user:
    await ctx.send("Who, me?")
  else:
    await ctx.send(user.mention + ", one of your messages was deemed to be inappropriate!")

    def check(reaction, moderator): # needed to check if moderator reacted to messages by user
      return moderator == ctx.message.author and str(reaction.emoji) == "⛔"

    message_ids = []
    bad_message_id = -1
    async for message in ctx.history(limit=6): # search through chat history for previous messages by mentioned user
      if message.author == user:
        await message.add_reaction("⛔") # add emoji for ease of adding to blacklist by moderator
        message_ids.append(message.id)

    try:
      reaction, moderator = await bot.wait_for("reaction_add", timeout=30.0, check=check) # 30 second timeout, wait for moderator to react
      bad_message = reaction.message
      bad_message_id = bad_message.id
    except asyncio.TimeoutError:
      await ctx.send("30 seconds elapsed, timed out.")
    else:
      await bad_message.delete() # delete message reacted to
      await ctx.send("Message deleted.")
      message_ids.remove(bad_message_id)

    for m_id in message_ids: # remove reactions
      message = await ctx.fetch_message(m_id)
      await message.remove_reaction("⛔", bot.user)

@bot.event
async def on_message(message):
  if message.author == bot.user: # don't reply to one's own messages
    return

  if is_profane(message.content): # check if message is profane
    await message.channel.send("Hey " + message.author.mention + "! That's no good!")
    await message.delete()

  await bot.process_commands(message) # check if message is a command

@bot.event
async def on_ready():
  print("Successfully logged in as {0.user}.".format(bot))

with open("bot-token.txt", "r") as tokenfile:
  bot.run(tokenfile.read())