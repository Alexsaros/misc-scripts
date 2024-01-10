import numpy as np
import msvcrt
import random
import copy


def init_map_empty():
    map_empty = np.zeros([map_width, map_height], dtype=str)
    return map_empty


def init_map_ground():
    map_empty = np.zeros([map_width, map_height], dtype=str)
    for y in range(len(map_empty[0])):
        for x in range(len(map_empty)):
            map_empty[x, y] = '·'
    return map_empty


def init_map_terrain():
    map_empty = np.zeros([map_width, map_height], dtype=str)
    for x in range(20):
        placed = False
        while not placed:
            x = random.randint(0, map_width - 1)
            y = random.randint(0, map_height - 1)
            if map_empty[x, y] == '':
                map_empty[x, y] = '#'
                placed = True
    return map_empty


def refresh_map_creatures():
    global map_creatures
    map_creatures = np.zeros([map_width, map_height], dtype=str)
    for creature in creature_list:
        map_creatures[creature.x, creature.y] = creature.symbol


def show_map():
    for x in range(blank_lines):
        print('')
    for line in log:
        print(line, end='')
    print("Turn:", turn_counter)
    refresh_map_creatures()
    temp_map = np.copy(map_ground)
    for y in range(map_height):
        for x in range(map_width):
            if map_terrain[x, y] != '':
                temp_map[x, y] = map_terrain[x, y]
    for y in range(map_height):
        for x in range(map_width):
            if map_creatures[x, y] != '':
                temp_map[x, y] = map_creatures[x, y]
    for y in range(map_height):
        for x in range(map_width):
            if map_temp[x, y] != '':
                temp_map[x, y] = map_temp[x, y]
    for y in range(map_height - 1, -1, -1):  # walks backwards through the loop so positive y prints up
        for x in range(map_width):
            print("", temp_map[x, y], "", end='')
        print('')
    print("Health[{}/{}] Mana[{}/{}] Armor[{}] Weapon[{}]".format(player.current_health, player.max_health,
                                                                  player.current_mana, player.max_mana,
                                                                  player.armor, player.weapon.name))


def sort_tile_cost(given_list):
    return given_list[2]


def get_distance(a, b):
    distance_x = abs(a[0] - b[0])
    distance_y = abs(a[0] - b[0])
    if distance_x > distance_y:
        return distance_x
    else:
        return distance_y


def walk_to(begin_pos, end_pos):
    # tile = [x, y, total_cost, parent_tile]
    # makes sure the x and y coordinates are in shape [x, y]
    try:
        if len(begin_pos) != 2:
            start = [begin_pos.x, begin_pos.y]
        else:
            start = begin_pos
    except TypeError:
        start = [begin_pos.x, begin_pos.y]
    try:
        if len(end_pos) != 2:
            goal = [end_pos.x, end_pos.y]
        else:
            goal = end_pos
    except TypeError:
        goal = [end_pos.x, end_pos.y]
    neighbours = [[0, 1], [1, 0], [0, -1], [-1, 0], [1, 1], [1, -1], [-1, -1], [-1, 1]]
    distance = get_distance(start, goal)
    start.append(distance)
    start.append(0)
    # creates the open and closed list and adds start to the open list
    open_list = [start]
    closed_list = []
    # keeps exploring unexplored tiles until none are left
    current_tile = start
    while len(open_list) > 0:
        open_list.sort(key=sort_tile_cost)    # sorts available tiles by cost
        current_tile = open_list[0]     # takes the unexplored tile with the best chance of going to the goal
        if current_tile[:2] == goal:    # checks if you've found the goal
            break
        for neighbour in neighbours:    # selects tiles next to current tile
            new_tile = copy.deepcopy(current_tile)  # makes a copy so current_tile doesn't get edited
            new_tile[0] += neighbour[0]
            new_tile[1] += neighbour[1]
            # checks if new tile is blocked by map size
            if 0 <= new_tile[0] < map_width and 0 <= new_tile[1] < map_height:
                # checks if new tile is blocked by other creatures or terrain
                if (map_creatures[new_tile[0], new_tile[1]] == '' or new_tile[:2] == goal) and map_terrain[new_tile[0], new_tile[1]] == '':
                    # todo make it so different terrain costs can be read from map and dictionary and used here
                    # adds cost to the new tile: previous tile's cost plus one and new/updated distance cost
                    new_tile[2] = (current_tile[2] + 1 - get_distance(current_tile, goal) + get_distance(new_tile, goal))
                    new_tile[3] = current_tile  # adds parent tile
                    # checks if new tile is in the open list
                    in_open = False
                    for tile in open_list:
                        if tile[0] == new_tile[0] and tile[1] == new_tile[1]:
                            in_open = True
                            if tile[2] >= new_tile[2]:  # checks if new route to tile is better
                                tile = new_tile  # updates to better tile/route
                            break
                    # check if new tile is in the closed list
                    in_closed = False
                    if not in_open:
                        for tile in closed_list:
                            if tile[0] == new_tile[0] and tile[1] == new_tile[1]:
                                in_closed = True
                                if tile[2] >= new_tile[2]:  # checks if new route to tile is better
                                    closed_list.remove(tile)
                                    tile = new_tile  # updates to better tile/route
                                    open_list.append(tile)  # adds tile to open list to try and get better route
                                break
                    if not in_open and not in_closed:   # if it's a new tile add it to the open list
                        open_list.append(new_tile)
        open_list.remove(current_tile)
        closed_list.append(current_tile)
    if current_tile[:2] != goal:
        return None
    else:
        positions = []
        end = False
        while not end:
            try:
                if len(current_tile[3]) == 4:   # checks if the tile has a parent tile
                    positions.append(current_tile[:2])  # adds the position of the current tile to a list
                    current_tile = current_tile[3]  # works its way up to the next tile
                else:
                    end = True
            except TypeError:
                end = True
        positions.reverse()
        positions.append(goal)
        return positions


def handle_input(command):
    global log
    global end_turn
    global player
    global quit_game
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
            else:
                new_pos = [player.x, player.y]
                log.append("Error: {}\n".format(command))
            if 0 <= new_pos[0] < map_width and 0 <= new_pos[1] < map_height:
                if map_creatures[new_pos[0], new_pos[1]] == '' and map_terrain[new_pos[0], new_pos[1]] == '':
                    player.x = new_pos[0]
                    player.y = new_pos[1]
                    end_turn = True
                else:
                    log.append("You can't move there. Something is blocking your path.\n")
            else:
                log.append("You can't move there. This is the border of the map.\n")
        elif command == '5':
            end_turn = True
            log.append("You wait.\n")
    except ValueError:
        if command == 'a':
            player_attack()
        elif command == 'k':
            look_at()
        elif command == 'q':
            end_turn = True
            quit_game = True
        else:
            log.append("Invalid input.\n")


def look_at():
    global map_temp
    global log
    cursor = [player.x, player.y]
    command = ''
    while command != 'x':
        map_temp = init_map_empty()
        map_temp[cursor[0], cursor[1]] = '▢'
        creature = map_creatures[cursor[0], cursor[1]]
        if creature != '':
            for creature in creature_list:
                if creature.x == cursor[0] and creature.y == cursor[1]:
                    log.append("You see a {}\n".format(creature.name))
                    log.append("Health[{}/{}] Armor[{}] Weapon[{}]\n".format(creature.current_health, creature.max_health, creature.armor, creature.weapon.name))
                    break
        show_map()
        log = []
        print("Move (numpad) or e(x)it:")
        input_char = msvcrt.getch()
        try:
            command = bytes.decode(input_char)
            try:
                if 1 <= int(command) <= 9 and int(command) != 5:
                    print("yes")
                    if command == '1':
                        new_pos = [cursor[0] - 1, cursor[1] - 1]
                    elif command == '2':
                        new_pos = [cursor[0], cursor[1] - 1]
                    elif command == '3':
                        new_pos = [cursor[0] + 1, cursor[1] - 1]
                    elif command == '4':
                        new_pos = [cursor[0] - 1, cursor[1]]
                    elif command == '6':
                        new_pos = [cursor[0] + 1, cursor[1]]
                    elif command == '7':
                        new_pos = [cursor[0] - 1, cursor[1] + 1]
                    elif command == '8':
                        new_pos = [cursor[0], cursor[1] + 1]
                    elif command == '9':
                        new_pos = [cursor[0] + 1, cursor[1] + 1]
                    else:
                        new_pos = [cursor[0], cursor[1]]
                        log.append("Error: {}\n".format(command))
                    if 0 <= new_pos[0] < map_width and 0 <= new_pos[1] < map_height:
                        cursor[0] = new_pos[0]
                        cursor[1] = new_pos[1]
                    else:
                        log.append("This is the border of the map.\n")
            except ValueError:
                if command == 'x':
                    log = []
                else:
                    log.append("Invalid input.\n")
        except UnicodeDecodeError:
            log.append("Invalid input.\n")
    map_temp = init_map_empty()


def creature_in_range(action):
    global log
    global end_turn
    global player
    actual_target = 0
    max_range = action.max_range
    min_range = action.min_range
    targets = []
    for target in creature_list:  # checks if creature is (inside of max range) and (not inside of min range)
        x_distance = target.x - player.x
        y_distance = target.y - player.y
        if abs(x_distance) <= max_range and abs(y_distance) <= max_range and (abs(x_distance) >= min_range or abs(y_distance) >= min_range):
            targets.append(target)
    if len(targets) > 0:
        number = 0
        log.append("Choose your target: \n")
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
            log.append("{}. {} ".format(number, target.name))
            if north:
                distance = target.y - player.y
                if distance == 1:
                    log.append("{} tile to the north".format(distance))
                else:
                    log.append("{} tiles to the north".format(distance))
            elif south:
                distance = player.y - target.y
                if distance == 1:
                    log.append("{} tile to the south".format(distance))
                else:
                    log.append("{} tiles to the south".format(distance))
            if (north or south) and (east or west):
                log.append(" and ")
            if east:
                distance = target.x - player.x
                if distance == 1:
                    log.append("{} tile to the east".format(distance))
                else:
                    log.append("{} tiles to the east".format(distance))
            elif west:
                distance = player.x - target.x
                if distance == 1:
                    log.append("{} tile to the west".format(distance))
                else:
                    log.append("{} tiles to the west".format(distance))
            log.append(". \n")
        show_map()
        print("Input the number of the creature you want to target or e(x)it: ")
        chosen_target = msvcrt.getch()
        chosen_target = bytes.decode(chosen_target)
        try:
            if int(chosen_target) <= len(targets):
                actual_target = targets[int(chosen_target) - 1]
                end_turn = True
            else:
                log = ["Invalid input.\n"]
        except ValueError:
            if chosen_target == 'x':
                log = []
            else:
                log = ["Invalid input.\n"]
    else:
        log.append("There are no possible targets nearby.\n")
    return actual_target


def player_attack():
    global player
    global log
    weapon = player.weapon
    target = creature_in_range(weapon)
    if target != 0:  # if a target has been chosen
        log = []
        critical_hit = False
        log.append("You attack the {}.\n".format(target.name))
        attack_roll = random.randint(1, 20)
        if player.attack_modifier > 0:
            log.append("You roll {}+{} to hit.\n".format(attack_roll, player.attack_modifier))
        elif player.attack_modifier < 0:
            log.append("You roll {}{} to hit.\n".format(attack_roll, player.attack_modifier))
        else:
            log.append("You roll {} to hit.\n".format(attack_roll))
        if attack_roll == 20:
            log.append("It's a critical hit! You're guaranteed to hit with extra damage.\n")
            critical_hit = True
        attack_roll += player.attack_modifier
        if attack_roll >= target.armor or critical_hit:
            if critical_hit:
                damage_roll1 = random.randint(1, weapon.damage)
                damage_roll2 = random.randint(1, weapon.damage)
                damage_roll = damage_roll1 + damage_roll2
                log.append("You hit the {} for {}+{} damage.\n".format(target.name, damage_roll1, damage_roll2))
            else:
                damage_roll = random.randint(1, weapon.damage)
                log.append("You hit the {} for {} damage.\n".format(target.name, damage_roll))
            target.current_health -= damage_roll
            if target.current_health > 0:
                log.append("The {} has {} hit points left.\n".format(target.name, target.current_health))
            else:
                on_creature_dead(target)
        else:
            log.append("But you miss.\n")


def on_creature_dead(creature):
    log.append("The {} died.\n".format(creature.name))
    index = 0
    for x in creature_list:     # finds and deletes dead creature in creature_list
        if x == creature:
            del creature_list[index]
            break
        index += 1


def on_player_dead():
    global player
    player.dead = True
    log.append("You have died.\n")
    del creature_list[player_index]


def new_turn():
    global player
    # actions = 0
    # total_actions = 0
    # for creature in creature_list:
    #     creature.actions_left += creature.speed
    #     total_actions += int(creature.actions_left)     # gets total amount of action for this turn
    # while actions < total_actions:
    #     for creature in creature_list:
    #         if creature.actions_left >= 1:
    #             creature.actions_left -= 1
    #             actions += 1
    #             creature.turn()
    #             print(creature.name)


    actions_left = len(creature_list)   # amount of creatures that can still act
    while actions_left > 0:  # loops until every creature acted
        actions_left = len(creature_list)
        for creature in creature_list:
            if creature.actions_left > 0:
                creature.turn()
                creature.actions_left -= 1
            else:
                actions_left -= 1
    for creature in creature_list:  # refreshes all actions left for each creature
        creature.actions_left += creature.speed


def player_turn():
    global log
    while not end_turn:
        show_map()
        log = []
        global input_char
        print("(a)ttack, loo(k), move (numpad) or (q)uit:")
        input_char = msvcrt.getch()
        try:
            input_char = bytes.decode(input_char)
            handle_input(input_char)
        except UnicodeDecodeError:
            log.append("Invalid input.\n")


def spawn(creature):
    spawned = False
    while not spawned:
        x = random.randint(0, map_width-1)
        y = random.randint(0, map_height-1)
        if map_creatures[x, y] == '' and map_terrain[x, y] == '':
            creature.x = x
            creature.y = y
            refresh_map_creatures()
            spawned = True


def basic_turn(creature):
    global player
    if not player.dead:
        min_range = creature.weapon.min_range
        max_range = creature.weapon.max_range
        x_distance = player.x - creature.x
        y_distance = player.y - creature.y
        # checks if enemy is within max weapon range
        if abs(x_distance) <= max_range and abs(y_distance) <= max_range and (abs(x_distance) >= min_range or abs(y_distance) >= min_range):
            creature_attack(creature, player)
        else:
            path = walk_to(creature, player)
            if path is not None:
                next_pos = path[0]
                creature.x = next_pos[0]
                creature.y = next_pos[1]


# def walk_to_goal(creature, goal):
#     min_range = creature.weapon.min_range
#     max_range = creature.weapon.max_range
#     x_distance = goal.x - creature.x
#     y_distance = goal.y - creature.y
#     new_pos = [creature.x, creature.y]
#     if abs(x_distance) > max_range or abs(y_distance) > max_range:
#         if x_distance < 0 and y_distance < 0:
#             new_pos = [creature.x - 1, creature.y - 1]
#         elif x_distance == 0 and y_distance < 0:
#             new_pos = [creature.x, creature.y - 1]
#         elif x_distance > 0 and y_distance < 0:
#             new_pos = [creature.x + 1, creature.y - 1]
#         elif x_distance < 0 and y_distance == 0:
#             new_pos = [creature.x - 1, creature.y]
#         elif x_distance > 0 and y_distance == 0:
#             new_pos = [creature.x + 1, creature.y]
#         elif x_distance < 0 and y_distance > 0:
#             new_pos = [creature.x - 1, creature.y + 1]
#         elif x_distance == 0 and y_distance > 0:
#             new_pos = [creature.x, creature.y + 1]
#         elif x_distance > 0 and y_distance > 0:
#             new_pos = [creature.x + 1, creature.y + 1]
#     elif abs(x_distance) < min_range and abs(y_distance) < min_range:
#         if x_distance < 0 and y_distance < 0:
#             new_pos = [creature.x + 1, creature.y + 1]
#         elif x_distance == 0 and y_distance < 0:
#             new_pos = [creature.x, creature.y + 1]
#         elif x_distance > 0 and y_distance < 0:
#             new_pos = [creature.x - 1, creature.y + 1]
#         elif x_distance < 0 and y_distance == 0:
#             new_pos = [creature.x + 1, creature.y]
#         elif x_distance > 0 and y_distance == 0:
#             new_pos = [creature.x - 1, creature.y]
#         elif x_distance < 0 and y_distance > 0:
#             new_pos = [creature.x + 1, creature.y - 1]
#         elif x_distance == 0 and y_distance > 0:
#             new_pos = [creature.x, creature.y - 1]
#         elif x_distance > 0 and y_distance > 0:
#             new_pos = [creature.x - 1, creature.y - 1]
#     if 0 <= new_pos[0] < map_width and 0 <= new_pos[1] < map_height:
#         if map_creatures[new_pos[0], new_pos[1]] == '' and map_terrain[new_pos[0], new_pos[1]] == '':
#             creature.x = new_pos[0]
#             creature.y = new_pos[1]
#         elif creature.speech:
#             log.append("The {} shouts for mercy!\n".format(creature.name))
#     elif creature.speech:
#         log.append("The {} shouts for mercy!\n".format(creature.name))


def creature_attack(creature, target):
    weapon = creature.weapon
    critical_hit = False
    log.append("The {} attacks the {}.\n".format(creature.name, target.name))
    attack_roll = random.randint(1, 20)
    if creature.attack_modifier > 0:
        log.append("They roll {}+{} to hit.\n".format(attack_roll, creature.attack_modifier))
    elif creature.attack_modifier < 0:
        log.append("They roll {}{} to hit.\n".format(attack_roll, creature.attack_modifier))
    else:
        log.append("They roll {} to hit.\n".format(attack_roll))
    if attack_roll == 20:
        log.append("It's a critical hit! They're guaranteed to hit with extra damage.\n")
        critical_hit = True
    attack_roll += creature.attack_modifier
    if attack_roll >= target.armor or critical_hit:
        if critical_hit:
            damage_roll1 = random.randint(1, weapon.damage)
            damage_roll2 = random.randint(1, weapon.damage)
            damage_roll = damage_roll1 + damage_roll2
            log.append("They hit the {} for {}+{} damage.\n".format(target.name, damage_roll1, damage_roll2))
        else:
            damage_roll = random.randint(1, weapon.damage)
            log.append("They hit the {} for {} damage.\n".format(target.name, damage_roll))
        target.current_health -= damage_roll
        if target.current_health > 0:
            log.append("The {} has {} hit points left.\n".format(target.name, target.current_health))
        elif target == player:
            on_player_dead()
        else:
            on_creature_dead(target)
    else:
        log.append("But they miss.\n")


class Weapon:
    def __init__(self, weapon_name, min_range, max_range, damage):
        self.name = weapon_name
        self.min_range = min_range
        self.max_range = max_range
        self.damage = damage


class Player:
    name = "player"
    symbol = 'O'

    def __init__(self, team):
        self.max_health = 100
        self.current_health = self.max_health
        self.max_mana = 100
        self.current_mana = self.max_mana
        self.armor = 12
        self.attack_modifier = 2
        self.weapon = sword
        self.speed = 1
        self.actions_left = self.speed
        self.dead = False
        self.team = team
        self.x = 2
        self.y = 2
        spawn(self)

    def turn(self):
        player_turn()
        refresh_map_creatures()


class Goblin:
    name = "goblin"
    symbol = 'g'

    def __init__(self, team):
        self.max_health = 0
        for x in range(4):
            self.max_health += random.randint(1, 6)
        self.current_health = self.max_health
        self.max_mana = 0
        self.current_mana = self.max_mana
        self.armor = 10 + random.randint(-1, 1)
        self.attack_modifier = random.randint(-1, 2)
        self.weapon = shortsword
        self.speed = 3
        self.actions_left = self.speed
        self.goal = None
        self.speech = True
        self.team = team
        self.x = 0
        self.y = 0
        spawn(self)

    def turn(self):
        basic_turn(self)
        refresh_map_creatures()


class Zombie:
    name = "zombie"
    symbol = 'z'

    def __init__(self, team):
        self.max_health = 0
        for x in range(4):
            self.max_health += random.randint(1, 8)
        self.current_health = self.max_health
        self.max_mana = 0
        self.current_mana = self.max_mana
        self.armor = 12 + random.randint(-1, 1)
        self.attack_modifier = random.randint(-2, 1)
        self.weapon = claws
        self.speed = 0.5
        self.actions_left = self.speed
        self.goal = None
        self.speech = False
        self.team = team
        self.x = 0
        self.y = 0
        spawn(self)

    def turn(self):
        basic_turn(self)
        refresh_map_creatures()


map_width = 40
map_height = 20

blank_lines = 20

claws = Weapon("claws", 1, 1, 2)
sword = Weapon("sword", 1, 1, 10)
shortsword = Weapon("shortsword", 1, 1, 6)
dagger = Weapon("dagger", 1, 1, 4)
pike = Weapon("pike", 2, 2, 12)
shortbow = Weapon("shortbow", 2, 4, 4)
longbow = Weapon("longbow", 2, 6, 4)

random.seed()

creature_list = []

map_ground = init_map_ground()
map_terrain = init_map_terrain()
map_creatures = []
refresh_map_creatures()
map_temp = init_map_empty()

creature_list.append(Player(1))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
creature_list.append(Zombie(2))
player_index = 0
player = creature_list[player_index]

input_char = '0'
turn_counter = 0
log = []

quit_game = False

while not quit_game and not player.dead:  # 1 loop is 1 turn
    end_turn = False
    new_turn()
    turn_counter += 1

show_map()
