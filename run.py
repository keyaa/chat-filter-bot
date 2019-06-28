from shutil import copyfile
from discord.ext import commands
import profanity_check as pc
import discord
import asyncio

mute_role = "muted"
mod_role = "mod"
custom_prefix = "."
default_threshold = 0.8

bot = commands.Bot(command_prefix=custom_prefix)
blacklist = {}
quiet_mode = False
threshold_value = default_threshold


def is_mod(invoker):
  return discord.utils.get(invoker.guild.roles, name=mod_role) in invoker.roles


async def get_user(ctx, uid, usage_str):
  user = discord.utils.get(ctx.guild.members, id=int(uid.strip("<>@"))) # try to find user id
  if user == None:
    await ctx.send("User not found!")
    await ctx.send(usage_str)
  elif user == bot.user:
    await ctx.send("Who, me?")
    await ctx.send(usage_str)
  else:
    return user


def is_profane(message):
  for word in blacklist.keys(): # check hard-coded filter first
    if word in message:
      return True

  if pc.predict([message])[0] > threshold_value: # after passing through fixed filter, use trained SVM model
    return True
  return False


# another form of "kick" command
@bot.command(pass_context=True)
async def k(ctx):
  await kick.invoke(ctx)


# another form of "reset" command
@bot.command(pass_context=True)
async def r(ctx):
  await reset.invoke(ctx)


# another form of "threshold" command
@bot.command(pass_context=True)
async def t(ctx):
  await threshold.invoke(ctx)


# another form of "quiet_mode" command
@bot.command(pass_context=True)
async def q(ctx):
  await quiet.invoke(ctx)


# another form of "addword" command
@bot.command(pass_context=True)
async def a(ctx):
  await addword.invoke(ctx)


# another form of "delete" command
@bot.command(pass_context=True)
async def d(ctx):
  await delete.invoke(ctx)


# another form of "mute" command
@bot.command(pass_context=True)
async def m(ctx):
  await mute.invoke(ctx)


# kick specified user
@bot.command()
async def kick(ctx, *args):
  if not is_mod(ctx.author):
    if not quiet_mode:
      await ctx.send("You don't have permission to do that!")
    return

  def reaction_check(reaction, moderator): # needed to check if moderator reacted to messages by user
    return moderator == ctx.message.author and str(reaction.emoji) == "✅"

  user = await get_user(ctx, args[0], "Usage: '.k[ick] @user [reason]")
  if user != None:
    message = await ctx.send("Are you sure you want to kick ? (10 second timeout)")
    await message.add_reaction("✅") # wait for response
    try:
      reaction, moderator = await bot.wait_for("reaction_add", timeout=10.0, check=reaction_check) # 10 second timeout, wait for moderator to react
    except asyncio.TimeoutError:
      if not quiet_mode:
        await ctx.send("10 seconds elapsed, timed out.")
    else:
      if len(args) == 2:
        await ctx.guild.kick(user, reason=args[1]) # reason provided
      else:
        await ctx.guild.kick(user) # no reason provided
    await message.delete() # delete message reacted to


# reset blacklist to default
@bot.command()
async def reset(ctx):
  if not is_mod(ctx.author):
    if not quiet_mode:
      await ctx.send("You don't have permission to do that!")
    return

  def reaction_check(reaction, moderator): # needed to check if moderator reacted to messages by user
    return moderator == ctx.message.author and str(reaction.emoji) == "✅"

  message = await ctx.send("Are you sure you want to reset the blacklist? (10 second timeout)")
  await message.add_reaction("✅") # wait for response
  try:
    reaction, moderator = await bot.wait_for("reaction_add", timeout=10.0, check=reaction_check) # 10 second timeout, wait for moderator to react
  except asyncio.TimeoutError:
    if not quiet_mode:
      await ctx.send("10 seconds elapsed, timed out.")
  else:
    blacklist.clear()
    copyfile("default_blacklist.txt", "blacklist.txt")
    with open("blacklist.txt", "r") as blacklist_file: # hard-coded matching words
      for word in blacklist_file.readlines(): # load banned words
        blacklist[word.strip()] = 1
    if not quiet_mode:
      await ctx.send("Blacklist reset.")
  await message.delete() # delete message reacted to


# adjust threshold of trained SVM model for detecting hate speech
@bot.command()
async def threshold(ctx, new_t):
  global quiet_mode
  global threshold_value

  if not is_mod(ctx.author):
    if not quiet_mode:
      await ctx.send("You don't have permission to do that!")
    return

  async def usage():
    await ctx.send("Usage:\n'.t[hreshold] (0.0 - 1.0)'")

  try: 
    threshold_value = float(new_t)
    if threshold_value < 0.0 or threshold_value > 1.0: # outside of valid probability range
      threshold_value = default_threshold # reset to default
      await usage()
      return
    if not quiet_mode:
      await ctx.send("New threshold set to " + new_t + ".")
  except ValueError:
    await usage()
    return


# determines if bot provides feedback upon command completion
@bot.command()
async def quiet(ctx):
  global quiet_mode
  quiet_mode = not quiet_mode
  if quiet_mode:
    await ctx.send("Quiet mode enabled.")
  else:
    await ctx.send("Quiet mode disabled.")


# add word to blacklist of filtered words
@bot.command()
async def addword(ctx, word):
  global quiet_mode

  if not is_mod(ctx.author):
    if not quiet_mode:
      await ctx.send("You don't have permission to do that!")
    return

  prev = quiet_mode
  quiet_mode = True # temporarily suppress filter reply message
  if word in blacklist:
    await ctx.send("Word already blacklisted.")
    return
  else: # not in blacklist, add
    with open("blacklist.txt", "a+") as blacklist_file:
      blacklist_file.write(word + "\n")
    blacklist[word] = 1
    if not prev:
      await ctx.send("New entry added to blacklist.")
  quiet_mode = prev


# deletes user's previous server messages
@bot.command()
async def delete(ctx, *args):
  global quiet_mode

  if not is_mod(ctx.author):
    if not quiet_mode:
      await ctx.send("You don't have permission to do that!")
    return

  def reaction_check(reaction, moderator): # needed to check if moderator reacted to messages by user
    return moderator == ctx.message.author and str(reaction.emoji) == "⛔"

  if len(args) != 1 and len(args) != 2:
    await ctx.send("Usage:\n'.d[elete] @user [# of messages to delete]")
    return

  user = await get_user(ctx, args[0], "Usage:\n'.d[elete] @user [# of messages to delete]")
  if user != None:
    msg_count = -1
    numeric = False
    if len(args) == 2: # if numberic argument provided, delete (args[1]) previous # of messages from user
      numeric = True
      try:
        msg_count = int(args[1])
        if not quiet_mode:
          await ctx.send(user.mention + ", your previous " + str(msg_count) + " messages are inappropriate!")
      except ValueError:
        await ctx.send("Usage:\n'.d[elete] @user [# of messages to delete]")
        return
    else:
      if not quiet_mode:
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
      reaction, moderator = await bot.wait_for("reaction_add", timeout=20.0, check=reaction_check) # 20 second timeout, wait for moderator to react
      bad_message = reaction.message
      bad_message_id = bad_message.id
    except asyncio.TimeoutError:
      await ctx.send("20 seconds elapsed, timed out.")
    else:
      await bad_message.delete() # delete message reacted to
      if not quiet_mode:
        await ctx.send("Message deleted.")
      message_ids.remove(bad_message_id)

    for m_id in message_ids: # remove reactions
      message = await ctx.fetch_message(m_id)
      await message.remove_reaction("⛔", bot.user)


# requires a "muted" role, adds role to mute users
@bot.command()
async def mute(ctx, *args):
  if not is_mod(ctx.author):
    if not quiet_mode:
      await ctx.send("You don't have permission to do that!")
    return

  user = await get_user(ctx, args[0], "Usage: '.m[ute] @user [reason]")
  if user != None:
    role = discord.utils.get(user.guild.roles, name=mute_role)
    if len(args) == 2:
      if role in user.roles:
        await user.remove_roles(role, reason=args[1]) # unmute
        if not quiet_mode:
          await ctx.send("Server unmuted " + user.display_name + "! Reason: " + args[1] + ".")
      else:
        await user.add_roles(role, reason=args[1]) # mute
        if not quiet_mode:
          await ctx.send("Server muted " + user.display_name + "! Reason: " + args[1] + ".")
    else:
      if role in user.roles:
        await user.remove_roles(role) # unmute
        if not quiet_mode:
          await ctx.send("Server unmuted " + user.display_name + "!")
      else:
        await user.add_roles(role) # mute
        if not quiet_mode:
          await ctx.send("Server muted " + user.display_name + "!")


# runs when message is received
@bot.event
async def on_message(message):
  if message.author == bot.user: # don't reply to one's own messages
    return

  await bot.process_commands(message) # check if message is a command

  if is_profane(message.content): # check if message is profane
    if not quiet_mode:
      await message.channel.send("Hey " + message.author.mention + "! That's no good!")
    await message.delete()


# runs upon loading the bot successfully
@bot.event
async def on_ready():
  with open("blacklist.txt", "r") as blacklist_file: # hard-coded matching words
    for word in blacklist_file.readlines(): # load banned words
      blacklist[word.strip()] = 1
  print("Successfully logged in as {0.user}.".format(bot))


with open("bot-token.txt", "r") as tokenfile:
  bot.run(tokenfile.read())