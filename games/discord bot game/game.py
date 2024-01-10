# bot.py
import os
import random
import discord
import pickle
import time
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

client = discord.Client()
bot = commands.Bot(command_prefix='!', description='HELP ME')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

class Player():
    def __init__(self, user, ID):
        self.discordName = user
        self.discordID = ID
        self.name = ''
        self.character_class = ''
        self.race = ''
        self.location = ''
        self.screen = 'new_player'
        self.enemy = ''
        self.level = 0
        self.max_hp = 0
        self.current_hp = 0
        self.str = 10
        self.con = 10
        self.dex = 10
        self.int = 10
        self.armor = 0
        self.xp = 0
        self.gp = 0
        self.inventory = []
        self.actions = []
        self.actions_pool = []
        self.actions_hand = []
        self.armor_bonus = 0
        self.hand_size = 3
        self.distance = 0
        self.my_turn = False
        self.last_online = 0

class Enemy():
    def __init__(self, name, distance=-1, actions=['punch'], ranged=False, hp=0, str=10, con=10, dex=10, int=10, armor=0):
        self.name = name
        if distance == -1:
            distance = random.randint(3, 10)
        if hp == 0:
            hp = con*2
        self.max_hp = hp
        self.current_hp = hp
        self.ranged = ranged
        self.distance = distance
        self.str = str
        self.con = con
        self.dex = dex
        self.int = int
        self.armor = armor
        self.armor_bonus = 0
        self.actions = actions
        self.current_action = ''
        self.my_turn = False

timeout = 60*5

player = ''
command = ''
channel = ''
playerList = ''
exits = []
exits.append(['city', ['grasslands']])
exits.append(['grasslands', ['mountains', 'forest', 'desert', 'city']])
exits.append(['mountains', ['grasslands', 'forest']])
exits.append(['forest', ['mountains', 'grasslands', 'desert', 'beach']])
exits.append(['desert', ['grasslands', 'forest', 'beach']])
exits.append(['beach', ['desert', 'forest']])

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    global player
    global command
    global channel
    global playerList
    channel = message.channel
    
    if message.content[:1] == '-':
        existingPlayer = False
        await channel.send('-'*10)
        try:
            with open('playerList.data', 'rb') as pl:
                playerList = pickle.load(pl)
                for uniquePlayer in playerList:
                    if uniquePlayer.discordName == str(message.author):
                        player = uniquePlayer
                        existingPlayer = True
                        break
            if existingPlayer:
                player.last_online = time.time()
                command = message.content[1:]
                await handle_command()
            else:
                print(f"{message.author} has just joined for the first time.")
                player = Player(str(message.author), message.author.id)
                playerList.append(player)
                await message.author.create_dm()
                command = ''
                await handle_command()
            with open('playerList.data', 'wb') as pl:
                pickle.dump(playerList, pl)
        except (EOFError, FileNotFoundError):
            with open('playerList.data', 'wb') as pl:
                emptyList = []
                pickle.dump(emptyList, pl)
        try:
            await message.delete()
        except discord.errors.Forbidden:
            pass



async def handle_command():
    global command
    print(player.screen)
    if command[:4] == 'help':
        command = command[5:]
        await help()
    elif command == 'playerlist':
        command = ''
        await playerlist()
    elif command == 'map':
        command = ''
        await map()
    elif command[:5] == 'stats' or command == 'statistics' or command == 'stat':
        await stats()
    elif command == 'actions':
        command = ''
        await actions()
    elif player.screen == 'location':
        await location()
    elif player.screen == 'battle':
        await battle()
    elif player.screen == 'battle_confirmation':
        await battle_confirmation()
    elif player.screen == 'battle_confirmation_wait':
        await battle_confirmation_wait()
    elif player.screen == 'name_selection':
        await name_selection()
    elif player.screen == 'name_selection_confirmation':
        await name_selection_confirmation()
    elif player.screen == 'class_selection':
        await class_selection()
    elif player.screen == 'class_selection_confirmation':
        await class_selection_confirmation()
    elif player.screen == 'race_selection':
        await race_selection()
    elif player.screen == 'race_selection_confirmation':
        await race_selection_confirmation()
    elif player.screen == 'new_player':
        await new_player()
    else:
        print(f"ERROR: player screen is {player.screen}")

async def help():
    global command
    if command == '':
        await channel.send('Type -playerlist to view a list of all existing players.'
                           '\nType -map to view your current location on the map.'
                           '\nType -stats to open an overview of your character.'
                           '\nType -actions to open a list of your currently equipped actions.'
                           '\nType -help followed by an action name to learn more about this action.'
                           '\nTyping a single - will repeat the last message.'
                           '\nType -help battle to get more information about fighting.')
    elif command == 'battle':
        await channel.send('During combat you will fight an enemy using your actions.'
                           '\nThe base of these actions is the action pool which consists of all the actions you know.'
                           '\nWhenever you start combat or use an action you will automatically take a new action from the action pool'
                           '\nWhen all of your actions have been used the action pool will refill allowing you to take new actions from it.'
                           '\nTwo actions are always available but will not take a new action from the action pool when you use them.'
                           '\nThese actions are moving forward and waiting.'
                           '\nMoving will move you closer to the enemy for a distance equal to your dexterity divided by 10 while waiting will skip your turn.'
                           '\nTo use an action type - followed by the name of the action or the number the action is preceded by.'
                           '\nTo win a battle you need to reduce the enemy\'s hp to 0.'
                           '\nAny damage done will be substracted by the amount of armor.')
    elif command == 'move' or command == 'moving' or command == 'forward' or command == 'move forward':
        await channel.send('Moving forward will reduce the distance to the enemy by a distance equal to your dexterity divided by 10.'
                           '\nIt will not give you a new action from your action pool.')
    elif command == 'wait':
        await channel.send('Waiting will skip your turn allowing your enemy to act.'
                           '\nIt will not give you a new action from your action pool.')
    elif command == 'stab' or command == 'punch' or command == 'bite':
        await channel.send('Does damage equal to your strength divided by 2.'
                           '\nThe enemy has to be a distance of 1 meter or less away.')
    elif command == 'lunge':
        await channel.send('Moves a distance equal to 2 times your dexterity divided by 10 towards the enemy.'
                           '\nIf you are closer than 1 meter to the enemy before using this action you deal damage equal to you strength divided by two.'
                           '\nIf using this action brings you closer than 1 meter to the enemy you deal 50% more damage.'
                           '\nIf you won\'t get within 1 meter of the enemy this action deals no damage.')
    elif command == 'shield':
        await channel.send('Will boost your armor by 1 during the current battle.')
    elif command == 'arrow':
        await channel.send('Deals damage equal to your dexterity divided by 2.')
    elif command == 'backstep':
        await channel.send('Move a distance away from the enemy equal to your dexterity divided by 10 times 1,5.')
    elif command == 'volley':
        await channel.send('Deals damage equal to your dexterity.')
    elif command == 'magic bolt':
        await channel.send('Deals damage equal to your intelligence divided by 2.')
    elif command == 'electrify':
        await channel.send('Deals damage equal to your intelligence divided by 2.'
                           '\nInstead of the damage being reduced by the enemy\'s armor, their armor will be added to the damage.')
    elif command == 'gust':
        await channel.send('Moves the enemy away for a distance equal to your intelligence minus the enemy\'s strength.')

async def playerlist():
    message = ''
    for uniquePlayer in playerList:
        time_passed = ''
        seconds_passed = time.time() - player.last_online
        if seconds_passed >= 86400:
            time_passed = str(int(seconds_passed/86400)) + ' day'
        elif seconds_passed >= 3600:
            time_passed = str(int(seconds_passed/3600)) + ' hour'
        elif seconds_passed >= 60:
            time_passed = str(int(seconds_passed/60)) + ' minute'
        else:
            time_passed = str(int(seconds_passed)) + ' second'
        if time_passed[:1] != '1':
            time_passed += 's'
        message += f"{uniquePlayer.name} | {uniquePlayer.character_class} | {uniquePlayer.race} | level {uniquePlayer.level} | {uniquePlayer.location} | last online {time_passed} ago\n"
    await channel.send(message)

async def map():
    await channel.send(file=discord.File(f'{player.location}.png'))

async def stats():
    global command
    person = player
    if command[:5] == 'stats':
        command = command[6:]
        if len(command) > 0:
            for uniquePlayer in playerList:
                if uniquePlayer.name == command:
                    person = uniquePlayer
    await channel.send(f'**{person.name}**\nLevel {person.level} {person.race} {person.character_class}'
                       f'\nMax HP: {person.max_hp} \t Base armor: {person.armor}'
                       f'\nStrength: {person.str}\nConstitution: {person.con}\nDexterity: {person.dex}\nIntelligence: {person.int}')

async def actions():
    actions_pool = ''
    for action in player.actions_pool:
        actions_pool += '\n'
        actions_pool += action
    await channel.send(f'Your current action pool consists of the following actions:{actions_pool}')

async def new_player():
    global command
    player.screen = 'new_player'
    if command == 'next':
        command = ''
        await name_selection()
    else:
        await channel.send('Welcome to this game. You can type \"-help\" whenever you need help with commands.'
                           '\nType \"-next\" to move onto the next screen and create your character.')

async def name_selection():
    global command
    player.screen = 'name_selection'
    if command == '':
        await channel.send("Enter the name you want to use preceded by \"-\".")
    else:
        if len(command) <= 20:
            nameAvailable = True
            for uniquePlayer in playerList:
                if uniquePlayer.name == command:
                    nameAvailable = False
                    break
            if nameAvailable:
                player.name = command
                command = ''
                await name_selection_confirmation()
            else:
                await channel.send("This name is not available. Please choose a different one.")
        else:
            await channel.send("Please don't use a name of more than 20 characters.")
        
async def name_selection_confirmation():
    global command
    player.screen = 'name_selection_confirmation'
    if command == '':
        await channel.send(f"Are you sure you want to use \"{player.name}\" as your name? Enter -yes or -no.")
    elif command == 'yes' or command == 'y':
        command = ''
        await class_selection()
    else:
        command = ''
        await name_selection()

async def class_selection():
    global command
    player.screen = 'class_selection'
    if command == '':
        await channel.send("Choose one of the following classes to play:\n-fighter\n-ranger\n-mage.")
    elif command == 'fighter' or command == 'ranger' or command == 'mage':
        player.character_class = command
        command = ''
        await class_selection_confirmation()
    else:
        await channel.send("That class doesn't exist. Choose one of the following:\n-fighter\n-ranger\n-mage")

async def class_selection_confirmation():
    global command
    player.screen = 'class_selection_confirmation'
    if command == '':
        await channel.send(f"Are your sure you want to play as a {player.character_class}?")
    elif command == 'yes' or command == 'y':
        if player.character_class == 'fighter':
            player.actions = ['stab', 'stab', 'stab', 'stab', 'lunge', 'lunge', 'shield']
        elif player.character_class == 'ranger':
            player.actions = ['arrow', 'arrow', 'arrow', 'arrow', 'arrow', 'backstep', 'volley']
        elif player.character_class == 'mage':
            player.actions = ['magic bolt', 'magic bolt', 'magic bolt', 'magic bolt', 'electrify', 'electrify', 'gust']
        command = ''
        await race_selection()
    else:
        command = ''
        await class_selection()

async def race_selection():
    global command
    player.screen = 'race_selection'
    if command == '':
        await channel.send("What race do you want to be?\n-human (+2 to every stat)\n-dwarf (+5 to CON, +2 to STR)\n-elf (+5 to DEX, +2 to INT)")
    elif command == 'human' or command == 'dwarf' or command == 'elf' or command == 'goblin':   #SECRET RACE, DELETE LATER
        player.race = command
        command = ''
        await race_selection_confirmation()
    else:
        await channel.send("That race doesn't exist. Choose one of the following:\n-human\n-dwarf\n-elf")

async def race_selection_confirmation():
    global command
    player.screen = 'race_selection_confirmation'
    if command == '':
        if player.race == 'elf':
            await channel.send(f"Are your sure you want to play as an {player.race}?")
        else:
            await channel.send(f"Are your sure you want to play as a {player.race}?")
    elif command == 'yes' or command == 'y':
        player.level = 1
        if player.race == 'human':
            player.str += 2
            player.con += 2
            player.dex += 2
            player.int += 2
        elif player.race == 'dwarf':
            player.con += 5
            player.str += 2
        elif player.race == 'elf':
            player.dex += 5
            player.int += 2
        #SECRET RACE, DELETE LATER
        elif player.race == 'goblin':
            player.dex += 8
            player.int -= 3
        else:
            print(f'ERROR: race {player.race}')
        player.max_hp = player.con*2
        player.current_hp = player.max_hp
        command = ''
        player.location = 'city'
        await location()
    else:
        command = ''
        await race_selection()

async def location():
    global command
    player.screen = 'location'
    if command[:4] == 'look':
        message = 'Player\'s in this location: '
        playersPresent = False
        for uniquePlayer in playerList:
            if uniquePlayer.location == player.location and uniquePlayer.name != player.name:
                playersPresent = True
                message += f' {uniquePlayer.name}'
        if not playersPresent:
            message = 'There are no other player\'s in this location.'
        message += '\nYou can go to:'
        for exit in exits:
            if exit[0] == player.location:
                amountOfExits = len(exit[1])
                x = 0
                for exitLocation in exit[1]:
                    x += 1
                    message += f' the {exitLocation}'
                break
        await channel.send(message)
    elif command[:6] == 'go to ':
        new_location = command[6:]
        if new_location[:4] == 'the ':
            new_location = new_location[4:]
        for exit in exits:
            if exit[0] == player.location:
                for exitLocation in exit[1]:
                    if exitLocation == new_location:
                        player.location = new_location
                        break
                break
        if player.location == new_location:
            command = ''
            await location()
        else:
            await channel.send('You can\'t go there.')
    elif command[:5] == 'fight':
        if command == 'fight':
            player.actions_hand = []
            player.actions_pool = []
            player.actions_pool = player.actions.copy()
            for action in range(player.hand_size):
                await new_action(player)
            enemy_type = random.randint(1,3)
            if enemy_type == 1:
                player.enemy = Enemy('swarm of rats', actions=['bite'], str=6, con=8, dex=12, int=1)
            elif enemy_type == 2:
                player.enemy = Enemy('troublemaker', actions=['punch'], str=8, con=10, dex=8, int=8)
            elif enemy_type == 3:
                player.enemy = Enemy('bandit', actions=['stab'], str=10, con=12, dex=10, int=10)
            command = ''
            player.distance = player.enemy.distance
            player.my_turn = True
            await battle()
        else:
            command = command[6:]
            if command != player.name:
                for uniquePlayer in playerList:
                    if uniquePlayer.name == command:
                        if uniquePlayer.screen != 'location':
                            await channel.send(f'{uniquePlayer.name} can\'t be fought right now.')
                        elif uniquePlayer.location != player.location:
                            await channel.send(f'{uniquePlayer.name} is currently not at your location.')
                        else:
                            uniquePlayer.enemy = player
                            uniquePlayer.screen = 'battle_confirmation'
                            player.enemy = uniquePlayer
                            player.screen = 'battle_confirmation_wait'
                            user = await bot.fetch_user(uniquePlayer.discordID)
                            await user.dm_channel.send(f'{player.name} challenged you to a fight. Do you accept?')
                            await channel.send(f'{uniquePlayer.name} has been challenged to a fight.')
            else:
                await channel.send('You can\'t fight yourself.')
                    
    else:
        await channel.send(f'Your current location is the {player.location}.\n'
                           'You can **look** around, **go to** a different location or **fight** an enemy.')

async def battle_confirmation():
    global command
    if command == 'y' or command == 'yes':
        user = await bot.fetch_user(player.enemy.discordID)
        player.enemy.screen = 'battle'
        await user.dm_channel.send(f'{player.name} has accepted your invitation to a fight.')
        command = ''
        player.my_turn = True
        player.enemy.my_turn = False
        player.actions_hand = []
        player.actions_pool = []
        player.actions_pool = player.actions.copy()
        for action in range(player.hand_size):
            await new_action(player)
        player.enemy.actions_hand = []
        player.enemy.actions_pool = []
        player.enemy.actions_pool = player.enemy.actions.copy()
        for action in range(player.enemy.hand_size):
            await new_action(player.enemy)
        await battle()
    elif command == 'n' or command == 'no':
        await channel.send(f'You have refused {player.enemy.name}\'s invitation to fight.')
        user = await bot.fetch_user(player.enemy.discordID)
        player.enemy.screen = 'location'
        await user.dm_channel.send(f'{player.name} has refused your invitation to a fight.')
        command = ''
        await location()
    else:
        await channel.send(f'{player.enemy.name} challenged you to a fight. Do you accept?')

async def battle_confirmation_wait():
    global command
    if command == 'cancel':
        await channel.send(f'You have cancelled the invitation to {player.enemy.name} to fight.')
        user = await bot.fetch_user(player.enemy.discordID)
        player.enemy.screen = 'location'
        await user.dm_channel.send(f'{player.name} has cancelled their invitation to a fight.')
        command = ''
        await location()
    else:
        await channel.send(f'{player.enemy.name} has not responded to your invitation to a fight yet. Type \"-cancel\" to cancel the invitation.')


async def battle():
    global command
    player.screen = 'battle'
    action_in_hand = False
    if command == '':
        pass
    elif command == 'forward' or command == 'move' or command == 'move forward' or command == 'm' or command == 'wait' or command == 'w':
        await chosen_action(command, player, player.enemy)
    else:
        try:
            command = int(command)
            if command <= len(player.actions_hand):
                command = player.actions_hand[command-1]
                succeeded = await chosen_action(command, player, player.enemy)
                if succeeded:
                    player.actions_hand.remove(command)
                    await new_action(player)
            else:
                await channel.send("This action is invalid.")
        except ValueError:
            for action in player.actions_hand:
                if action == command:
                    action_in_hand = True
                    succeeded = await chosen_action(command, player, player.enemy)
                    if succeeded:
                        player.actions_hand.remove(command)
                        await new_action(player)
                    break
            if not action_in_hand:
                await channel.send("This action is invalid.")
    if not player.my_turn and player.enemy.current_hp > 0:
        try:    #when fighting a human
            if player.enemy.discordName != '':
                await channel.send(f'It\'s now {player.enemy.name}\'s turn.')
        except AttributeError:  #when fighting an NPC
            if player.enemy.current_action == '':
                new_action_index = random.randint(0, len(player.enemy.actions)-1)
                player.enemy.current_action = player.enemy.actions[new_action_index]
            if player.enemy.distance > 1:
                await chosen_action('move', player.enemy, player)
                await channel.send(f'{player.enemy.name} approaches you.')
            else:
                await channel.send(f'{player.enemy.name} uses {player.enemy.current_action}.')
                await chosen_action(player.enemy.current_action, player.enemy, player)
                player.enemy.current_action = ''
    if player.enemy.current_hp <= 0:
        try:
            if player.enemy.discordName != '':
                player.enemy.armor_bonus = 0
                player.enemy.current_hp = player.max_hp
                player.enemy.actions_hand = []
                player.enemy.actions_pool = player.enemy.actions.copy()
                player.enemy.screen = 'location'
                enemy_player = await bot.fetch_user(player.enemy.discordID)
                await enemy_player.dm_channel.send(f'You have been defeated by {player.enemy.name}.'
                                                   '\nYou have lost half of your gp.')
        except AttributeError:
            pass
        player.armor_bonus = 0
        player.current_hp = player.max_hp
        player.actions_hand = []
        player.actions_pool = player.actions.copy()
        await channel.send(f'You succesfully defeated {player.enemy.name}')
        await location()
    elif player.current_hp <= 0:
        try:
            if player.enemy.discordName != '':
                player.enemy.armor_bonus = 0
                player.enemy.current_hp = player.max_hp
                player.enemy.actions_hand = []
                player.enemy.actions_pool = player.enemy.actions.copy()
                player.enemy.screen = 'location'
                enemy_player = await bot.fetch_user(player.enemy.discordID)
                await enemy_player.dm_channel.send(f'You succesfully defeated {player.enemy.name}')
        except AttributeError:
            pass
        player.armor_bonus = 0
        player.current_hp = player.max_hp
        player.actions_hand = []
        player.actions_pool = player.actions.copy()
        player.gp = player.gp/2
        await channel.send(f'You have been defeated by {player.enemy.name}.'
                           '\nYou have lost half of your gp.')
        await location()
    else:
        available_actions = ''
        index = 0
        for action in player.actions_hand:
            index += 1
            available_actions += f'\n {index}. {action}'
        await channel.send(f'{player.enemy.name} is {round(player.enemy.distance, 2)} meters away and has {player.enemy.current_hp}/{player.enemy.max_hp} HP and {player.enemy.armor+player.enemy.armor_bonus} armor.'
                           f'\nYou have {player.current_hp}/{player.max_hp} HP and {player.armor+player.armor_bonus} armor.'
                           '\n**move** forward or **wait**'
                           f'\nCurrently available actions are: {available_actions}')

async def new_action(person):
    if len(person.actions_pool) == 0:
        person.actions_pool = person.actions.copy()
    new_action_index = random.randint(0, len(person.actions_pool)-1)
    new_action = person.actions_pool[new_action_index]
    person.actions_hand.append(new_action)
    person.actions_pool.remove(new_action)

async def chosen_action(action, user, enemy):
    user.my_turn = False
    succeeded = True
    if action == 'forward' or action == 'move' or action == 'move forward' or action == 'm':
        enemy.distance -= user.dex/10
    elif action == 'wait' or action == 'w':
        pass
    elif action == 'stab' or action == 'punch' or action == 'bite':
        if enemy.distance <= 1:
            enemy.current_hp -= max(0, user.str/2 - enemy.armor - enemy.armor_bonus)
        else:
            user.my_turn = True
            succeeded = False
            await channel.send('The enemy is too far away.')
    elif action == 'lunge':
        if enemy.distance > 1 and enemy.distance <= (2*user.dex/10)+1:
            enemy.distance -= 2*user.dex/10
            enemy.current_hp -= max(0, 1.5*user.str/2 - enemy.armor - enemy.armor_bonus)
        elif enemy.distance <= 1:
            enemy.distance -= 2*user.dex/10
            enemy.current_hp -= max(0, user.str/2 - enemy.armor - enemy.armor_bonus)
        else:
            enemy.distance -= 2*player.dex/10
    elif action == 'shield':
        user.armor_bonus += 1
    elif action == 'arrow':
        enemy.current_hp -= max(0, user.dex/2 - enemy.armor - enemy.armor_bonus)
    elif action == 'backstep':
        enemy.distance += 1.5*user.dex/10
    elif action == 'volley':
        enemy.current_hp -= max(0, user.dex - enemy.armor - enemy.armor_bonus)
    elif action == 'magic bolt':
        enemy.current_hp -= max(0, user.int/2 - enemy.armor - enemy.armor_bonus)
    elif action == 'electrify':
        enemy.current_hp -= max(0, user.int/2 + enemy.armor + enemy.armor_bonus)
    elif action == 'gust':
        enemy.distance += max(0, user.int - enemy.str)
    else:
        user.my_turn = True
        succeeded = False
        await channel.send('This action doesn\'t exist.')
    if enemy.distance < 0:
        enemy.distance = 0
    user.distance = enemy.distance
    if user.my_turn:
        enemy.my_turn = False
    else:
        enemy.my_turn = True
        try:
            if enemy.discordName != '':
                enemy_player = await bot.fetch_user(enemy.discordID)
                await enemy_player.dm_channel.send(f'{player.name} used {action}. It\s now your turn.')
                if user.current_hp > 0 and enemy.current_hp > 0:
                    available_actions = ''
                    index = 0
                    for action in enemy.actions_hand:
                        index += 1
                        available_actions += f'\n {index}. {action}'
                    await enemy_player.dm_channel.send(f'{user.name} is {round(user.distance, 2)} meters away and has {user.current_hp}/{user.max_hp} HP and {user.armor+user.armor_bonus} armor.'
                                                       f'\nYou have {enemy.current_hp}/{enemy.max_hp} HP and {enemy.armor+enemy.armor_bonus} armor.'
                                                       '\n**move** forward or **wait**'
                                                       f'\nCurrently available actions are: {available_actions}')
        except AttributeError:
            pass
    return succeeded

		

bot.run(token)
