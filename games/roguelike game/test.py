import numpy as np
import msvcrt
import random
import copy
import curses
from curses.textpad import Textbox


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
        log.append("Error: ", creature_type)
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
    global player_spawn_pos
    map_new = np.zeros([map_width, map_height], dtype=object)
    for x in range(map_width):
        for y in range(map_height):
            map_new[x][y] = EmptyTile()
    if not empty:
        if map_mode == 'b':  # creates walls of random length with holes in them at random positions
            wall_ratio = 90  # one wall per amount of tiles
            amount_of_walls = int((map_width * map_height) / wall_ratio)
            for x in range(amount_of_walls):
                horizontal = random.randint(0, 1)
                if horizontal == 1:
                    y = random.randint(0, map_height - 1)
                    length = random.randint(int(map_width * 0.5), int(map_width * 0.9 - 1))
                else:
                    x = random.randint(0, map_width - 1)
                    length = random.randint(int(map_height * 0.5), int(map_height * 0.9 - 1))
                patience = 10  # stops early if it can't find any free spots to place walls
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
        elif map_mode == 'd':   # creates a random dungeon
            room_width = 6  # including one wall
            room_height = 6
            dungeon_creatures = ["goblin", "zombie"]
            room_amount_x = int((map_width-1) / room_width)
            room_amount_y = int((map_height-1) / room_height)
            layout_map = np.zeros([room_amount_x, room_amount_y, 5], dtype=int)
            first_room = True
            for x in range(room_amount_x):
                for y in range(room_amount_y):  # creates new map tile: [room_type, northern exit, eastern exit]
                    if not first_room:
                        layout_map[x, y] = [random.randint(1, 2), False, False, False, False]
                    else:
                        layout_map[x, y] = [2, False, False, False, False]
                        first_room = False
            for x in range(map_width):
                for y in range(map_height):  # first, fills the map with walls
                    map_new[x, y] = Wall()
            rooms_list = []
            for y in range(room_amount_y):
                for x in range(room_amount_x):
                    if layout_map[x, y, 0] == 2:   # if it is a room
                        for x_room in range(room_width-1):
                            for y_room in range(room_height-1):  # empties the room leaving 1-layer SW wall
                                map_new[x * room_width + x_room+1, y * room_height + y_room+1] = EmptyTile()
                        rooms_list.append([x, y])
                        if y > 0:
                            south_exit = layout_map[x, y-1, 1]
                        else:
                            south_exit = False
                        if x > 0:
                            west_exit = layout_map[x-1, y, 2]
                        else:
                            west_exit = False
                        if south_exit and west_exit:
                            amount_of_exits = random.randint(0, 2)
                        elif south_exit or west_exit:
                            amount_of_exits = random.randint(0, 2)
                        else:
                            amount_of_exits = random.randint(1, 2)
                        previous_exits = []
                        for amount in range(amount_of_exits):
                            unique_exit = False
                            while not unique_exit:
                                exit_side = random.randint(1, 2)    # north or east
                                unique_exit = True
                                for previous_exit in previous_exits:
                                    if previous_exit == exit_side:
                                        unique_exit = False
                                        break
                            previous_exits.append(exit_side)
                            if (exit_side == 1 or (exit_side == 2 and x == room_amount_x-1)) and y != room_amount_y-1:  # north
                                layout_map[x, y, 1] = True
                                map_new[x*room_width+int(room_width/2), (y+1)*room_height] = Door()
                            elif (exit_side == 2 or (exit_side == 1 and y == room_amount_y-1)) and x != room_amount_x-1:    # east
                                layout_map[x, y, 2] = True
                                map_new[(x+1)*room_width, y*room_height+int(room_height/2)] = Door()
                    elif layout_map[x, y, 0] == 1:  # if it's a corridor
                        map_new[x*room_width+int(room_width/2), y*room_height+int(room_height/2)] = EmptyTile()
                        if y > 0:
                            south_exit = layout_map[x, y-1, 1]
                        else:
                            south_exit = False
                        if x > 0:
                            west_exit = layout_map[x-1, y, 2]
                        else:
                            west_exit = False
                        if south_exit:  # makes southern corridor
                            for z in range(int(room_height / 2)):
                                map_new[x * room_width + int(room_width / 2), y * room_height + z] = EmptyTile()
                        if west_exit:   # makes western corridor
                            for z in range(int(room_width / 2)):
                                map_new[x * room_width + z, y * room_height + int(room_height / 2)] = EmptyTile()
                        if south_exit and west_exit:
                            amount_of_exits = random.randint(0, 2)
                        elif south_exit or west_exit:
                            amount_of_exits = random.randint(1, 2)
                        else:
                            amount_of_exits = 2
                        previous_exits = []
                        for amount in range(amount_of_exits):
                            unique_exit = False
                            while not unique_exit:
                                exit_side = random.randint(1, 2)    # north or east
                                unique_exit = True
                                for previous_exit in previous_exits:
                                    if previous_exit == exit_side:
                                        unique_exit = False
                                        break
                            previous_exits.append(exit_side)
                            if (exit_side == 1 or (exit_side == 2 and x == room_amount_x-1)) and y != room_amount_y-1 and layout_map[x, y, 1] != True:  # north
                                layout_map[x, y, 1] = True
                                layout_map[x, y+1, 3] = True
                                for z in range(int(room_height/2)):
                                    map_new[x*room_width + int(room_width/2), (y+1)*room_height-z] = EmptyTile()
                            elif (exit_side == 2 or (exit_side == 1 and y == room_amount_y-1)) and x != room_amount_x-1 and layout_map[x, y, 2] != True:  # east
                                layout_map[x, y, 2] = True
                                layout_map[x+1, y, 4] = True
                                for z in range(int(room_width/2)):
                                    map_new[(x+1)*room_width-z, y*room_height+int(room_height/2)] = EmptyTile()
                            # makes sure corridors can't end in dead-ends
                            elif (x == room_amount_x-1 or y == room_amount_y-1) and not south_exit and not west_exit:
                                if exit_side == 1 or y == room_amount_y-1:  # makes corridor go west
                                    layout_map[x-1, y, 2] = True
                                    for z in range(room_width):
                                        map_new[x*room_width+int(room_width/2)-z, y*room_height+int(room_height/2)] = EmptyTile()
                                elif exit_side == 2 or x == room_amount_x-1:    # makes corridor go south
                                    layout_map[x, y-1, 1] = True
                                    for z in range(room_height):
                                        map_new[x*room_width+int(room_width/2), y*room_height+int(room_height/2)-z] = EmptyTile()
                            elif x == room_amount_x-1 and y == room_amount_y-1:
                                layout_map[x - 1, y, 2] = True  # makes corridor go west
                                for z in range(room_width):
                                    map_new[x*room_width+int(room_width/2)-z, y*room_height + int(room_height/2)] = EmptyTile()
                                layout_map[x, y - 1, 1] = True  # makes corridor go south
                                for z in range(room_height):
                                    map_new[x*room_width+int(room_width/2), y*room_height+int(room_height/2)-z] = EmptyTile()
            for x in range(room_amount_x):
                for y in range(room_amount_y):  # places down doors
                    if layout_map[x, y, 0] == 2:
                        if layout_map[x, y, 1]:     # northern door
                            map_new[(x*room_width+int(room_width/2)), (y+1)*room_height] = Door()
                        if layout_map[x, y, 2]:     # eastern door
                            map_new[(x+1)*room_width, y*room_height+int(room_height/2)] = Door()
                        if layout_map[x, y, 3]:     # southern door
                            map_new[(x*room_width+int(room_width/2)), y*room_height] = Door()
                        if layout_map[x, y, 4]:     # western door
                            map_new[x*room_width, y*room_height+int(room_height/2)] = Door()
            if game_mode == 'p':    # reserves a room as spawn point
                start_room_index = random.randint(0, len(rooms_list)-1)
                start_room = rooms_list[start_room_index]   # always the same position ERROR todo, check player_dead
                player_spawn_pos[0] = random.randint(1, room_width-1) + start_room[0] * room_width
                player_spawn_pos[1] = random.randint(1, room_height-1) + start_room[1] * room_height
                rooms_list.remove(start_room)
            for room in rooms_list:
                creature_type = random.randint(0, len(dungeon_creatures) - 1)
                creature_type = dungeon_creatures[creature_type]
                creature_amount = random.randint(0, int(((room_height - 1) * (room_width - 1)) / 6))
                for amount in range(creature_amount):  # spawns creatures in rooms
                    creature = create_creature_of_type(creature_type)
                    spawned = False
                    while not spawned:
                        x_pos = random.randint(1, room_width-1) + room[0] * room_width
                        y_pos = random.randint(1, room_height-1) + room[1] * room_height
                        if map_creatures[x_pos, y_pos] == '' and not map_new[x_pos, y_pos].blocks_movement:
                            creature.x = x_pos
                            creature.y = y_pos
                            spawned = True
                            refresh_map_creatures()
    return map_new


def refresh_map_creatures():
    global map_creatures
    map_creatures = np.zeros([map_width, map_height], dtype=str)
    for creature in creature_list:
        map_creatures[creature.x, creature.y] = creature.symbol


def update_map():
    global map_window
    global game_mode
    global map_temp
    global map_creatures
    global map_terrain
    global map_ground
    if game_mode != 'b':
        refresh_map_creatures()
    # flips the maps around y so y+ is up
    map_temp = np.flip(map_temp, 1)
    map_creatures = np.flip(map_creatures, 1)
    map_terrain = np.flip(map_terrain, 1)
    map_ground = np.flip(map_ground, 1)
    for x in range(map_width):
        for y in range(map_height):
            attribute = curses.A_NORMAL
            if map_terrain[x, y].seen and not map_terrain[x, y].visible:
                attribute = curses.A_BLINK  # darkens the map if currently not visible
            if map_temp[x, y] != '':  # top layer is overlay
                map_window.addstr(y, (x * 3) + 1, map_temp[x, y])
            elif map_creatures[x, y] != '' and (
                    map_terrain[x, y].visible or game_mode != 'p'):  # next layer is creatures
                for creature in creature_list:
                    if creature.x == x and creature.y == (map_height-y-1):  # finds creature, y is flipped
                        map_window.addstr(y, x*3 + 1, creature.symbol, curses.color_pair(creature.color))
                        break
            elif map_terrain[x, y].symbol != '' and (
                    map_terrain[x, y].seen or game_mode != 'p'):  # bottom layer is terrain
                map_window.addstr(y, (x * 3) + 1, map_terrain[x, y].symbol, attribute)
                if attribute != curses.A_NORMAL:    # changes attribute of whole tile
                    map_window.addstr(y, (x * 3), ' ', attribute)
                    map_window.addstr(y, (x * 3) + 2, ' ', attribute)
            elif not map_terrain[x, y].seen and game_mode == 'p':
                map_window.addstr(y, x*3, '███', curses.A_REVERSE)
            else:
                map_window.addstr(y, x * 3 + 1, map_ground[x, y], attribute)
                # changes attribute of whole tile
                map_window.addstr(y, (x * 3), ' ', attribute)
                map_window.addstr(y, (x * 3) + 2, ' ', attribute)
    # flips the map back for later editing
    map_temp = np.flip(map_temp, 1)
    map_creatures = np.flip(map_creatures, 1)
    map_terrain = np.flip(map_terrain, 1)
    map_ground = np.flip(map_ground, 1)


def show_screen():
    global screen
    global map_window
    global console_window
    global misc_window
    global log_window
    global console_log
    global misc_log
    global log
    global previous_turn
    global main_window_offset_x
    global main_window_offset_y
    screen.clear()
    map_window.clear()
    console_window.clear()
    misc_window.clear()
    log_window.clear()
    for x in range(MAIN_WINDOW_WIDTH + SIDE_WINDOW_WIDTH + 3):
        screen.addstr(0, x, '═')
    for x in range(MAIN_WINDOW_WIDTH + SIDE_WINDOW_WIDTH + 3):
        screen.addstr(MAIN_WINDOW_HEIGHT + 1, x, '═')
    for x in range(MAIN_WINDOW_WIDTH + SIDE_WINDOW_WIDTH + 3):
        screen.addstr(MAIN_WINDOW_HEIGHT + SIDE_WINDOW_HEIGHT + 2, x, '═')
    for y in range(MAIN_WINDOW_HEIGHT + SIDE_WINDOW_HEIGHT + 3):
        screen.addstr(y, 0, '║')
    for y in range(MAIN_WINDOW_HEIGHT + SIDE_WINDOW_HEIGHT + 3):
        screen.addstr(y, MAIN_WINDOW_WIDTH + 1, '║')
    for y in range(MAIN_WINDOW_HEIGHT + SIDE_WINDOW_HEIGHT + 3):
        screen.addstr(y, MAIN_WINDOW_WIDTH + SIDE_WINDOW_WIDTH + 2, '║')
    screen.addstr(0, 0, '╔')
    screen.addstr(0, MAIN_WINDOW_WIDTH + 1, '╦')
    screen.addstr(0, MAIN_WINDOW_WIDTH + SIDE_WINDOW_WIDTH + 2, '╗')
    screen.addstr(MAIN_WINDOW_HEIGHT + 1, 0, '╠')
    screen.addstr(MAIN_WINDOW_HEIGHT + 1, MAIN_WINDOW_WIDTH + 1, '╬')
    screen.addstr(MAIN_WINDOW_HEIGHT + 1, MAIN_WINDOW_WIDTH + SIDE_WINDOW_WIDTH + 2, '╣')
    screen.addstr(MAIN_WINDOW_HEIGHT + SIDE_WINDOW_HEIGHT + 2, 0, '╚')
    screen.addstr(MAIN_WINDOW_HEIGHT + SIDE_WINDOW_HEIGHT + 2, MAIN_WINDOW_WIDTH + 1, '╩')
    screen.addstr(MAIN_WINDOW_HEIGHT + SIDE_WINDOW_HEIGHT + 2, MAIN_WINDOW_WIDTH + SIDE_WINDOW_WIDTH + 2, '╝')

    line_number = 0
    for line in console_log:
        console_window.addstr(line_number, 0, str(line))
        line_number += 1

    if game_started and game_mode != 'b' and previous_turn < turn_counter:
        string = "Turn: {} ".format(turn_counter)
        amount = MAIN_WINDOW_WIDTH - len(string)
        string = string + ('-' * amount)
        log.append(string)
        previous_turn = turn_counter
    log.reverse()  # reverses log so latest message is on top
    line_number = 0
    offset = 0
    for line in log:
        if line_number + offset + int(
                (len(line) - 2) / MAIN_WINDOW_WIDTH) + 1 < LOG_LENGTH:  # checks if still room on log
            log_window.addstr(line_number + offset, 0, str(line))  # then prints the line
        else:  # otherwise cuts off old messages
            log = log[:line_number]
        if len(line) > MAIN_WINDOW_WIDTH:
            offset += int((len(line) - 2) / MAIN_WINDOW_WIDTH)  # makes sure long message don't overlap
        line_number += 1
    log.reverse()  # reverses log again so it can be edited normally

    line_number = 0
    offset = 0
    for line in misc_log:
        misc_window.addstr(line_number + offset, 0, str(line))
        if len(line) > SIDE_WINDOW_WIDTH:
            offset += int((len(line) - 2) / SIDE_WINDOW_WIDTH)  # makes sure long message don't overlap
        line_number += 1
    if line_number == 0 and game_mode == 'p' and game_started:  # if nothing on misc screen
        string = (
            "\nHealth[{}/{}]\nMana[{}/{}]\nArmor[{}]\nWeapon[{}]\nTeam[{}]\nKills[{}]\n".format(player.current_health,
                                                                                                player.max_health,
                                                                                                player.current_mana,
                                                                                                player.max_mana,
                                                                                                player.armor,
                                                                                                player.weapon.name,
                                                                                                player.team,
                                                                                                player.kills))
        string = string + "Status["
        amount = len(player.statuses)
        if amount > 0:
            for status in player.statuses:
                if amount <= 1:
                    string = string + "{}".format(status)
                else:
                    string = string + "{}, ".format(status)
                amount -= 1
        string = string + "]"
        misc_window.addstr(line_number, 0, string)

    if game_started:
        update_map()
    if game_started:
        if game_mode == 'p':
            position = [player.x, player.y]
        elif game_mode == 'b' or cursor_mode:
            position = [cursor[0], cursor[1]]
        else:
            position = [middle[0], middle[1]]
        # enabling scrolling on x-axis
        if position[0] * 3 < MAIN_WINDOW_WIDTH / 2:  # west border lock
            main_window_offset_x = 0
        elif position[0] * 3 + 1 > (map_width * 3 - MAIN_WINDOW_WIDTH / 2):  # east border lock
            main_window_offset_x = map_width * 3 - MAIN_WINDOW_WIDTH
        else:  # relative view
            main_window_offset_x = int((position[0] * 3) - MAIN_WINDOW_WIDTH / 2) + 3
            if main_window_offset_x % 3 != 0:
                main_window_offset_x -= main_window_offset_x % 3
        # enables scrolling on y-axis
        if position[1] > map_height - (MAIN_WINDOW_HEIGHT / 2):  # north border lock
            main_window_offset_y = 0
        elif position[1] < MAIN_WINDOW_HEIGHT / 2 and map_height > MAIN_WINDOW_HEIGHT:  # south border lock
            main_window_offset_y = map_height - MAIN_WINDOW_HEIGHT
        elif map_height > MAIN_WINDOW_HEIGHT:  # relative view
            main_window_offset_y = map_height - int(position[1] + MAIN_WINDOW_HEIGHT / 2)
            if MAIN_WINDOW_HEIGHT % 2 != 0:
                main_window_offset_y -= 1
    screen.refresh()
    map_window.refresh(main_window_offset_y, main_window_offset_x, 1, 1, MAIN_WINDOW_HEIGHT, MAIN_WINDOW_WIDTH)
    console_window.refresh(0, 0, MAIN_WINDOW_HEIGHT + 2, MAIN_WINDOW_WIDTH + 2,
                           SIDE_WINDOW_HEIGHT + MAIN_WINDOW_HEIGHT + 1, SIDE_WINDOW_WIDTH + MAIN_WINDOW_WIDTH + 2)
    misc_window.refresh(0, 0, 1, MAIN_WINDOW_WIDTH + 2, MAIN_WINDOW_HEIGHT, MAIN_WINDOW_WIDTH + SIDE_WINDOW_WIDTH + 2)
    log_window.refresh(log_window_offset, 0, MAIN_WINDOW_HEIGHT + 2, 1, MAIN_WINDOW_HEIGHT + SIDE_WINDOW_HEIGHT + 1,
                       MAIN_WINDOW_WIDTH)
    console_log = []
    misc_log = []


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
        open_list.sort(key=sort_tile_cost)  # sorts available tiles by cost
        current_tile = open_list[0]  # takes the unexplored tile with the best chance of going to the goal
        if current_tile[:2] == goal:  # checks if you've found the goal
            break
        for neighbour in neighbours:  # selects tiles next to current tile
            new_tile = copy.deepcopy(current_tile)  # makes a copy so current_tile doesn't get edited
            new_tile[0] += neighbour[0]
            new_tile[1] += neighbour[1]
            # checks if new tile is blocked by map size
            if 0 <= new_tile[0] < map_width and 0 <= new_tile[1] < map_height:
                # checks if new tile is blocked by terrain
                if new_tile[:2] == goal or map_terrain[new_tile[0], new_tile[1]].blocks_movement == False:
                    # adds cost to the new tile: previous tile's cost and new/updated distance cost
                    new_tile[2] = (current_tile[2] - get_distance(current_tile, goal) + get_distance(new_tile, goal))
                    if map_creatures[new_tile[0], new_tile[1]] != '':
                        new_tile[2] += 2    # adds weight because a creature blocks the path
                    new_tile[2] += map_terrain[new_tile[0], new_tile[1]].movement_cost   # adds movement cost of terrain
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
                    if not in_open and not in_closed:  # if it's a new tile add it to the open list
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
                if len(current_tile[3]) == 4:  # checks if the tile has a parent tile
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
                elif map_creatures[new_pos[0], new_pos[1]] != '' and player.weapon.min_range <= 1 and player.weapon.max_range >= 1:
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
    global misc_log
    global cursor
    if location == 0:
        cursor = [player.x, player.y]
    else:
        cursor = [int(location[0]), int(location[1])]
    command = ''
    while command != 'x':
        map_temp = init_map_empty()
        map_temp[cursor[0], cursor[1]] = '▢'
        creature = map_creatures[cursor[0], cursor[1]]
        misc_log.append("Position: ({}, {})".format(cursor[0], cursor[1]))
        if creature != '':
            for creature in creature_list:
                if creature.x == cursor[0] and creature.y == cursor[1]:
                    misc_log.append("You see a {} from team {}\n".format(creature.name, creature.team))
                    stats = ''
                    stats = stats + (
                        "Health[{}/{}]\nArmor[{}]\nWeapon[{}]\nAlignment[{}]\n".format(creature.current_health,
                                                                                       creature.max_health,
                                                                                       creature.armor,
                                                                                       creature.weapon.name,
                                                                                       creature.alignment))
                    if len(creature.statuses) > 0:
                        stats = stats + "Status["
                        amount = len(creature.statuses)
                        for status in creature.statuses:
                            if amount <= 1:
                                stats = stats + ("{}".format(status))
                            else:
                                stats = stats + ("{}, ".format(status))
                            amount -= 1
                        stats = stats + "]\n"
                    else:
                        stats = stats + "\n"
                    misc_log.append(stats)
                    break
        console_log.append("Move (numpad) or e(x)it:")
        show_screen()
        command = screen.getkey()
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
                break
            else:
                log.append("Invalid input.\n")
    map_temp = init_map_empty()


def open_inventory():
    command = ''
    while command != 'x':
        try:
            if int(command) > 0:
                if isinstance(player.inventory[int(command) - 1], Weapon):
                    player.weapon = player.inventory[int(command) - 1]
                    misc_log.append("You have equipped the {}.\n".format(player.weapon.name))
        except (ValueError, IndexError):
            misc_log.append("")
        number = 0
        for item in player.inventory:
            number += 1
            string = ("{}. ".format(number))
            if isinstance(item, Weapon):
                string = string + (
                    "Weapon[{}] Range[{}-{}] Damage[{}]\n".format(item.name, item.min_range, item.max_range,
                                                                  item.damage))
            else:
                string = string + ("Item[{}]\n".format(item.name))
            misc_log.append((string))
        console_log.append("Input the number of the item you want to equip/use or e(x)it:")
        show_screen()
        command = screen.getkey()


def creature_in_range(action):
    global player
    global misc_log
    actual_target = None
    max_range = action.max_range
    min_range = action.min_range
    targets = []
    for target in creature_list:  # checks if creature is (inside of max range) and (not inside of min range)
        x_distance = target.x - player.x
        y_distance = target.y - player.y
        if abs(x_distance) <= max_range and abs(y_distance) <= max_range and (
                abs(x_distance) >= min_range or abs(y_distance) >= min_range):
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
        misc_log.append("Choose your target: \n")
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
            string = "{}. {} ".format(number, target.name)
            if north:
                distance = target.y - player.y
                if distance == 1:
                    string = string + ("{} tile to the north".format(distance))
                else:
                    string = string + ("{} tiles to the north".format(distance))
            elif south:
                distance = player.y - target.y
                if distance == 1:
                    string = string + ("{} tile to the south".format(distance))
                else:
                    string = string + ("{} tiles to the south".format(distance))
            if (north or south) and (east or west):
                string = string + (" and ")
            if east:
                distance = target.x - player.x
                if distance == 1:
                    string = string + ("{} tile to the east".format(distance))
                else:
                    string = string + ("{} tiles to the east".format(distance))
            elif west:
                distance = player.x - target.x
                if distance == 1:
                    string = string + ("{} tile to the west".format(distance))
                else:
                    string = string + ("{} tiles to the west".format(distance))
            string = string + ". \n"
            misc_log.append(string)
        console_log.append("Input the number of the creature you want to target or e(x)it:")
        show_screen()
        chosen_target = screen.getkey()
        try:
            if int(chosen_target) <= len(targets):
                actual_target = targets[int(chosen_target) - 1]
            else:
                log.append("Invalid input.\n")
        except ValueError:
            if chosen_target == 'x':
                print()
            else:
                log.append("Invalid input.\n")
    else:
        log.append("There are no possible targets nearby.\n")
    return actual_target


def tiles_that_are_attackable(creature):
    directions = [[-1, 1], [1, 1], [1, -1], [-1, -1]]
    seen_tiles = [[creature.x, creature.y]]
    for direction in directions:
        for change_dir_amount in range(creature.sight_range):  # decides how often to switch up direction
            counter = 0
            current_tile = [creature.x, creature.y]
            for x in range(creature.sight_range):  # looks until it hits the end of vision
                current_tile[0] += direction[0]
                counter += 1
                if counter >= change_dir_amount + 1:
                    counter = 0
                    current_tile[1] += direction[1]
                if 0 <= current_tile[0] < map_width and 0 <= current_tile[1] < map_height:
                    seen_tiles.append([current_tile[0], current_tile[1]])
                    if map_terrain[current_tile[0], current_tile[1]].blocks_sight or map_terrain[
                        current_tile[0], current_tile[1]].blocks_projectiles:
                        break
            counter = 0
            current_tile = [creature.x, creature.y]
            for x in range(creature.sight_range):  # looks until it hits the end of vision going the other way
                current_tile[0] += direction[0]
                current_tile[1] += direction[1]
                counter += 1
                if counter >= change_dir_amount + 1:
                    counter = 0
                    current_tile[1] -= direction[1]
                if 0 <= current_tile[0] < map_width and 0 <= current_tile[1] < map_height:
                    seen_tiles.append([current_tile[0], current_tile[1]])
                    if map_terrain[current_tile[0], current_tile[1]].blocks_sight or map_terrain[
                        current_tile[0], current_tile[1]].blocks_projectiles:
                        break
            counter = 0
            current_tile = [creature.x, creature.y]
            for x in range(creature.sight_range):  # looks until it hits the end of vision for the second half
                current_tile[1] += direction[1]
                counter += 1
                if counter >= change_dir_amount + 1:
                    counter = 0
                    current_tile[0] += direction[0]
                if 0 <= current_tile[0] < map_width and 0 <= current_tile[1] < map_height:
                    seen_tiles.append([current_tile[0], current_tile[1]])
                    if map_terrain[current_tile[0], current_tile[1]].blocks_sight or map_terrain[
                        current_tile[0], current_tile[1]].blocks_projectiles:
                        break
            counter = 0
            current_tile = [creature.x, creature.y]
            for x in range(creature.sight_range):  # looks until it hits the end of vision going the other way
                current_tile[1] += direction[1]
                current_tile[0] += direction[0]
                counter += 1
                if counter >= change_dir_amount + 1:
                    counter = 0
                    current_tile[0] -= direction[0]
                if 0 <= current_tile[0] < map_width and 0 <= current_tile[1] < map_height:
                    seen_tiles.append([current_tile[0], current_tile[1]])
                    if map_terrain[current_tile[0], current_tile[1]].blocks_sight or map_terrain[
                        current_tile[0], current_tile[1]].blocks_projectiles:
                        break
    return seen_tiles


def tiles_in_sight(creature):
    directions = [[-1, 1], [1, 1], [1, -1], [-1, -1]]
    seen_tiles = [[creature.x, creature.y]]
    for direction in directions:
        for change_dir_amount in range(creature.sight_range):  # decides how often to switch up direction
            counter = 0
            current_tile = [creature.x, creature.y]
            for x in range(creature.sight_range):  # looks until it hits the end of vision
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
            for x in range(creature.sight_range):  # looks until it hits the end of vision going the other way
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
            for x in range(creature.sight_range):  # looks until it hits the end of vision for the second half
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
            for x in range(creature.sight_range):  # looks until it hits the end of vision going the other way
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
    global end_turn
    weapon = player.weapon
    if target is None:
        target = creature_in_range(weapon)
    if target is not None:  # if a target has been chosen
        end_turn = True
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
    for status in creature.statuses:  # if creature is infected, spawn zombie at creature's location
        if status == "infected":
            creature_list.append(Zombie())
            zombie = creature_list[-1]
            log.append("A {} has risen from the {}'s corpse.\n".format(zombie.name, creature.name))
            zombie.x = creature.x
            zombie.y = creature.y
            break
    index = 0
    for x in creature_list:  # finds and deletes dead creature in creature_list
        if x == creature:
            del creature_list[index]
            break
        index += 1


def on_player_dead():
    global player
    global input_char
    global game_mode
    global quit_game
    player.dead = True
    log.append("You have died.\n")
    for status in player.statuses:  # if creature is infected, spawn zombie at creature's location
        if status == "infected":
            creature_list.append(Zombie())
            zombie = creature_list[-1]
            log.append("A {} has risen from your corpse.\n".format(zombie.name))
            zombie.x = player.x
            zombie.y = player.y
            break
    del creature_list[player_index]
    decision_made = False
    while not decision_made:
        console_log.append("Do you want to continue watching the fight? (y)es or (n)o")
        show_screen()
        input_char = screen.getkey()
        if input_char == 'y':
            for x in range(map_width):
                for y in range(map_height):
                    map_terrain[x, y].visible = True
            game_mode = 'w'
            decision_made = True
        elif input_char == 'n':
            quit_game = True
            decision_made = True
        else:
            console_log.append("Invalid input.")


def new_turn():
    for creature in creature_list:
        while creature.actions_left >= 1:
            creature.turn()
            creature.actions_left -= 1
    for creature in creature_list:  # refreshes all actions left for each creature
        creature.actions_left += creature.speed
    if map_mode == 'b':
        spawn_new_enemies()


def spawn_new_enemies():
    global creature_cap
    global species_cap
    global map_creatures
    roll = random.randint(0, creature_cap) + len(creature_list)
    if roll < creature_cap:
        npc_list = []
        for x in npc_types:
            npc_list.append([0, 0])  # amount and roll for every npc type
        for creature in creature_list:  # gets existing amount of each npc type
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
        if side == 1:  # north
            while not spawned:
                x = random.randint(0, map_width - 1)
                y = map_height - 1
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
        elif side == 2:  # east
            while not spawned:
                x = map_width - 1
                y = random.randint(0, map_height - 1)
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
        elif side == 3:  # south
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
        else:  # west
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
    global input_char
    visible_tiles = tiles_in_sight(player)
    update_visible_tiles(visible_tiles)
    while not end_turn:
        console_log.append("(a)ttack, loo(k), (i)nventory, move (numpad) or (q)uit:")
        show_screen()
        input_char = screen.getkey()
        handle_input(input_char)
    if player.current_mana < player.max_mana:
        player.current_mana += 1
    refresh_map_creatures()


def spawn(creature):
    global creature_list
    global map_creatures
    spawned = False
    patience = 10
    while not spawned:
        x = random.randint(0, map_width - 1)
        y = random.randint(0, map_height - 1)
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
    all_enemies = []  # gets all enemies on the field
    if creature.alignment == "evil":
        for enemy in creature_list:  # attacks all other teams
            if enemy.team != creature.team:
                all_enemies.append(enemy)
    elif creature.alignment == "good":
        for enemy in creature_list:  # attacks all evil characters
            if enemy.alignment == "evil":
                all_enemies.append(enemy)
    elif creature.alignment == "neutral":
        log.append("need to implement this alignment behaviour")
    else:
        log.apppend("error in creature alignment:", creature.alignment)
    visible_tiles = tiles_in_sight(creature)
    distance = creature.sight_range
    for enemy in all_enemies:
        if get_distance(creature, enemy) < distance:  # if new enemy is closer than previous enemy
            for tile in visible_tiles:  # checks if closer enemy is visible
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
            if target.x == tile[0] and target.y == tile[1]:  # if enemy is on a targetable tile
                attackable = True
                break
        # checks if enemy is within weapon range and not blocked by walls
        if attackable and abs(x_distance) <= max_range and abs(y_distance) <= max_range and (
                abs(x_distance) >= min_range or abs(y_distance) >= min_range):
            creature_attack(creature, target)
        else:
            if abs(x_distance) > max_range or abs(y_distance) > max_range or not attackable:
                path = walk_to(creature, target)
                if path is not None:
                    next_pos = path[0]
                    if map_creatures[next_pos[0], next_pos[1]] == '':
                        creature.x = next_pos[0]
                        creature.y = next_pos[1]
                    elif not show_only_attacks_on_player:
                        log.append("The {} waits for an opening.".format(creature.name))
            elif abs(x_distance) < min_range and abs(y_distance) < min_range:
                walk_away(creature, target)
            else:
                log.append("error in basic_turn")
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
    if blocked:  # tries to sidestep backwards
        new_pos = [creature.x, creature.y]
        for directions in side_dirs:
            new_pos[0] += directions[0]
            new_pos[1] += directions[1]
            if 0 <= new_pos[0] < map_width and 0 <= new_pos[1] < map_height and map_creatures[
                new_pos[0], new_pos[1]] == '' and map_terrain[new_pos[0], new_pos[1]].blocks_movement == False:
                creature.x = new_pos[0]
                creature.y = new_pos[1]
                blocked = False
                break
            else:  # gets original position back
                new_pos[0] -= directions[0]
                new_pos[1] -= directions[1]
        if blocked:  # tries to walk behind the creature
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
    string = ''
    attack_roll = random.randint(1, 20)
    if target == player or not show_only_attacks_on_player:  # shows only attacks targetting player
        if creature.attack_modifier > 0:
            string = string + (
                "The {} rolls {}+{} to attack the {} ".format(creature.name, attack_roll, creature.attack_modifier,
                                                              target.name))
        elif creature.attack_modifier < 0:
            string = string + (
                "The {} rolls {}{} to attack the {} ".format(creature.name, attack_roll, creature.attack_modifier,
                                                             target.name))
        else:
            string = string + ("The {} rolls {} to attack the {} ".format(creature.name, attack_roll, target.name))
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
            if target == player or not show_only_attacks_on_player:  # shows only attacks targetting player
                string = string + ("for {}+{} damage.\n".format(damage_roll1, damage_roll2))
        else:
            damage_roll = random.randint(1, weapon.damage)
            if target == player or not show_only_attacks_on_player:  # shows only attacks targetting player
                string = string + ("for {} damage.\n".format(damage_roll))
        target.current_health -= damage_roll
        if target.current_health > 0 and (target == player or not show_only_attacks_on_player):
            string = string + ("The {} has {} hit points left.\n".format(target.name, target.current_health))
        elif player is not None and target == player:
            creature.kills += 1
            on_player_dead()
        else:
            creature.kills += 1
            on_creature_dead(target)
    elif target == player or not show_only_attacks_on_player:
        string = string + "but misses.\n"
        log.append(string)


def get_input(string):
    global log
    log.append(string)
    console_log.append("Press Ctrl+G to submit.\n")
    show_screen()
    box = Textbox(INPUT_LINE)
    box.edit()
    input_string = box.gather()
    INPUT_LINE.clear()
    input_string = input_string[:-2]
    log = []
    return input_string


def build_mode():
    global map_temp
    global console_log
    global quit_game
    global cursor
    cursor = [int(map_width / 2), int(map_height / 2)]
    command = ''
    console_log = []
    while command != 'q':
        map_temp = init_map_empty()
        map_temp[cursor[0], cursor[1]] = '▢'
        console_log.append("Move (numpad), (p)lace/(r)emove wall, (s)ave map or (q)uit:")
        misc_log.append("Position: ({}, {})".format(cursor[0], cursor[1]))
        misc_log.append("Current tile: {}".format(map_terrain[cursor[0], cursor[1]].name))
        show_screen()
        command = screen.getkey()
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
    map_temp = init_map_empty()


def save_map():
    global console_log
    map_name = get_input("What do you want to name the map (without .txt): ") + ".txt"
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
        console_log = []
        while not finished:
            log.append("Input how you want each creature to enter the map from the directions: north, east, south, "
                       "west. Type 'y' to allow the creature to enter from that direction or 'n' to forbid it. (e.g. "
                       "'yyny')")
            settings = get_input("How do you want a {} to be able to enter the map? ".format(creature))
            if len(settings) == 4:
                for char in settings:
                    if char == 'y' or char == 'n':
                        chars += 1
                        file.write(char)
                    else:
                        console_log = []
                        console_log.append("Invalid input.\n")
                        break
                if chars == 4:
                    finished = True
                    file.write("\n")
            else:
                console_log = []
                console_log.append("Invalid input.\n")
    file.close()


def load_map():
    global map_width
    global map_height
    global map_terrain
    global loaded_map
    global npc_spawn_directions
    global console_log
    console_log = []
    while not loaded_map:
        map_name = get_input("Input the name of the map you want to load (without .txt) or type \"exit\" to go back.\n")
        map_name = map_name + ".txt"
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
                            console_log = []
                            console_log.append("Error, unknown tile:", lines[y][x])
                lines = lines[map_height:]
                for x in range(len(npc_spawn_directions)):
                    npc_spawn_directions[x] = lines[x][:4]
                lines = lines[len(npc_spawn_directions):]
            except FileNotFoundError:
                console_log = []
                console_log.append(
                    "No file called {} found. Make sure it's in the same directory as this game and that it's spelled correctly.".format(
                        map_name))
        else:
            break


def at_start_of_game():
    global loaded_map
    global input_char
    global console_log
    while not loaded_map:  # makes sure a map will be created
        console_log.append("Do you want to load a map from your pc?\n(y)es or (n)o")
        show_screen()
        input_char = screen.getkey()
        if input_char == 'y':
            load_map()
        elif input_char == 'n':
            loaded_map = False
            init_new_map()
            break
        else:
            console_log = []
            console_log.append("Invalid input.\n")
    choose_game_mode()


def init_new_map():
    global map_width
    global map_height
    global console_log
    map_size_chosen = False
    console_log = []
    while not map_size_chosen:
        try:
            map_width = int(get_input("Input the number of tiles you want the map width to be: "))
            map_height = int(get_input("Input the number of tiles you want the map height to be: "))
            if map_width < 1 or map_height < 1:
                console_log = []
                console_log.append("Map length can't be 0.")
            else:
                map_size_chosen = True
        except ValueError:
            console_log = []
            console_log.append("Invalid input.")


def choose_game_mode():
    global game_mode
    global console_log
    game_mode_chosen = False
    console_log = []
    while not game_mode_chosen:  # chooses game mode
        console_log.append("Do you want to (w)atch the AI battle, (p)lay yourself or (b)uild a map?")
        show_screen()
        game_mode = screen.getkey()
        if game_mode == 'w' or game_mode == 'p' or game_mode == 'b':
            game_mode_chosen = True
        else:
            console_log = []
            console_log.append("Invalid input.")


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
        self.movement_cost = 1


class EmptyTile(TerrainTile):
    def __init__(self):
        TerrainTile.__init__(self)
        self.symbol = ''
        self.name = "empty"


class Wall(TerrainTile):
    def __init__(self):
        TerrainTile.__init__(self)
        self.symbol = '#'
        self.name = "wall"
        self.blocks_movement = True
        self.blocks_sight = True
        self.blocks_projectiles = True


class Door(TerrainTile):
    def __init__(self):
        TerrainTile.__init__(self)
        self.symbol = '▯'
        self.name = "door"
        self.blocks_sight = True
        self.blocks_projectiles = True


class BaseCreature:
    def __init__(self, team, random_spawn):
        self.color = 1
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
        if random_spawn:
            self.spawned = spawn(self)
        else:
            self.spawned = False


class Player(BaseCreature):
    name = "player"
    symbol = '☃'

    def __init__(self, team=0, spawn_pos=0):
        if spawn_pos == 0:
            BaseCreature.__init__(self, team, True)
        else:
            log.append(f"test {spawn_pos}")
            BaseCreature.__init__(self, team, False)
            self.x = spawn_pos[0]
            self.y = spawn_pos[1]
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

    def __init__(self, team=1, random_spawn=False):
        BaseCreature.__init__(self, team, random_spawn)
        self.name = "goblin"
        self.color = 2
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

    def __init__(self, team=2, random_spawn=False):
        BaseCreature.__init__(self, team, random_spawn)
        self.color = 3
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
    symbol = '!'

    def __init__(self, team=3, random_spawn=False):
        BaseCreature.__init__(self, team, random_spawn)
        self.color = 4
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
npc_spawn_rates = [100, 500, 50]  # implement

# initializing weapons
fists = Weapon("fists", 1, 1, 1)
claws = Weapon("claws", 1, 1, 2)
sword = Weapon("sword", 1, 1, 10)
shortsword = Weapon("shortsword", 1, 1, 6)
dagger = Weapon("dagger", 1, 1, 4)
pike = Weapon("pike", 2, 2, 12)
shortbow = Weapon("shortbow", 2, 4, 4)
longbow = Weapon("longbow", 2, 6, 4)

# constants
MAIN_WINDOW_WIDTH = 21 * 3  # in amount of characters
MAIN_WINDOW_HEIGHT = int(MAIN_WINDOW_WIDTH / 3)
SIDE_WINDOW_WIDTH = 15 * 3
SIDE_WINDOW_HEIGHT = 5  # int(SIDE_WINDOW_WIDTH/3)
LOG_LENGTH = 100
screen = curses.initscr()
INPUT_LINE = curses.newwin(2, SIDE_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT + SIDE_WINDOW_HEIGHT + 1, MAIN_WINDOW_WIDTH + 2)
curses.start_color()
curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

# initializing variables, maps, etc.
main_window_offset_x = 0  # in amount of tiles
main_window_offset_y = 0
log_window_offset = 0
map_width = 30  # width of map in tiles
map_height = 15  # height of map in tiles
blank_lines = 40  # amount of blank lines between each "screen"
random.seed()  # randomizes the randomizer
creature_list = []  # prepares list of creatures
map_creatures = []  # prepares map of creatures
map_terrain = []
cursor = [0, 0]
player_spawn_pos = [0, 0]
previous_turn = 0
input_char = ''
game_mode = ''
loaded_map = False
game_started = False
log = []
console_log = []
misc_log = []
creature_map_ratio = 20  # one creature per amount of tiles
show_only_attacks_on_player = False
curses.noecho()
curses.cbreak()
map_window = curses.newpad(0, 0)
log_window = curses.newpad(LOG_LENGTH, MAIN_WINDOW_WIDTH)
misc_window = curses.newpad(100, SIDE_WINDOW_WIDTH)
console_window = curses.newpad(100, SIDE_WINDOW_WIDTH)
curses.curs_set(0)

at_start_of_game()
map_window = curses.newpad(map_height, map_width * 3+1)

# initializes maps and stuff
map_ground = init_map_ground()  # creates empty ground map
creature_cap = int((map_width * map_height) / creature_map_ratio)
species_cap = creature_cap / (0.9 * len(npc_types))  # sets ratio of creatures to species
refresh_map_creatures()  # initializes map of creatures
map_temp = init_map_empty()  # initializes empty overlay map

map_mode = 'b'
if game_mode == 'b':  # creates empty map for build map mode
    if not loaded_map:
        map_terrain = init_map_terrain(empty=True)
else:
    if not loaded_map:
        if game_mode == 'p':
            console_log = []
            map_mode_chosen = False
            while not map_mode_chosen:
                console_log.append("Do you want to play on a (b)attlefield or explore a (d)ungeon?")
                show_screen()
                input_char = screen.getkey()
                console_log = []
                if input_char == 'b':
                    map_mode = 'b'
                    map_mode_chosen = True
                elif input_char == 'd':
                    map_mode = 'd'
                    map_mode_chosen = True
                else:
                    console_log.append("Invalid input.")
        map_terrain = init_map_terrain(empty=False)
    if game_mode == 'p':  # creates the player first in play mode
        if map_mode == 'd':
            creature_list.append(Player(spawn_pos=player_spawn_pos))
        else:
            creature_list.append(Player())
        player_index = len(creature_list) - 1
        player = creature_list[player_index]
        refresh_map_creatures()


input_char = ''
turn_counter = 0
quit_game = False
# todo add spells, with map editor edit creature type, add endless mode to dungeon
# improve battlefield spawning rates, improve vision/ranged attacks?, fix watch mode scrolling view with numpad
while not quit_game:
    game_started = True
    if game_mode == 'w':
        cursor_mode = True
        show_only_attacks_on_player = False
        player = None
        show_screen()  # without this, first button press=k acts weird
        while not quit_game:
            console_log.append("(q)uit, loo(k) or press any other key to go to the next turn.)")
            if map_width > MAIN_WINDOW_WIDTH / 3:
                if MAIN_WINDOW_WIDTH % 2 == 0:
                    middle_x = ((MAIN_WINDOW_WIDTH / 6) + main_window_offset_x / 3) - 1
                else:
                    middle_x = (MAIN_WINDOW_WIDTH / 6) + main_window_offset_x / 3
            else:
                middle_x = map_width / 2
            if map_height > MAIN_WINDOW_HEIGHT:
                middle_y = map_height - ((MAIN_WINDOW_HEIGHT / 2) + main_window_offset_y)
            else:
                middle_y = map_height / 2
            middle = [middle_x, middle_y]
            show_screen()
            input_char = screen.getkey()
            if input_char == 'q':
                quit_game = True
            elif input_char == 'k':
                look_at(location=middle)
            else:
                new_turn()
                turn_counter += 1
    elif game_mode == 'p':
        show_only_attacks_on_player = True
        while not quit_game and not player.dead:  # 1 loop is 1 turn
            end_turn = False
            new_turn()
            turn_counter += 1
    elif game_mode == 'b':
        build_mode()
    else:
        console_log.append("Error {}".format(game_mode))
