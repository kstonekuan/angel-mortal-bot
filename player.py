import config
import csv
import json
import logging

logger = logging.getLogger(__name__)

class Player():
    def __init__(self):
        self.username = None
        self.angel = None
        self.mortal = None
        self.chat_id = None

def loadPlayers(players: dict):
    with open(config.PLAYERS_FILENAME) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                logger.info(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                playerName = row[0].strip().lower()
                angelName = row[1].strip().lower()
                mortalName = row[2].strip().lower()
                logger.info(f'\t{playerName} has angel {angelName} and mortal {mortalName}.')
                players[playerName].username = playerName
                players[playerName].angel = players[angelName]
                players[playerName].mortal = players[mortalName]
                line_count += 1
        logger.info(f'Processed {line_count} lines.')

    validatePairings(players)
    loadChatID(players)

def validatePairings(players: dict):
    for _, player in players.items():
        if player.angel.mortal.username != player.username or player.mortal.angel.username != player.username:
            print(f'Error with {player.username} pairings')
            logger.error(f'Error with {player.username} pairings')
            exit(1)

def saveChatID(players: dict):
    temp = {}
    for k, v in players.items():
        temp[k] = v.chat_id
    
    with open(config.CHAT_ID_JSON, 'w+') as f:
        json.dump(temp, f)

def loadChatID(players: dict):
    try:
        with open(config.CHAT_ID_JSON, 'r') as f:
            temp = json.load(f)

            logger.info(temp)

            for k, v in temp.items():
                players[k].chat_id = v
    except:
        logger.warn('Fail to load chat ids')