import copy

# heuristic is distance to goal


def sort_tile_cost(given_list):
    return given_list[2]


def get_distance(a, b):
    distance_x = abs(a[0] - b[0])
    distance_y = abs(a[0] - b[0])
    if distance_x > distance_y:
        return distance_x
    else:
        return distance_y


def a_star(start, goal):
    # tile = [x, y, total_cost, parent_tile]
    neighbours = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]
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
        # print(current_tile)
        if current_tile[:2] == goal:    # checks if you've found the goal
            break
        for neighbour in neighbours:    # selects tiles next to current tile
            new_tile = copy.deepcopy(current_tile)  # makes a copy so current_tile doesn't get edited
            new_tile[0] += neighbour[0]
            new_tile[1] += neighbour[1]
            # todo make it so different terrain costs can be read from map and dictionary and used here
            # adds cost to the new tile: previous tile's cost plus one and new/updated distance cost
            new_tile[2] = (current_tile[2] + 1 - get_distance(current_tile, goal) + get_distance(new_tile, goal))
            print(new_tile)
            new_tile[3] = current_tile  # adds parent tile
            print(new_tile)
            print()
            # checks if new tile is in the open list
            in_open = False
            for tile in open_list:
                if tile[0] == new_tile[0] and tile[1] == new_tile[1]:
                    in_open = True
                    if tile[2] >= new_tile[2]:  # checks if new route to tile is better
                        tile = new_tile  # updates to better parent tile
                    break
            # check if new tile is in the closed list
            in_closed = False
            if not in_open:
                for tile in closed_list:
                    if tile[0] == new_tile[0] and tile[1] == new_tile[1]:
                        in_closed = True
                        if tile[2] >= new_tile[2]:  # checks if new route to tile is better
                            tile = new_tile  # updates to better parent tile
                            open_list.append(tile)
                            closed_list.remove(tile)
                        break
            if not in_open and not in_closed:   # if it's a new tile add it to the open list
                new_tile
                open_list.append(new_tile)
        # print(open_list)
        open_list.remove(current_tile)
        # print(open_list)
        # print()
        closed_list.append(current_tile)
    if current_tile[:2] != goal:
        print("Goal not reachable.")
    else:
        print("Goal reached.")
        positions = []
        end = False
        while not end:
            try:
                if len(current_tile[3]) == 4:
                    positions.append(current_tile[:2])
                    current_tile = current_tile[3]
                else:
                    end = True
            except TypeError:
                end = True
        return positions


start1 = [2, 0]
goal1 = [1, 2]
next_step = a_star(start1, goal1)
print(next_step)
