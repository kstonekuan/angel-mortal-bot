# Angel and Mortals Bot

Send anonymous messages between angels and mortals

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
ANGEL_ALIAS = os.environ['ANGEL_ALIAS']
MORTAL_ALIAS = os.environ['MORTAL_ALIAS']