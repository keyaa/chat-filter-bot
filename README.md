# chat-filter-bot

A (hopefully working) chat filtering bot for Discord's Hack Week!

[![Discord Hack Week](hack_week_logo.png "Discord Hack Week!")](https://blog.discordapp.com/discord-community-hack-week-build-and-create-alongside-us-6b2a7b7bba33)

Note that there are a few adjustable parameters at the top of run.py:

- mute_role
- mod_role
- custom_prefix
- default_threshold

```
pip3 install -r requirements.txt
python3 run.py
```

## Commands:
```
usage: '.u[sage]', displays all commands.

reset: '.r[eset]', resets blacklist of banned words.

kick: '.k[ick] @user [reason]', kicks a user with optional reason.

threshold: '.t[hreshold] (0.0 - 1.0)', changes threshold detection for profanity filtering.

quiet: '.q[uiet]', toggles quiet mode on or off.

addword: '.a[ddword] (word)', adds a word to blacklist.

delete: '.d[elete] @user [# of messages to delete]', select a user's previous message to delete, or delete a number of previous messages.

mute: '.m[ute] @user [reason]', mutes/unmutes a user with optional reason.
```

Thanks to [Victor Zhou](https://github.com/vzhou842) for his [fantastic SVM model](https://github.com/vzhou842/profanity-check) and [great writeup!](https://towardsdatascience.com/building-a-better-profanity-detection-library-with-scikit-learn-3638b2f2c4c2)

Thanks to [Robert Gabriel](https://github.com/RobertJGabriel) for his [baseline list of Google profanities!](https://github.com/RobertJGabriel/Google-profanity-words)