import numpy as np
import msvcrt
import random


def init_map_ground():
    map_empty = np.zeros([width, height], dtype=str)
    for y in range(len(map_empty[0])):
        for x in range(len(map_empty)):
            map_empty[x, y] = '·'
    return map_empty


def init_map_terrain():
    map_empty = np.zeros([width, height], dtype=str)
    return map_empty


def refresh_map_creatures():
    map_new = np.zeros([width, height], dtype=str)
    for creature in creature_list:
        map_new[creature.x, creature.y] = creature.symbol
    return map_new


def show_map():
    temp_map = np.copy(map_ground)
    for y in range(height):
        for x in range(width):
            if map_terrain[x, y] != '':
                temp_map[x, y] = map_terrain[x, y]
    for y in range(height):
        for x in range(width):
            if map_creatures[x, y] != '':
                temp_map[x, y] = map_creatures[x, y]
    for y in range(height-1, -1, -1):   # walks backwards through the loop so positive y prints up
        for x in range(width):
            print("", temp_map[x, y], "", end='')
        print('')


def handle_input(command):
    turn_end = False
    player = creature_list[player_index]
    try:
        if 1 <= int(command) <= 9 and int(command) != 5:
            if command == '1':
                new_pos = [player.x - 1, player.y - 1]
            elif command == '2':
                new_pos = [player.x, player.y - 1]
            elif command == '3':
                new_pos = [player.x + 1, player.y - 1]
            elif command == '4':
                new_pos = [player.x - 1, player.y]
            elif command == '6':
                new_pos = [player.x + 1, player.y]
            elif command == '7':
                new_pos = [player.x - 1, player.y + 1]
            elif command == '8':
                new_pos = [player.x, player.y + 1]
            elif command == '9':
                new_pos = [player.x + 1, player.y + 1]
            if 0 <= new_pos[0] < width and 0 <= new_pos[1] < height:
                if map_creatures[new_pos[0], new_pos[1]] == '':
                    player.x = new_pos[0]
                    player.y = new_pos[1]
                    turn_end = True
                else:
                    print("You can't move there. Something is blocking your path.")
            else:
                print("You can't move there. This is the border of the map.")
        elif command == '5':
            turn_end = True
            print("You wait.")
    except ValueError:
        if command == 'a':
            turn_end = player_attack()
    return turn_end

#105

def player_attack():
    player = creature_list[player_index]
    weapon = player.weapon
    wpn_range = weapon[0]
    targets = []
    for target in creature_list:   # checks if creature is in range of weapon
        if player.x-wpn_range <= target.x <= player.x+wpn_range and player.y-wpn_range <= target.y <= player.y+wpn_range:
            targets.append(target)
    number = 0
    print("Choose your target:")
    for target in targets:  # lists and numbers all available targets in range with distance
        north = False
        south = False
        east = False
        west = False
        number += 1
        if target.y > player.y:
            north = True
        elif target.y < player.y:
            south = True
        if target.x > player.x:
            east = True
        elif target.x < player.x:
            west = True
        print("{}. {}".format(number, target.name), end='')
        if north:
            distance = int(target[3]) - int(creature_array[player_row, 3])
            if distance == 1:
                print(distance, "tile to the north", end='')
            else:
                print(distance, "tiles to the north", end='')
        elif south:
            distance = int(creature_array[player_row, 3]) - int(target[3])
            if distance == 1:
                print(distance, "tile to the south", end='')
            else:
                print(distance, "tiles to the south", end='')
        if (north or south) and (east or west):
            print(" and ", end='')
        if east:
            distance = int(target[2]) - int(creature_array[player_row, 2])
            if distance == 1:
                print(distance, "tile to the east", end='')
            else:
                print(distance, "tiles to the east", end='')
        elif west:
            distance = int(creature_array[player_row, 2]) - int(target[2])
            if distance == 1:
                print(distance, "tile to the west", end='')
            else:
                print(distance, "tiles to the west", end='')
        print("")
    chosen_target = msvcrt.getch()
    chosen_target = bytes.decode(chosen_target)
    actual_target = targets[int(chosen_target)-1]
    print("You attack the", actual_target[0])
    attack_roll = random.randint(1, 20)
    print("You roll ", int(attack_roll), "+",  + int(attacker[6]), " to hit.")
    attack_roll += int(attacker[6])
    if attack_roll >= int(actual_target[5]):
        damage_roll = random.randint(1, weapon[1])
        print("You hit the ", actual_target[0], " for ", damage_roll, " damage.")
        for index in range(len(creature_array)):    # finds index of attacked creature
            if (creature_array[index] == actual_target).all():
                creature_index = index
                break
        creature = creature_array[creature_index]
        creature[4] = int(creature[4]) - damage_roll
        if int(creature[4]) > 0:
            print("The ", creature[0], " has ", int(creature[4]), " hit points left.")
        else:
            on_dead(creature_index)
    else:
        print("But you miss.")
    return turn_end


def on_dead(index):
    updated_array = creature_array
    creature = creature_array[index]
    print("The ", creature[0], " died.")
    updated_array = np.delete(creature_array, index)


class Player:
    name = "player"
    symbol = 'O'
    max_health = 100
    current_health = max_health
    armor = 12
    attack_modifier = 2
    weapon = "sword"
    x = 2
    y = 2


class Goblin:
    def __init__(self):
        for x in range(4):
            self.max_health += random.randint(1, 6)
        self.armor = 10 + random.randint(-1, 1)
        self.attack_modifier = random.randint(-1, 2)
    name = "goblin"
    symbol = 'g'
    max_health = 0
    current_health = max_health
    armor = 0
    attack_modifier = 0
    weapon = "shortsword"
    x = 0
    y = 0


width = 10
height = 4

weapons = {     # range, damage
    "sword": [1, 10],
    "shortsword": [1, 6],
    "bow": [3, 4]
}

random.seed()

creature_list = []
creature_list.append(Player())
creature_list.append(Goblin())
player_index = 0

map_ground = init_map_ground()
map_terrain = init_map_terrain()
map_creatures = refresh_map_creatures()

input_char = '0'
turn_counter = 0
while input_char != 'p':   # 1 loop is 1 turn
    map_creatures = refresh_map_creatures()
    show_map()
    end_turn = False
    print("Health[{}] Weapon[{}]".format(creature_list[player_index].current_health, creature_list[player_index].weapon))
    print("Input next command:")
    input_char = msvcrt.getch()
    input_char = bytes.decode(input_char)
    for line in range(20):
        print('')
    end_turn = handle_input(input_char)
    if end_turn:
        turn_counter += 1
    print("Turn:", turn_counter)



