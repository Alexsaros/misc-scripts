import pickle

class Player():
    def __init__(self, user, ID):
        self.discordName = user
        self.discordID = ID
        self.name = ''
        self.character_class = ''
        self.race = ''
        self.location = ''
        self.screen = 'new_player'
        self.level = 0

all_locations = ['city', 'grasslands', 'mountains', 'forest', 'desert', 'beach']
all_screens = ['location', 'name_selection', 'name_selection_confirmation', 'class_selection', 'class_selection_confirmation', 'race_selection', 'race_selection_confirmation', 'new_player']

with open('playerList.data', 'rb') as pl:
    playerList = pickle.load(pl)
    for player in playerList:
        no_location = True
        no_screen = True
        for location in all_locations:
            if player.location == location:
                no_location = False
                break
        for screen in all_screens:
            if player.screen == screen:
                no_screen = False
                break
        if no_location:
            player.location = 'city'
        if no_screen:
            player.screen = 'location'
with open('playerList.data', 'wb') as pl:
    pickle.dump(playerList, pl)
