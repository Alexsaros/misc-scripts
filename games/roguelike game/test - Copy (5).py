import numpy as np
import msvcrt
import random
import copy
import curses


def create_creature_of_type(creature_type):
    if creature_type == "goblin":
        creature_list.append(Goblin())
        creature = creature_list[-1]
    elif creature_type == "zombie":
        creature_list.append(Zombie())
        creature = creature_list[-1]
    elif creature_type == "guard":
        creature_list.append(Guard())
        creature = creature_list[-1]
    else:
        print("Error: ", creature_type)
    return creature


def init_map_empty():
    map_empty = np.zeros([map_width, map_height], dtype=str)
    return map_empty


def init_map_ground():
    map_empty = np.zeros([map_width, map_height], dtype=str)
    for y in range(len(map_empty[0])):
        for x in range(len(map_empty)):
            map_empty[x, y] = '·'
    return map_empty


def init_map_terrain(empty=True):
    map_new = np.zeros([map_width, map_height], dtype=object)
    for x in range(map_width):
        for y in range(map_height):
            map_new[x][y] = EmptyTile()
    if not empty:
        if play_mode == 'b':    # creates walls of random length with holes in them at random positions
            wall_ratio = 90     # one wall per amount of tiles
            amount_of_walls = int((map_width * map_height) / wall_ratio)
            for x in range(amount_of_walls):
                horizontal = random.randint(0, 1)
                if horizontal == 1:
                    y = random.randint(0, map_height - 1)
                    length = random.randint(int(map_width * 0.5), int(map_width * 0.9 - 1))
                else:
                    x = random.randint(0, map_width - 1)
                    length = random.randint(int(map_height * 0.5), int(map_height * 0.9 - 1))
                patience = 10   # stops early if it can't find any free spots to place walls
                while length > 0:
                    placed = False
                    while not placed:
                        if horizontal == 1:
                            x = random.randint(0, map_width - 1)
                        else:
                            y = random.randint(0, map_height - 1)
                        if map_new[x, y].symbol == '':
                            map_new[x, y] = Wall()
                            placed = True
                        else:
                            patience -= 1
                        if patience <= 0:
                            placed = True
                            patience = 10
                    length -= 1
        elif play_mode == 'd':
            room_width = 7  # including walls
            room_height = 7
            room_amount_x = map_width/room_width
            room_amount_y = map_height/room_height
            for x in range(map_width):
                print()
    return map_new


def refresh_map_creatures():
    global map_creatures
    map_creatures = np.zeros([map_width, map_height], dtype=str)
    for creature in creature_list:
        map_creatures[creature.x, creature.y] = creature.symbol


def show_map():
    global game_mode
    for x in range(blank_lines):
        print('')
    for line in log:
        print(line, end='')
    if game_mode != 'b':
        print("Turn:", turn_counter)
        refresh_map_creatures()
    temp_map = np.copy(map_ground)
    for y in range(map_height):
        for x in range(map_width):
            if map_temp[x, y] != '':    # top layer is overlay
                temp_map[x, y] = map_temp[x, y]
            elif map_creatures[x, y] != '' and (map_terrain[x, y].visible or game_mode != 'p'):     # next layer is creatures
                temp_map[x, y] = map_creatures[x, y]
            elif map_terrain[x, y].symbol != '' and (map_terrain[x, y].seen or game_mode != 'p'):    # bottom layer is terrain
                temp_map[x, y] = map_terrain[x, y].symbol
            elif not map_terrain[x, y].seen and game_mode == 'p':
                temp_map[x, y] = '█'    # fog of war
    for y in range(map_height - 1, -1, -1):  # walks backwards through the loop so positive y prints up
        for x in range(map_width):
            if temp_map[x, y] != '█':
                print("", temp_map[x, y], "", end='')
            else:
                print('███', end='')
        print('')
    if game_mode == 'p':
        print("Health[{}/{}] Mana[{}/{}] Armor[{}] Weapon[{}] Team[{}] Kills[{}]".format(player.current_health, player.max_health,
                                                                      player.current_mana, player.max_mana,
                                                                      player.armor, player.weapon.name, player.team, player.kills), end='')
        print(" Status[", end='')
        amount = len(player.statuses)
        if amount > 0:
            for status in player.statuses:
                if amount <= 1:
                    print("{}".format(status), end='')
                else:
                    print("{}, ".format(status), end ='')
                amount -= 1
        print("]")


def sort_tile_cost(given_list):
    return given_list[2]


def get_distance(a, b):
    try:
        if len(a) >= 2:
            a = a
    except TypeError:
        a = [a.x, a.y]
    try:
        if len(b) >= 2:
            b = b
    except TypeError:
        b = [b.x, b.y]
    distance_x = abs(a[0] - b[0])
    distance_y = abs(a[1] - b[1])
    if distance_x > distance_y:
        return distance_x
    else:
        return distance_y


def walk_to(begin_pos, end_pos):
    # tile = [x, y, total_cost, parent_tile]
    try:
        if len(begin_pos) >= 2:
            start = begin_pos
    except TypeError:
        start = [begin_pos.x, begin_pos.y]
    try:
        if len(end_pos) >= 2:
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
                if (map_creatures[new_tile[0], new_tile[1]] == '' or new_tile[:2] == goal) and map_terrain[new_tile[0], new_tile[1]].blocks_movement == False:
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
                if map_creatures[new_pos[0], new_pos[1]] == '' and map_terrain[new_pos[0], new_pos[1]].blocks_movement == False:
                    player.x = new_pos[0]
                    player.y = new_pos[1]
                    end_turn = True
                # moving onto occupied tile attacks creature if melee weapon
                elif map_creatures[new_pos[0], new_pos[1]] != '' and player.weapon.min_range <= 1 and player.weapon.max_range <= 1:
                    for creature in creature_list:
                        if creature.x == new_pos[0] and creature.y == new_pos[1]:
                            player_attack(creature)
                            break
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
        elif command == 'i':
            open_inventory()
        elif command == 'q':
            end_turn = True
            quit_game = True
        else:
            log.append("Invalid input.\n")


def look_at(location=0):
    global map_temp
    global log
    global input_char
    if location == 0:
        cursor = [player.x, player.y]
    else:
        cursor = [int(location[0]), int(location[1])]
    command = ''
    while command != 'x':
        map_temp = init_map_empty()
        map_temp[cursor[0], cursor[1]] = '▢'
        creature = map_creatures[cursor[0], cursor[1]]
        if creature != '':
            for creature in creature_list:
                if creature.x == cursor[0] and creature.y == cursor[1]:
                    log.append("You see a {} from team {}\n".format(creature.name, creature.team))
                    log.append("Health[{}/{}] Armor[{}] Weapon[{}] Alignment[{}]".format(creature.current_health,
                                                                                         creature.max_health, creature.armor, creature.weapon.name, creature.alignment))
                    if len(creature.statuses) > 0:
                        log.append(" Status[")
                        amount = len(creature.statuses)
                        for status in creature.statuses:
                            if amount <= 1:
                                log.append("{}".format(status))
                            else:
                                log.append("{}, ".format(status))
                            amount -= 1
                        log.append("]\n")
                    else:
                        log.append("\n")
                    break
        show_map()
        log = []
        print("Move (numpad) or e(x)it:")
        input_char = msvcrt.getch()
        try:
            command = bytes.decode(input_char)
            try:
                if 1 <= int(command) <= 9 and int(command) != 5:
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


def open_inventory():
    global log
    command = ''
    while command != 'x':
        log = []
        for x in range(blank_lines):
            print('')
        try:
            if int(command) > 0:
                if isinstance(player.inventory[int(command) - 1], Weapon):
                    player.weapon = player.inventory[int(command) - 1]
                    log.append("You have equipped the {}.\n".format(player.weapon.name))
        except ValueError:
            log = []    # do nothing
        number = 0
        for item in player.inventory:
            number += 1
            log.append("{}. ".format(number))
            if isinstance(item, Weapon):
                log.append("Weapon[{}] Range[{}-{}] Damage[{}]\n".format(item.name, item.min_range, item.max_range, item.damage))
            else:
                log.append("Item[{}]\n".format(item.name))
        for line in log:
            print(line, end='')
        print("Input the number of the item you want to equip/use or e(x)it:")
        command = msvcrt.getch()
        try:
            command = bytes.decode(command)
        except UnicodeDecodeError:
            log.append("Invalid input.\n")
    log = []


def creature_in_range(action):
    global log
    global player
    actual_target = None
    max_range = action.max_range
    min_range = action.min_range
    targets = []
    for target in creature_list:  # checks if creature is (inside of max range) and (not inside of min range)
        x_distance = target.x - player.x
        y_distance = target.y - player.y
        if abs(x_distance) <= max_range and abs(y_distance) <= max_range and (abs(x_distance) >= min_range or abs(y_distance) >= min_range):
            targets.append(target)
    visible_tiles = tiles_that_are_attackable(player)
    visible_targets = []
    for target in targets:  # only targets visible creatures
        for tile in visible_tiles:
            if target.x == tile[0] and target.y == tile[1]:
                visible_targets.append(target)
                break
    targets = visible_targets
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


def tiles_that_are_attackable(creature):
    directions = [[-1, 1], [1, 1], [1, -1], [-1, -1]]
    seen_tiles = [[creature.x, creature.y]]
    for direction in directions:
        for change_dir_amount in range(creature.sight_range):     # decides how often to switch up direction
            counter = 0
            current_tile = [creature.x, creature.y]
            for x in range(creature.sight_range):   # looks until it hits the end of vision
                current_tile[0] += direction[0]
                counter += 1
                if counter >= change_dir_amount + 1:
                    counter = 0
                    current_tile[1] += direction[1]
                if 0 <= current_tile[0] < map_width and 0 <= current_tile[1] < map_height:
                    seen_tiles.append([current_tile[0], current_tile[1]])
                    if map_terrain[current_tile[0], current_tile[1]].blocks_sight or map_terrain[current_tile[0], current_tile[1]].blocks_projectiles:
                        break
            counter = 0
            current_tile = [creature.x, creature.y]
            for x in range(creature.sight_range):   # looks until it hits the end of vision going the other way
                current_tile[0] += direction[0]
                current_tile[1] += direction[1]
                counter += 1
                if counter >= change_dir_amount + 1:
                    counter = 0
                    current_tile[1] -= direction[1]
                if 0 <= current_tile[0] < map_width and 0 <= current_tile[1] < map_height:
                    seen_tiles.append([current_tile[0], current_tile[1]])
                    if map_terrain[current_tile[0], current_tile[1]].blocks_sight or map_terrain[current_tile[0], current_tile[1]].blocks_projectiles:
                        break
            counter = 0
            current_tile = [creature.x, creature.y]
            for x in range(creature.sight_range):   # looks until it hits the end of vision for the second half
                current_tile[1] += direction[1]
                counter += 1
                if counter >= change_dir_amount + 1:
                    counter = 0
                    current_tile[0] += direction[0]
                if 0 <= current_tile[0] < map_width and 0 <= current_tile[1] < map_height:
                    seen_tiles.append([current_tile[0], current_tile[1]])
                    if map_terrain[current_tile[0], current_tile[1]].blocks_sight or map_terrain[current_tile[0], current_tile[1]].blocks_projectiles:
                        break
            counter = 0
            current_tile = [creature.x, creature.y]
            for x in range(creature.sight_range):   # looks until it hits the end of vision going the other way
                current_tile[1] += direction[1]
                current_tile[0] += direction[0]
                counter += 1
                if counter >= change_dir_amount + 1:
                    counter = 0
                    current_tile[0] -= direction[0]
                if 0 <= current_tile[0] < map_width and 0 <= current_tile[1] < map_height:
                    seen_tiles.append([current_tile[0], current_tile[1]])
                    if map_terrain[current_tile[0], current_tile[1]].blocks_sight or map_terrain[current_tile[0], current_tile[1]].blocks_projectiles:
                        break
    return seen_tiles


def tiles_in_sight(creature):
    directions = [[-1, 1], [1, 1], [1, -1], [-1, -1]]
    seen_tiles = [[creature.x, creature.y]]
    for direction in directions:
        for change_dir_amount in range(creature.sight_range):     # decides how often to switch up direction
            counter = 0
            current_tile = [creature.x, creature.y]
            for x in range(creature.sight_range):   # looks until it hits the end of vision
                current_tile[0] += direction[0]
                counter += 1
                if counter >= change_dir_amount + 1:
                    counter = 0
                    current_tile[1] += direction[1]
                if 0 <= current_tile[0] < map_width and 0 <= current_tile[1] < map_height:
                    seen_tiles.append([current_tile[0], current_tile[1]])
                    if map_terrain[current_tile[0], current_tile[1]].blocks_sight:
                        break
            counter = 0
            current_tile = [creature.x, creature.y]
            for x in range(creature.sight_range):   # looks until it hits the end of vision going the other way
                current_tile[0] += direction[0]
                current_tile[1] += direction[1]
                counter += 1
                if counter >= change_dir_amount + 1:
                    counter = 0
                    current_tile[1] -= direction[1]
                if 0 <= current_tile[0] < map_width and 0 <= current_tile[1] < map_height:
                    seen_tiles.append([current_tile[0], current_tile[1]])
                    if map_terrain[current_tile[0], current_tile[1]].blocks_sight:
                        break
            counter = 0
            current_tile = [creature.x, creature.y]
            for x in range(creature.sight_range):   # looks until it hits the end of vision for the second half
                current_tile[1] += direction[1]
                counter += 1
                if counter >= change_dir_amount + 1:
                    counter = 0
                    current_tile[0] += direction[0]
                if 0 <= current_tile[0] < map_width and 0 <= current_tile[1] < map_height:
                    seen_tiles.append([current_tile[0], current_tile[1]])
                    if map_terrain[current_tile[0], current_tile[1]].blocks_sight:
                        break
            counter = 0
            current_tile = [creature.x, creature.y]
            for x in range(creature.sight_range):   # looks until it hits the end of vision going the other way
                current_tile[1] += direction[1]
                current_tile[0] += direction[0]
                counter += 1
                if counter >= change_dir_amount + 1:
                    counter = 0
                    current_tile[0] -= direction[0]
                if 0 <= current_tile[0] < map_width and 0 <= current_tile[1] < map_height:
                    seen_tiles.append([current_tile[0], current_tile[1]])
                    if map_terrain[current_tile[0], current_tile[1]].blocks_sight:
                        break
    return seen_tiles


def update_visible_tiles(visible_tiles):
    for x in range(map_width):
        for y in range(map_height):
            map_terrain[x, y].visible = False
    for tile in visible_tiles:
        map_terrain[tile[0], tile[1]].visible = True
        map_terrain[tile[0], tile[1]].seen = True


def player_attack(target=None):
    global player
    global log
    global end_turn
    weapon = player.weapon
    if target is None:
        target = creature_in_range(weapon)
    if target is not None:  # if a target has been chosen
        end_turn = True
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
                player.kills += 1
                if target.alignment == "good":
                    player.alignment = "evil"
                on_creature_dead(target)
        else:
            log.append("But you miss.\n")


def on_creature_dead(creature):
    log.append("The {} died.\n".format(creature.name))
    creature.dead = True
    for status in creature.statuses:    # if creature is infected, spawn zombie at creature's location
        if status == "infected":
            creature_list.append(Zombie())
            zombie = creature_list[-1]
            log.append("A {} has risen from the {}'s corpse.\n".format(zombie.name, creature.name))
            zombie.x = creature.x
            zombie.y = creature.y
            break
    index = 0
    for x in creature_list:     # finds and deletes dead creature in creature_list
        if x == creature:
            del creature_list[index]
            break
        index += 1


def on_player_dead():
    global player
    global input_char
    global game_mode
    global quit_game
    global log
    player.dead = True
    log.append("You have died.\n")
    for status in player.statuses:    # if creature is infected, spawn zombie at creature's location
        if status == "infected":
            creature_list.append(Zombie())
            zombie = creature_list[-1]
            log.append("A {} has risen from your corpse.\n".format(zombie.name))
            zombie.x = player.x
            zombie.y = player.y
            break
    del creature_list[player_index]
    show_map()
    decision_made = False
    while not decision_made:
        log = []
        print("Do you want to continue watching the fight?\n(y)es or (n)o")
        input_char = msvcrt.getch()
        try:
            input_char = bytes.decode(input_char)
            if input_char == 'y':
                game_mode = 'w'
                decision_made = True
            elif input_char == 'n':
                quit_game = True
                decision_made = True
            else:
                for x in range(blank_lines):
                    print('')
                log.append("Invalid input.\n")
                show_map()
        except UnicodeDecodeError:
            for x in range(blank_lines):
                print('')
            log.append("Invalid input.\n")
            show_map()
    log = []


def new_turn():
    for creature in creature_list:
        while creature.actions_left >= 1:
            creature.turn()
            creature.actions_left -= 1
    for creature in creature_list:  # refreshes all actions left for each creature
        creature.actions_left += creature.speed
    spawn_new_enemies()


def spawn_new_enemies():
    global creature_cap
    global species_cap
    global map_creatures
    roll = random.randint(0, creature_cap) + len(creature_list)
    if roll < creature_cap:
        npc_list = []
        for x in npc_types:
            npc_list.append([0, 0])     # amount and roll for every npc type
        for creature in creature_list:   # gets existing amount of each npc type
            for x in range(len(npc_types)):
                if creature.name == npc_types[x]:
                    npc_list[x][0] = npc_list[x][0] + 1
                    break
        for x in range(len(npc_list)):
            npc_list[x][1] = random.randint(0, int(species_cap)) - npc_list[x][0]
        roll = None
        for x in range(len(npc_list)):
            if (roll is None or npc_list[x][1] > roll) and npc_spawn_directions[x] != "nnnn":
                roll = npc_list[x][1]
                index = x
                chosen_creature = npc_types[index]
        creature = create_creature_of_type(chosen_creature)
        possible_directions = 0
        for direction in npc_spawn_directions[index]:
            if direction == 'y':
                possible_directions += 1
        side = random.randint(1, possible_directions)
        for x in range(4):
            if side == 1:
                side = x
            elif npc_spawn_directions[index] == 'y':
                side -= 1
        patience = 10
        spawned = False
        if side == 1:   # north
            while not spawned:
                x = random.randint(0, map_width-1)
                y = map_height-1
                if map_creatures[x, y] == '' and map_terrain[x, y].blocks_movement == False:
                    creature.x = x
                    creature.y = y
                    map_creatures[creature.x, creature.y] = creature.symbol
                    log.append("A {} has joined the battle from the north.\n".format(creature.name))
                    spawned = True
                patience -= 1
                if patience <= 0:
                    del creature_list[-1]
                    break
        elif side == 2:     # east
            while not spawned:
                x = map_width-1
                y = random.randint(0, map_height-1)
                if map_creatures[x, y] == '' and map_terrain[x, y].blocks_movement == False:
                    creature.x = x
                    creature.y = y
                    map_creatures[creature.x, creature.y] = creature.symbol
                    log.append("A {} has joined the battle from the east.\n".format(creature.name))
                    spawned = True
                patience -= 1
                if patience <= 0:
                    del creature_list[-1]
                    break
        elif side == 3:     # south
            while not spawned:
                x = random.randint(0, map_width - 1)
                y = 0
                if map_creatures[x, y] == '' and map_terrain[x, y].blocks_movement == False:
                    creature.x = x
                    creature.y = y
                    map_creatures[creature.x, creature.y] = creature.symbol
                    log.append("A {} has joined the battle from the south.\n".format(creature.name))
                    spawned = True
                patience -= 1
                if patience <= 0:
                    del creature_list[-1]
                    break
        else:   # west
            while not spawned:
                x = 0
                y = random.randint(0, map_height - 1)
                if map_creatures[x, y] == '' and map_terrain[x, y].blocks_movement == False:
                    creature.x = x
                    creature.y = y
                    map_creatures[creature.x, creature.y] = creature.symbol
                    log.append("A {} has joined the battle from the west.\n".format(creature.name))
                    spawned = True
                patience -= 1
                if patience <= 0:
                    del creature_list[-1]
                    break


def player_turn():
    global log
    global input_char
    visible_tiles = tiles_in_sight(player)
    update_visible_tiles(visible_tiles)
    while not end_turn:
        show_map()
        log = []
        print("(a)ttack, loo(k), (i)nventory, move (numpad) or (q)uit:")
        input_char = msvcrt.getch()
        try:
            input_char = bytes.decode(input_char)
            handle_input(input_char)
        except UnicodeDecodeError:
            log.append("Invalid input.\n")
    if player.current_mana < player.max_mana:
        player.current_mana += 1
    refresh_map_creatures()


def spawn(creature):
    global creature_list
    global map_creatures
    spawned = False
    patience = 10
    while not spawned:
        x = random.randint(0, map_width-1)
        y = random.randint(0, map_height-1)
        if map_creatures[x, y] == '' and map_terrain[x, y].blocks_movement == False:
            creature.x = x
            creature.y = y
            map_creatures[creature.x, creature.y] = creature.symbol
            spawned = True
            return spawned
        else:
            patience -= 1
        if patience <= 0:
            return spawned


def basic_turn(creature):
    all_enemies = []    # gets all enemies on the field
    if creature.alignment == "evil":
        for enemy in creature_list:     # attacks all other teams
            if enemy.team != creature.team:
                all_enemies.append(enemy)
    elif creature.alignment == "good":
        for enemy in creature_list:     # attacks all evil characters
            if enemy.alignment == "evil":
                all_enemies.append(enemy)
    elif creature.alignment == "neutral":
        print("need to implement this alignment behaviour")
    else:
        print("error in creature alignment:", creature.alignment)
    visible_tiles = tiles_in_sight(creature)
    distance = creature.sight_range
    for enemy in all_enemies:
        if get_distance(creature, enemy) < distance:   # if new enemy is closer than previous enemy
            for tile in visible_tiles:   # checks if closer enemy is visible
                if enemy.x == tile[0] and enemy.y == tile[1]:
                    distance = get_distance(creature, enemy)
                    creature.target = enemy
    target = creature.target
    if target is not None and not target.dead:
        min_range = creature.weapon.min_range
        max_range = creature.weapon.max_range
        x_distance = target.x - creature.x
        y_distance = target.y - creature.y
        attackable_tiles = tiles_that_are_attackable(creature)
        attackable = False
        for tile in attackable_tiles:
            if target.x == tile[0] and target.y == tile[1]:   # if enemy is on a targetable tile
                attackable = True
                break
        # checks if enemy is within weapon range and not blocked by walls
        if attackable and abs(x_distance) <= max_range and abs(y_distance) <= max_range and (abs(x_distance) >= min_range or abs(y_distance) >= min_range):
            creature_attack(creature, target)
        else:
            if abs(x_distance) > max_range or abs(y_distance) > max_range or not attackable:
                path = walk_to(creature, target)
                if path is not None:
                    next_pos = path[0]
                    creature.x = next_pos[0]
                    creature.y = next_pos[1]
            elif abs(x_distance) < min_range and abs(y_distance) < min_range:
                walk_away(creature, target)
            else:
                print("error in basic_turn")
    if creature.current_mana < creature.max_mana:
        creature.current_mana += 1
    refresh_map_creatures()


def walk_away(creature, target):
    x_distance = target.x - creature.x
    y_distance = target.y - creature.y
    side_dirs = []
    new_pos = [creature.x, creature.y]
    if x_distance < 0 and y_distance < 0:
        new_pos = [creature.x + 1, creature.y + 1]
        side_dirs = [[0, 1], [1, 0], [-1, 1], [1, -1]]
    elif x_distance == 0 and y_distance < 0:
        new_pos = [creature.x, creature.y + 1]
        side_dirs = [[-1, 1], [1, 1]]
    elif x_distance > 0 and y_distance < 0:
        new_pos = [creature.x - 1, creature.y + 1]
        side_dirs = [[-1, 0], [0, 1], [-1, -1], [1, 1]]
    elif x_distance < 0 and y_distance == 0:
        new_pos = [creature.x + 1, creature.y]
        side_dirs = [[1, 1], [1, -1]]
    elif x_distance > 0 and y_distance == 0:
        new_pos = [creature.x - 1, creature.y]
        side_dirs = [[-1, -1], [-1, 1]]
    elif x_distance < 0 and y_distance > 0:
        new_pos = [creature.x + 1, creature.y - 1]
        side_dirs = [[1, 0], [0, -1], [1, 1], [-1, -1]]
    elif x_distance == 0 and y_distance > 0:
        new_pos = [creature.x, creature.y - 1]
        side_dirs = [[1, -1], [-1, -1]]
    elif x_distance > 0 and y_distance > 0:
        new_pos = [creature.x - 1, creature.y - 1]
        side_dirs = [[0, -1], [-1, 0], [1, -1], [-1, 1]]
    blocked = False
    if 0 <= new_pos[0] < map_width and 0 <= new_pos[1] < map_height:
        if map_creatures[new_pos[0], new_pos[1]] == '' and map_terrain[new_pos[0], new_pos[1]].blocks_movement == False:
            creature.x = new_pos[0]
            creature.y = new_pos[1]
        else:
            blocked = True
    else:
        blocked = True
    if blocked:     # tries to sidestep backwards
        new_pos = [creature.x, creature.y]
        for directions in side_dirs:
            new_pos[0] += directions[0]
            new_pos[1] += directions[1]
            if 0 <= new_pos[0] < map_width and 0 <= new_pos[1] < map_height and map_creatures[new_pos[0], new_pos[1]] == '' and map_terrain[new_pos[0], new_pos[1]].blocks_movement == False:
                creature.x = new_pos[0]
                creature.y = new_pos[1]
                blocked = False
                break
            else:   # gets original position back
                new_pos[0] -= directions[0]
                new_pos[1] -= directions[1]
        if blocked:     # tries to walk behind the creature
            new_pos = [creature.x + x_distance * 3, creature.y + y_distance * 3]
            path = walk_to(creature, new_pos)
            if path is not None:
                next_pos = path[0]
                creature.x = next_pos[0]
                creature.y = next_pos[1]
            else:
                new_pos = [creature.x + x_distance * 2, creature.y + y_distance * 2]
                path = walk_to(creature, new_pos)
                if path is not None:
                    next_pos = path[0]
                    creature.x = next_pos[0]
                    creature.y = next_pos[1]
                elif creature.speech:
                    log.append("The {} shouts for mercy.\n".format(creature.name))


def creature_attack(creature, target):
    weapon = creature.weapon
    critical_hit = False
    attack_roll = random.randint(1, 20)
    if target == player or not show_only_attacks_on_player:    # shows only attacks targetting player
        if creature.attack_modifier > 0:
            log.append("The {} rolls {}+{} to attack the {} ".format(creature.name, attack_roll, creature.attack_modifier, target.name))
        elif creature.attack_modifier < 0:
            log.append("The {} rolls {}{} to attack the {} ".format(creature.name, attack_roll, creature.attack_modifier, target.name))
        else:
            log.append("The {} rolls {} to attack the {} ".format(creature.name, attack_roll, target.name))
    if attack_roll == 20:
        critical_hit = True
    attack_roll += creature.attack_modifier
    if attack_roll >= target.armor or critical_hit:
        if creature.name == "zombie":
            infected = False
            for status in target.statuses:
                if status == "infected":
                    infected = True
                    break
            if not infected:
                target.statuses.append("infected")
        if critical_hit:
            damage_roll1 = random.randint(1, weapon.damage)
            damage_roll2 = random.randint(1, weapon.damage)
            damage_roll = damage_roll1 + damage_roll2
            if target == player or not show_only_attacks_on_player:     # shows only attacks targetting player
                log.append("for {}+{} damage.\n".format(damage_roll1, damage_roll2))
        else:
            damage_roll = random.randint(1, weapon.damage)
            if target == player or not show_only_attacks_on_player:     # shows only attacks targetting player
                log.append("for {} damage.\n".format(damage_roll))
        target.current_health -= damage_roll
        if target.current_health > 0 and (target == player or not show_only_attacks_on_player):
            log.append("The {} has {} hit points left.\n".format(target.name, target.current_health))
        elif player is not None and target == player:
            creature.kills += 1
            on_player_dead()
        else:
            creature.kills += 1
            on_creature_dead(target)
    elif target == player or not show_only_attacks_on_player:
        log.append("but misses.\n")


def build_mode():
    global map_temp
    global log
    global input_char
    global quit_game
    cursor = [int(map_width/2), int(map_height/2)]
    command = ''
    while command != 'q':
        map_temp = init_map_empty()
        map_temp[cursor[0], cursor[1]] = '▢'
        show_map()
        log = []
        print("Move (numpad), (p)lace/(r)emove wall, (s)ave map or (q)uit:")
        input_char = msvcrt.getch()
        try:
            command = bytes.decode(input_char)
            try:
                if 1 <= int(command) <= 9 and int(command) != 5:
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
                if command == 'p':
                    map_terrain[cursor[0], cursor[1]] = Wall()
                elif command == 'r':
                    map_terrain[cursor[0], cursor[1]] = EmptyTile()
                elif command == 's':
                    save_map()
                elif command == 'q':
                    quit_game = True
                    break
                else:
                    log.append("Invalid command: {}\n".format(command))
        except UnicodeDecodeError:
            log.append("Invalid input: {}.\n".format(input_char))
    map_temp = init_map_empty()


def save_map():
    map_name = input("What do you want to name the map (without .txt): ") + ".txt"
    file = open(map_name, "w+")
    file.write("{}\n{}\n".format(map_width, map_height))  # saves map width and height
    for y in range(len(map_terrain[0])):
        for x in range(len(map_terrain)):
            if map_terrain[x, y].symbol != '':
                file.write("{}".format(map_terrain[x, y].symbol))
            else:
                file.write(" ")
        file.write("\n")
    for creature in npc_types:
        finished = False
        chars = 0
        for x in range(blank_lines):
            print('')
        while not finished:
            print("Enter how you want each creature to enter the map from the directions: north, east, south, west.")
            print("Type 'y' to allow the creature to enter from that direction or 'n' to forbid it. (e.g. 'yyny')")
            settings = input("How do you want a {} to be able to enter the map? ".format(creature))
            if len(settings) == 4:
                for char in settings:
                    if char == 'y' or char == 'n':
                        chars += 1
                        file.write(char)
                    else:
                        for x in range(blank_lines):
                            print('')
                        print("Invalid input.")
                        break
                if chars == 4:
                    finished = True
                    file.write("\n")
            else:
                print("Invalid input.")
                for x in range(blank_lines):
                    print('')
    file.close()


def load_map():
    global map_width
    global map_height
    global map_terrain
    global loaded_map
    global npc_spawn_directions
    for x in range(blank_lines):
        print('')
    while not loaded_map:
        map_name = input("Input the name of the map you want to load (without .txt) or type \"exit\" to go back.\n") + ".txt"
        for x in range(blank_lines):
            print('')
        if map_name != "exit.txt":
            try:
                file = open(map_name, "r")
                loaded_map = True
                lines = file.readlines()
                map_width = int(lines[0])
                map_height = int(lines[1])
                lines = lines[2:]
                map_terrain = init_map_terrain(empty=True)
                for x in range(map_width):
                    for y in range(map_height):
                        if lines[y][x] == ' ':
                            map_terrain[x, y] = EmptyTile()
                        elif lines[y][x] == '#':
                            map_terrain[x, y] = Wall()
                        else:
                            print("Error, unknown tile:", lines[y][x])
                lines = lines[map_height:]
                for x in range(len(npc_spawn_directions)):
                    npc_spawn_directions[x] = lines[x][:4]
                lines = lines[len(npc_spawn_directions):]
            except FileNotFoundError:
                print("No file called {} found. Make sure it's in the same directory as this game and that it's spelled correctly.".format(map_name))
        else:
            break


def at_start_of_game():
    global loaded_map
    global input_char
    for x in range(blank_lines):
        print('')
    while not loaded_map:   # makes sure a map will be created
        print("Do you want to load a map from your pc?")
        print("(y)es or (n)o")
        input_char = msvcrt.getch()
        try:
            answer = bytes.decode(input_char)
            if answer == 'y':
                load_map()
            elif answer == 'n':
                loaded_map = False
                init_new_map()
                break
            else:
                for x in range(blank_lines):
                    print('')
                print("Invalid input.")
        except UnicodeDecodeError:
            for x in range(blank_lines):
                print('')
            print("Invalid input.")
    choose_game_mode()


def init_new_map():
    global map_width
    global map_height
    map_size_chosen = False
    for x in range(blank_lines):
        print('')
    while not map_size_chosen:
        try:
            map_width = int(
                input("Input the number of tiles you want the map width to be and press enter: "))
            map_height = int(
                input("Input the number of tiles you want the map height to be and press enter: "))
            if map_width < 1 or map_height < 1:
                for x in range(blank_lines):
                    print('')
                print("Map width or height can't be smaller than 1 tile.")
            else:
                map_size_chosen = True
        except ValueError:
            for x in range(blank_lines):
                print('')
            print("Invalid input")


def choose_game_mode():
    global input_char
    global game_mode
    game_mode_chosen = False
    for x in range(blank_lines):
        print('')
    while not game_mode_chosen:  # chooses game mode
        print("Do you want to (w)atch the AI battle, (p)lay yourself or (b)uild a map?")
        input_char = msvcrt.getch()
        try:
            game_mode = bytes.decode(input_char)
            if game_mode == 'w' or game_mode == 'p' or game_mode == 'b':
                game_mode_chosen = True
            else:
                for x in range(blank_lines):
                    print('')
                print("Invalid input.")
        except UnicodeDecodeError:
            for x in range(blank_lines):
                print('')
            print("Invalid input.")


class Weapon:
    def __init__(self, weapon_name, min_range, max_range, damage):
        self.name = weapon_name
        self.min_range = min_range
        self.max_range = max_range
        self.damage = damage


class TerrainTile:
    def __init__(self):
        self.blocks_movement = False
        self.blocks_sight = False
        self.blocks_projectiles = False
        self.seen = False
        self.visible = False


class EmptyTile(TerrainTile):
    def __init__(self):
        TerrainTile.__init__(self)
        self.symbol = ''


class Wall(TerrainTile):
    def __init__(self):
        TerrainTile.__init__(self)
        self.symbol = '#'
        self.blocks_movement = True
        self.blocks_sight = True
        self.blocks_projectiles = True


class BaseCreature:
    def __init__(self, team):
        self.max_health = 0
        self.current_health = self.max_health
        self.max_mana = 0
        self.current_mana = self.max_mana
        self.armor = 10
        self.attack_modifier = 0
        self.weapon = fists
        self.speed = 1
        self.actions_left = self.speed
        self.sight_range = 5
        # if map_width > map_height:  # allows them to see everything
        #     self.sight_range = map_width
        # else:
        #     self.sight_range = map_height
        self.target = None
        self.dead = False
        self.speech = False
        self.team = team
        self.inventory = []
        self.statuses = []
        self.kills = 0
        self.alignment = "neutral"
        self.x = -1
        self.y = -1
        self.spawned = spawn(self)


class Player(BaseCreature):
    name = "player"
    symbol = '☃'

    def __init__(self, team=0):
        BaseCreature.__init__(self, team)
        self.max_health = 20
        self.current_health = self.max_health
        self.max_mana = 30
        self.current_mana = self.max_mana
        self.armor = 12
        self.attack_modifier = 2
        self.inventory.append(fists)
        self.weapon = self.inventory[0]
        for x in range(2):
            weapon = random.randint(0, 5)
            if weapon == 0:
                self.inventory.append(sword)
            elif weapon == 1:
                self.inventory.append(shortsword)
            elif weapon == 2:
                self.inventory.append(pike)
            elif weapon == 3:
                self.inventory.append(shortbow)
            elif weapon == 4:
                self.inventory.append(longbow)
            else:
                self.inventory.append(dagger)
        self.sight_range = 7
        self.speech = True

    def turn(self):
        player_turn()


class Goblin(BaseCreature):
    symbol = 'g'

    def __init__(self, team=1):
        BaseCreature.__init__(self, team)
        self.name = "goblin"
        for x in range(4):
            self.max_health += random.randint(1, 6)
        self.current_health = self.max_health
        self.armor = 10 + random.randint(-1, 1)
        self.attack_modifier = random.randint(-1, 2)
        weapon = random.randint(1, 4)
        if weapon == 1:
            self.weapon = shortbow
        elif weapon == 2:
            self.weapon = shortsword
        else:
            self.weapon = dagger
        self.speech = True
        self.alignment = "evil"

    def turn(self):
        basic_turn(self)


class Zombie(BaseCreature):
    symbol = 'z'

    def __init__(self, team=2):
        BaseCreature.__init__(self, team)
        self.name = "zombie"
        for x in range(4):
            self.max_health += random.randint(1, 10)
        self.current_health = self.max_health
        self.armor = 8 + random.randint(-1, 1)
        self.attack_modifier = random.randint(-2, 1)
        self.weapon = claws
        self.speed = 0.5
        self.actions_left = self.speed
        self.alignment = "evil"

    def turn(self):
        basic_turn(self)


class Guard(BaseCreature):
    symbol = 'T'

    def __init__(self, team=3):
        BaseCreature.__init__(self, team)
        self.name = "guard"
        for x in range(4):
            self.max_health += random.randint(1, 8)
        self.current_health = self.max_health
        self.attack_modifier = random.randint(0, 2)
        weapon = random.randint(1, 2)
        if weapon == 1:
            self.weapon = shortsword
            self.armor = 12 + random.randint(-1, 1)
            self.name = "guard swordsman"
            self.symbol = 's'
        else:
            self.weapon = shortbow
            self.armor = 10 + random.randint(-1, 1)
            self.name = "guard archer"
            self.symbol = 'a'
        self.alignment = "good"
        self.speech = True

    def turn(self):
        basic_turn(self)


# if adding new creature type, edit npc_types and create_creature_of_type
npc_types = ["goblin", "zombie", "guard"]
npc_spawn_directions = ["yyyy", "yyyy", "yyyy"]
npc_spawn_rates = [100, 500, 50]


# initializing weapons
fists = Weapon("fists", 1, 1, 1)
claws = Weapon("claws", 1, 1, 2)
sword = Weapon("sword", 1, 1, 10)
shortsword = Weapon("shortsword", 1, 1, 6)
dagger = Weapon("dagger", 1, 1, 4)
pike = Weapon("pike", 2, 2, 12)
shortbow = Weapon("shortbow", 2, 4, 4)
longbow = Weapon("longbow", 2, 6, 4)

# initializing variables, maps, etc.
map_width = 30      # width of map in tiles
map_height = 15     # height of map in tiles
blank_lines = 40    # amount of blank lines between each "screen"
random.seed()       # randomizes the randomizer
creature_list = []  # prepares list of creatures
map_creatures = []  # prepares map of creatures
map_terrain = []
input_char = ''
game_mode = ''
loaded_map = False
log = []
creature_map_ratio = 20     # one creature per amount of tiles
show_only_attacks_on_player = False
stdscr = curses.initscr()

at_start_of_game()

# initializes maps and stuff
map_ground = init_map_ground()  # creates empty ground map
creature_cap = int((map_width * map_height) / creature_map_ratio)
species_cap = creature_cap / (0.9 * len(npc_types))    # sets ratio of creatures to species
refresh_map_creatures()     # initializes map of creatures
map_temp = init_map_empty()     # initializes empty overlay map


if game_mode == 'b':     # creates empty map for build map mode
    if not loaded_map:
        map_terrain = init_map_terrain(empty=True)
else:
    if not loaded_map:
        if game_mode == 'p':
            for x in range(blank_lines):
                print('')
            play_mode_chosen = False
            while not play_mode_chosen:
                print("Do you want to play an a (b)attlefield or explore a (d)ungeon?")
                input_char = msvcrt.getch()
                for x in range(blank_lines):
                    print('')
                try:
                    input_char = bytes.decode(input_char)
                    if input_char == 'b':
                        play_mode = 'b'
                        play_mode_chosen = True
                    elif input_char == 'd':
                        play_mode = 'd'
                        play_mode_chosen = True
                    else:
                        print("Invalid input.")
                except UnicodeDecodeError:
                    print("Invalid input.")
        map_terrain = init_map_terrain(empty=False)
    if game_mode == 'p':    # creates the player first in play mode
        creature_list.append(Player())
        player_index = len(creature_list) - 1
        player = creature_list[player_index]
        refresh_map_creatures()

input_char = ''
turn_counter = 0
log = []
quit_game = False
# todo add spells, with map editor edit creature type, add endless dungeon generation
# improve spawning rates, improve vision/ranged attacks
play_mode = 'b'
while not quit_game:
    if game_mode == 'w':
        show_only_attacks_on_player = False
        player = None
        while not quit_game:
            show_map()
            log = []
            print("(q)uit, loo(k) or press any other key to go to the next turn.)")
            input_char = msvcrt.getch()
            try:
                input_char = bytes.decode(input_char)
                if input_char == 'q':
                    new_turn()
                    turn_counter += 1
                    quit_game = True
                elif input_char == 'k':
                    middle = [map_width/2, map_height/2]
                    look_at(location=middle)
                else:
                    new_turn()
                    turn_counter += 1
            except UnicodeDecodeError:
                log.append("Invalid input.\n")
    elif game_mode == 'p':
        show_only_attacks_on_player = True
        while not quit_game and not player.dead:  # 1 loop is 1 turn
            end_turn = False
            new_turn()
            turn_counter += 1
    elif game_mode == 'b':
        build_mode()
    else:
        print("Error {}".format(game_mode))

show_map()
