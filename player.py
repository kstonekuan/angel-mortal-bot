import collections
from config import PLAYERS_FILENAME
import csv

class Player():
    def __init__(self):
        self.username = None
        self.angel = None
        self.mortal = None
        self.chat_id = None

def loadPlayers():
    players = collections.defaultdict(Player)
    with open(PLAYERS_FILENAME) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                playerName = row[0].strip().lower()
                angelName = row[1].strip().lower()
                mortalName = row[2].strip().lower()
                print(f'\t{playerName} has angel {angelName} and mortal {mortalName}.')
                players[playerName].username = playerName
                players[playerName].angel = players[angelName]
                players[playerName].mortal = players[mortalName]
                line_count += 1
        print(f'Processed {line_count} lines.')
    
    return players