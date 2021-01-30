import collections
import config
import csv

class Player():
    def __init__(self):
        self.angel = None
        self.mortal = None
        self.chat_id = None

def initPlayers():
    players = collections.defaultdict(Player)
    with open(config.PLAYERS_FILENAME) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                player = row[0].strip()
                angel = row[1].strip()
                mortal = row[2].strip()
                print(f'\t{player} has angel {angel} and mortal {mortal}.')
                players[player].angel = players[angel]
                players[player].mortal = players[mortal]
                line_count += 1
        print(f'Processed {line_count} lines.')
    
    return players