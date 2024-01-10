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
    # creates walls of random length with holes in them at random positions
    for x in range(5):
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
                if map_empty[x, y] == '':
                    map_empty[x, y] = '#'
                    placed = True
                else:
                    patience -= 1
                if patience <= 0:
                    placed = True
                    patience = 10
            length -= 1
    return map_empty


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
            elif map_creatures[x, y] != '':     # next layer is creatures
                temp_map[x, y] = map_creatures[x, y]
            elif map_terrain[x, y] != '':       # bottom layer is terrain
                temp_map[x, y] = map_terrain[x, y]
    for y in range(map_height - 1, -1, -1):  # walks backwards through the loop so positive y prints up
        for x in range(map_width):
            print("", temp_map[x, y], "", end='')
        print('')
    if game_mode == 'p':
        print("Health[{}/{}] Mana[{}/{}] Armor[{}] Weapon[{}] Team[{}]".format(player.current_health, player.max_health,
                                                                      player.current_mana, player.max_mana,
                                                                      player.armor, player.weapon.name, player.team))


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
    distance_y = abs(a[0] - b[0])
    if distance_x > distance_y:
        return distance_x
    else:
        return distance_y


def walk_to(begin_pos, end_pos):
    # tile = [x, y, total_cost, parent_tile]
    # makes sure the x and y coordinates are in shape [x, y]
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
                    log.append("Health[{}/{}] Armor[{}] Weapon[{}]".format(creature.current_health, creature.max_health, creature.armor, creature.weapon.name))
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
    roll = random.randint(0, creature_cap) + len(creature_list)
    if roll < creature_cap:
        patience = 10
        spawned = False
        goblins = 0
        zombies = 0
        for x in creature_list:
            if x.name == "goblin":
                goblins += 1
            elif x.name == "zombie":
                zombies += 1
        goblin_roll = random.randint(0, int(species_cap - goblins))
        zombie_roll = random.randint(0, int(species_cap - zombies))
        if goblin_roll > zombie_roll:
            creature_list.append(Goblin())
        else:
            creature_list.append(Zombie())
        creature = creature_list[-1]
        side = random.randint(1, 4)
        if side == 1:   # north
            while not spawned:
                x = random.randint(0, map_width-1)
                y = map_height-1
                if map_creatures[x, y] == '' and map_terrain[x, y] == '':
                    creature.x = x
                    creature.y = y
                    refresh_map_creatures()
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
                if map_creatures[x, y] == '' and map_terrain[x, y] == '':
                    creature.x = x
                    creature.y = y
                    refresh_map_creatures()
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
                if map_creatures[x, y] == '' and map_terrain[x, y] == '':
                    creature.x = x
                    creature.y = y
                    refresh_map_creatures()
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
                if map_creatures[x, y] == '' and map_terrain[x, y] == '':
                    creature.x = x
                    creature.y = y
                    refresh_map_creatures()
                    log.append("A {} has joined the battle from the west.\n".format(creature.name))
                    spawned = True
                patience -= 1
                if patience <= 0:
                    del creature_list[-1]
                    break


def player_turn():
    global log
    global input_char
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
    enemies = []
    for enemy in creature_list:
        if enemy.team != creature.team:
            enemies.append(enemy)
    distance = creature.sight_range
    for enemy in enemies:
        if get_distance(creature, enemy) < distance:   # if new enemy is closer than previous enemy
            distance = get_distance(creature, enemy)
            creature.target = enemy
    target = creature.target
    if target is not None and not target.dead:
        min_range = creature.weapon.min_range
        max_range = creature.weapon.max_range
        x_distance = target.x - creature.x
        y_distance = target.y - creature.y
        # checks if enemy is within max weapon range
        if abs(x_distance) <= max_range and abs(y_distance) <= max_range and (abs(x_distance) >= min_range or abs(y_distance) >= min_range):
            creature_attack(creature, target)
        else:
            if abs(x_distance) >= max_range or abs(y_distance) >= max_range:
                path = walk_to(creature, target)
                if path is not None:
                    next_pos = path[0]
                    creature.x = next_pos[0]
                    creature.y = next_pos[1]
            elif abs(x_distance) < min_range and abs(y_distance) < min_range:
                walk_away(creature, target)
            else:
                print("error in basic_turn")


def walk_away(creature, target):
    x_distance = target.x - creature.x
    y_distance = target.y - creature.y
    new_pos = [creature.x, creature.y]
    if x_distance < 0 and y_distance < 0:
        new_pos = [creature.x + 1, creature.y + 1]
    elif x_distance == 0 and y_distance < 0:
        new_pos = [creature.x, creature.y + 1]
    elif x_distance > 0 and y_distance < 0:
        new_pos = [creature.x - 1, creature.y + 1]
    elif x_distance < 0 and y_distance == 0:
        new_pos = [creature.x + 1, creature.y]
    elif x_distance > 0 and y_distance == 0:
        new_pos = [creature.x - 1, creature.y]
    elif x_distance < 0 and y_distance > 0:
        new_pos = [creature.x + 1, creature.y - 1]
    elif x_distance == 0 and y_distance > 0:
        new_pos = [creature.x, creature.y - 1]
    elif x_distance > 0 and y_distance > 0:
        new_pos = [creature.x - 1, creature.y - 1]
    if 0 <= new_pos[0] < map_width and 0 <= new_pos[1] < map_height:
        if map_creatures[new_pos[0], new_pos[1]] == '' and map_terrain[new_pos[0], new_pos[1]] == '':
            creature.x = new_pos[0]
            creature.y = new_pos[1]
            # *3
        else:   # tries to walk behind the creature
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
    else:   # tries to walk behind the creature
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
            log.append("for {}+{} damage.\n".format(damage_roll1, damage_roll2))
        else:
            damage_roll = random.randint(1, weapon.damage)
            log.append("for {} damage.\n".format(damage_roll))
        target.current_health -= damage_roll
        if target.current_health > 0:
            log.append("The {} has {} hit points left.\n".format(target.name, target.current_health))
        elif player is not None and target == player:
            on_player_dead()
        else:
            on_creature_dead(target)
    else:
        log.append("but misses.\n")


class Weapon:
    def __init__(self, weapon_name, min_range, max_range, damage):
        self.name = weapon_name
        self.min_range = min_range
        self.max_range = max_range
        self.damage = damage


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
        if map_width > map_height:  # allows them to see everything
            self.sight_range = map_width
        else:
            self.sight_range = map_height
        self.target = None
        self.dead = False
        self.speech = False
        self.team = team
        self.inventory = []
        self.statuses = []
        self.x = -1
        self.y = -1


class Player(BaseCreature):
    name = "player"
    symbol = 'O'

    def __init__(self, team=1):
        BaseCreature.__init__(self, team)
        self.max_health = 20
        self.current_health = self.max_health
        self.max_mana = 100
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
        self.speech = True
        spawn(self)

    def turn(self):
        player_turn()
        refresh_map_creatures()


class Goblin(BaseCreature):
    name = "goblin"
    symbol = 'g'

    def __init__(self, team=2):
        BaseCreature.__init__(self, team)
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
        # self.sight_range = 7
        self.speech = True
        spawn(self)

    def turn(self):
        basic_turn(self)
        refresh_map_creatures()


class Zombie(BaseCreature):
    name = "zombie"
    symbol = 'z'

    def __init__(self, team=0):
        BaseCreature.__init__(self, team)
        for x in range(4):
            self.max_health += random.randint(1, 8)
        self.current_health = self.max_health
        self.armor = 8 + random.randint(-1, 1)
        self.attack_modifier = random.randint(-2, 1)
        self.weapon = claws
        self.speed = 0.5
        self.actions_left = self.speed
        spawn(self)

    def turn(self):
        basic_turn(self)
        refresh_map_creatures()

# team 0 means evil and always attacks all other teams
# if adding new creature type, edit species_cap and spawn_new_enemies


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
map_ground = init_map_ground()  # creates empty ground map
creature_cap = (map_width * map_height) / 30    # sets ratio of creatures to map
species_cap = creature_cap / 1.7    # sets ratio of creatures to species
creature_list = []  # prepares list of creatures
map_creatures = []  # prepares map of creatures
refresh_map_creatures()     # initializes map of creatures
map_temp = init_map_empty()     # initializes empty overlay map

game_mode_chosen = False
while not game_mode_chosen:     # chooses game mode
    print("Do you want to (w)atch the AI battle, (p)lay yourself or (b)uild a map?")
    input_char = msvcrt.getch()
    try:
        game_mode = bytes.decode(input_char)
        if game_mode == 'w' or game_mode == 'p' or game_mode == 'b':
            game_mode_chosen = True
    except UnicodeDecodeError:
        for x in range(blank_lines):
            print('')
        print("Invalid input.")
# todo implement these modes

if game_mode == 'b':
    map_terrain = init_map_empty()
else:
    map_terrain = init_map_terrain()
    amount_of_zombies = random.randint(1, 6)
    for x in range(amount_of_zombies):
        creature_list.append(Zombie())
    amount_of_goblins = random.randint(1, 3)
    for x in range(amount_of_goblins):
        creature_list.append(Goblin())

input_char = '0'
turn_counter = 0
log = []

quit_game = False

# todo add spells
if game_mode == 'w':
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
    creature_list.append(Player())
    player_index = len(creature_list)-1
    player = creature_list[player_index]
    while not quit_game and not player.dead:  # 1 loop is 1 turn
        end_turn = False
        new_turn()
        turn_counter += 1
elif game_mode == 'b':
    print("Not implemented yet")
else:
    print("Error {}".format(game_mode))

show_map()
