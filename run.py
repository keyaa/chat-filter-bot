from discord.ext import commands
import profanity_check as pc
from fuzzywuzzy import fuzz
import discord
import asyncio

bot = commands.Bot(command_prefix=".")


def is_profane(message):
  # print(str(pc.predict_prob([message])[0]))
  if pc.predict([message])[0]:
    return True
  return False


# another form of "delete" command
@bot.command(pass_context=True)
async def d(ctx):
  await delete.invoke(ctx)


# another form of "mute" command
@bot.command(pass_context=True)
async def m(ctx):
  await mute.invoke(ctx)


# deletes user's previous server messages
@bot.command()
async def delete(ctx, *args):

  async def usage():
    await ctx.send("Usage:\n'.d[elete] @user [# of messages to delete]")

  def check(reaction, moderator): # needed to check if moderator reacted to messages by user
    return moderator == ctx.message.author and str(reaction.emoji) == "⛔"

  if len(args) != 1 and len(args) != 2:
    await usage()
    return

  mention_id = args[0]
  user = discord.utils.get(ctx.guild.members, id=int(mention_id.strip("<>@"))) # try to find user id
  if user == None:
    await ctx.send("User not found!")
    await usage()
  elif user == bot.user:
    await ctx.send("Who, me?")
    await usage()
  else:
    msg_count = -1
    numeric = False
    if len(args) == 2: # if numberic argument provided, delete (args[1]) previous # of messages from user
      numeric = True
      try:
        msg_count = int(args[1])
        await ctx.send(user.mention + ", your previous " + str(msg_count) + " messages are inappropriate!")
      except ValueError:
        await usage()
        return
    else:
      await ctx.send(user.mention + ", one of your messages was deemed to be inappropriate!")

    message_ids = []
    bad_message_id = -1
    async for message in ctx.history(limit=10): # search through chat history for previous messages by mentioned user
      if message.author == user:
        if numeric:
          if msg_count > 0:
            await message.delete()
            msg_count -= 1
        else:
          await message.add_reaction("⛔") # add emoji for ease of adding to blacklist by moderator
          message_ids.append(message.id)
    
    if numeric:
      return

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


# requires a "muted" role, adds role to mute users
@bot.command()
async def mute(ctx, *args):
  async def usage():
    await ctx.send("Usage: '.m[ute] @user [reason]")

  mention_id = args[0]
  print(mention_id)
  user = discord.utils.get(ctx.guild.members, id=int(mention_id.strip("<>@"))) # try to find user id
  print(user)
  if user == None:
    await ctx.send("User not found!")
    await usage()
  elif user == bot.user:
    await ctx.send("Who, me?")
    await usage()
  else:
    role = discord.utils.get(user.guild.roles, name="muted")
    print(role)
    if len(args) == 2:
      await user.add_roles(role, reason=args[1])
    else:
      await user.add_roles(role)
    await ctx.send("Server muted " + user.display_name + "!")


# runs when message is received
@bot.event
async def on_message(message):
  if message.author == bot.user: # don't reply to one's own messages
    return

  if is_profane(message.content): # check if message is profane
    await message.channel.send("Hey " + message.author.mention + "! That's no good!")
    await message.delete()

  await bot.process_commands(message) # check if message is a command


# runs upon loading the bot successfully
@bot.event
async def on_ready():
  print("Successfully logged in as {0.user}.".format(bot))


with open("bot-token.txt", "r") as tokenfile:
  bot.run(tokenfile.read())