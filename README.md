# Angel and Mortals Bot

Send anonymous messages between angels and mortals. 

**[NEW]** Now supports photos, stickers, documents, audio, video, and animations!

## Read on Medium

https://chatbotslife.com/building-a-chatbot-for-angel-mortal-5d389ab7acde

## User data

Data used for the game was small so just use file PLAYERS_FILENAME to store usernames of players.
Order of columns is player, angel and mortal with one header row.

Sample:
```
Player,Angel,Mortal
username1,username2,username3
username2,username3,username1
username3,username1,username2
```

## Environment variables

ANGEL_BOT_TOKEN = os.environ['ANGEL_BOT_TOKEN']
PLAYERS_FILENAME = os.environ['PLAYERS_FILENAME']
CHAT_ID_JSON = os.environ['CHAT_ID_JSON']
ANGEL_ALIAS = os.environ['ANGEL_ALIAS']
MORTAL_ALIAS = os.environ['MORTAL_ALIAS']

## Useful references
https://python-telegram-bot.readthedocs.io/en/stable/telegram.bot.html?highlight=bot.send_photo
https://python-telegram-bot.readthedocs.io/en/stable/telegram.message.html#telegram.Message