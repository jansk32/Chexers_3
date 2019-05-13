from collections import defaultdict
import math
import numpy as np

    # coordinate indexes
X = 0
Y = 1

# directions relative to a space
DIRECTION_E = 0
DIRECTION_SE = 1
DIRECTION_SW = 2
DIRECTION_W = 3
DIRECTION_NW = 4
DIRECTION_NE = 5

# PLAYER_TYPE = ''

BOARD_EDGE = 3
MAX_DISTANCE = 7

MOVE_DISTANCE = 1
JUMP_DISTANCE = 2

RED_EXITS = [(3, -3), (3, -2), (3, -1), (3, 0)]
GREEN_EXITS = [(-3, 3), (-2, 3), (-1, 3), (0, 3)]
BLUE_EXITS = [(0, -3), (-1, -2), (-2, -1), (-3, 0)]

RED_CORNERS = [(3, -3), (3, 0)]
GREEN_CORNERS = [(-3, 3), (0, 3)]
BLUE_CORNERS = [(0, -3), (-3, 0)]

RED_STARTS = [(-3, 0), (-3, 1), (-3, 2), (-3, 3)]
GREEN_STARTS = [(0, -3), (1, -3), (2, -3), (3, -3)]
BLUE_STARTS = [(0, 3), (1, 2), (2, 1), (3, 0)]

# temporary holding place for exiting pieces
EXIT_LOC = (3, 1)

class ExamplePlayer:
    def __init__(self, colour):
        """
        This method is called once at the beginning of the game to initialise
        your player. You should use this opportunity to set up your own internal
        representation of the game state, and any other information about the 
        game state you would like to maintain for the duration of the game.

        The parameter colour will be a string representing the player your 
        program will play as (Red, Green or Blue). The value will be one of the 
        strings "red", "green", or "blue" correspondingly.
        """
        # TODO: Set up state representation.
        self.colour = colour
        ## to decide what the initial pieces are
        self.pieces = []
        pieces = self.startinPieces(self.colour)
        for i in pieces:
            self.pieces.append(tuple(i))
        self.board = self.createBoard()
        self.updated_board = self.createBoard()
        # assign exits according to colour
        if colour == "red":
            # PLAYER_TYPE = "red"
            self.exits = RED_EXITS
        elif colour == "green":
            # PLAYER_TYPE = "green"
            self.exits = GREEN_EXITS
        else:
            # PLAYER_TYPE = "blue"
            self.exits = BLUE_EXITS



    def action(self):
        """
        This method is called at the beginning of each of your turns to request 
        a choice of action from your program.

        Based on the current state of the game, your player should select and 
        return an allowed action to play on this turn. If there are no allowed 
        actions, your player must return a pass instead. The action (or pass) 
        must be represented based on the above instructions for representing 
        actions.
        """
        goal = self.generate_goal()
        searched = self.a_star(self.board, goal)
        if (searched):
            return searched
        else :
        # TODO: Decide what action to take.
            return ("PASS", None)


    def update(self, colour, action):
        """
        This method is called at the end of every turn (including your player’s 
        turns) to inform your player about the most recent action. You should 
        use this opportunity to maintain your internal representation of the 
        game state and any other information about the game you are storing.

        The parameter colour will be a string representing the player whose turn
        it is (Red, Green or Blue). The value will be one of the strings "red", 
        "green", or "blue" correspondingly.

        The parameter action is a representation of the most recent action (or 
        pass) conforming to the above in- structions for representing actions.

        You may assume that action will always correspond to an allowed action 
        (or pass) for the player colour (your method does not need to validate 
        the action/pass against the game rules).
        """
        # TODO: Update state representation in response to action.
        
        coord = action[1][0]
        new_coord = action[1][1]
        

        self.updated_board = self.update_board(self.updated_board, coord, new_coord)
        if action[0] == 'JUMP':
            jumpedOver = self.isJumped(coord, new_coord)
            self.updated_board = self.jump_update(self.updated_board, jumpedOver, colour)
            print(self.updated_board)
        self.board = dict(self.updated_board)
        self.pieces = self.updatePieces(self.updated_board)
        print("SELF.PIECES: ",self.colour, self.pieces,"\n\n")
    
    # uses a heuristic function to return a value for the given state
    def heuristic(self, state):
        state_val = 0
        # iterate through all pieces on the board
        for piece in state:
            min_piece_distance = MAX_DISTANCE
            # ignore blocks
            if piece[1] == self.colour:
                # calculate the distance from the piece to each of the exits
                for exit_location in self.exits:
                    if self.distance(piece[0], exit_location) < min_piece_distance:
                        min_piece_distance = self.distance(piece[0], exit_location)
                # add the distance to the closest exit to the overall state value
                state_val += min_piece_distance + 1
        return state_val

    # returns the mathematical z coordinate of a space given its x and y coordinate
    def z_coordinate(self, coord):
        return -(coord[X]) - coord[Y]

    # returns the minimum number of spaces to traverse between two spaces
    def distance(self, coord1, coord2):
        z_coord1 = self.z_coordinate(coord1)
        z_coord2 = self.z_coordinate(coord2)
        return int((abs(coord2[X] - coord1[X]) + abs(coord2[Y] - coord1[Y]) + abs(z_coord2 - z_coord1)) / 2)

    # identifies if a given space has an object on it or not
    def is_empty_space(self, coord):
        if not self.is_on_board(coord[X], coord[Y]):
            return False
        elif coord not in self.board or self.board[coord] == "":
            return True
        return False

    # returns a boolean value indicating whether a given coordinate is on the board
    def is_on_board(self, x, y):
        if abs(x) > BOARD_EDGE or abs(y) > BOARD_EDGE or abs(self.z_coordinate((x, y))) > BOARD_EDGE:
            return False
        return True

    # returns list of all possible hexes a piece can move or jump to, given the piece's location
    def can_move(self, coord):
        [x, y] = coord
        move_list = [None] * 6
        # check if a move or jump can be made to the east
        if self.is_empty_space((x + 1, y)):
            move_list[DIRECTION_E] = (x + 1, y)
        elif self.is_empty_space((x + 2, y)):
            move_list[DIRECTION_E] = (x + 2, y)
        # check if a move or jump can be made to the southeast
        if self.is_empty_space((x + 1, y - 1)):
            move_list[DIRECTION_NE] = (x + 1, y - 1)
        elif self.is_empty_space((x + 2, y - 2)):
            move_list[DIRECTION_NE] = (x + 2, y - 2)
        # check if a move or jump can be made to the southwest
        if self.is_empty_space((x, y + 1)):
            move_list[DIRECTION_SE] = (x, y + 1)
        elif self.is_empty_space((x, y + 2)):
            move_list[DIRECTION_SE] = (x, y + 2)
        # check if a move or jump can be made to the west
        if self.is_empty_space((x - 1, y)):
            move_list[DIRECTION_W] = (x - 1, y)
        elif self.is_empty_space((x - 2, y)):
            move_list[DIRECTION_W] = (x - 2, y)
        # check if a move or jump can be made to the northwest
        if self.is_empty_space((x - 1, y + 1)):
            move_list[DIRECTION_SW] = (x - 1, y + 1)
        elif self.is_empty_space((x - 2, y + 2)):
            move_list[DIRECTION_SW] = (x - 2, y + 2)
        # check if a move or jump can be made to the northeast
        if self.is_empty_space((x, y - 1)):
            move_list[DIRECTION_NW] = (x, y - 1)
        elif self.is_empty_space((x, y - 2)):
            move_list[DIRECTION_NW] = (x, y - 2)
        return move_list

    # indicates whether an action is an exit, move or a jump
    def action_type(self, old_coord, new_coord):
        if new_coord is None:
            return "EXIT"
        elif self.distance(old_coord, new_coord) == MOVE_DISTANCE:
            return "MOVE"
        elif self.distance(old_coord, new_coord) == JUMP_DISTANCE:
            return "JUMP"
        else:
            return None

    # converts a dictionary to a tuple format
    def dict_to_tuple(self, state):
        a = tuple(state.items())
        return a

    # updates the input board
    def update_board(self, board, coord, new_coord):
        # remove the old coordinate's player
        color = board[coord]
        del board[coord]
        # place the player on the new coordinate
        if new_coord != EXIT_LOC:
            board[new_coord] = color
        return board

    #  prints output describing the move
    def print_move(self, old_coord, new_coord=None):
        action = self.action_type(old_coord, new_coord)
        # if the action is an exit, remove piece from board
        if new_coord is None:
            ## for part b
            return (action, tuple(old_coord))
            ##("{} from {}.".format(action, tuple(old_coord)))
        # if the action is a move or jump, move piece to its next location
        else:
            ## for part b
            return (action,(tuple(old_coord), tuple(new_coord)))
            #print("{} from {} to {}.".format(action, tuple(old_coord), tuple(new_coord)))

    # generates a list of states showing the next possible actions
    def generate_next_states(self, state):
        next_state = []
        for piece in state:
            if state[piece] == self.colour:
                # if the piece can move or jump, generate a new state for its possible actions
                for move in self.can_move(piece):
                    if move:
                        tmp_board = state.copy()
                        tmp_board = self.update_board(tmp_board, piece, move)
                        tmp_board = self.dict_to_tuple(tmp_board)
                        next_state.append(tmp_board)
        return next_state

    # generates the goal state based on the initial board
    def generate_goal(self):
        goal_board = self.board.copy()
        # remove all the player pieces from the board copy
        for piece in self.pieces:
            del goal_board[piece]
        goal_board = self.dict_to_tuple(goal_board)
        return goal_board

    # determines the next node to look at
    def find_current(self, total_cost, open_set):
        min_cost = total_cost[open_set[0]]
        current = None
        # choose the open node with the lowest cost
        for state in open_set:
            if total_cost[state] <= min_cost:
                current = state
                min_cost = total_cost[state]
        return current

    # finds the difference between two states
    def state_diff(self, state1, state2):
        diff = [None, None]
        for piece in state1:
            if piece not in state2:
                diff[0] = piece[0]
                # if a piece has exited between states, there is no new location
                if len(state2) < len(state1):
                    return diff
                # if a piece has moved between states, find new location
                for new_piece in state2:
                    if new_piece not in state1:
                        diff[1] = new_piece[0]
        return diff

    # reconstructs the path to the current node. based off webinar code provided by Matt Farrugia (2019)
    def construct_path(self, came_from, goal):
        path = []
        state = goal
        # trace steps backwards from goal
        while came_from[state] is not None:
            path.append(state)
            state = came_from[state]
        path.append(state)
        path.reverse()
        # print the moves made
        action = self.state_diff(path[0], path[path.index(state) + 1])
        return self.print_move(action[0], action[1])
        # for state in path[:-1]:
        #     action = self.state_diff(state, path[path.index(state) + 1])
        #     self.print_move(action[0], action[1])

    # removes a certain piece from the board
    def make_exit(self, coord, state):
        del state[coord]
        return state

    # runs the a* algorithm to find the best moves to the goal state. derived from pseudocode
    # available on wikipedia.org
    def a_star(self, start, goal):
        # initialise state sets that a* keeps track of
        start = self.dict_to_tuple(start)
        closed_set = []
        open_set = [start]
        came_from = {start: None}
        # known distance from initial state
        g_cost = defaultdict(lambda: math.inf)
        g_cost[start] = 0
        # g_cost added to heuristic
        total_cost = defaultdict(lambda: math.inf)
        total_cost[start] = self.heuristic(start)
        
        # while there are open nodes to consider
        while open_set:
            current = self.find_current(total_cost, open_set)
            current_dict = dict(current)
        

            # search whether a player is on an exit, if so, EXIT
            for i in list(current):
                if i[0] in self.exits and i[1] == self.colour:
                    old_state = current
                    open_set.remove(current)
                    # make exit
                    current_dict = self.make_exit(i[0], current_dict)
                    current = tuple(current_dict.items())
                    # adjust trackers
                    came_from[current] = old_state
                    g_cost[current] = 0
                    total_cost[current] = self.heuristic(current)
                    open_set.append(current)

            self.board = current_dict

            # if goal has been reached, return reconstructed path
            if current == goal:
                print("goal found")
                return self.construct_path(came_from, goal)

            open_set.remove(current)
            closed_set.append(current)
            # evaluate possible states to succeed current state
            for next_state in self.generate_next_states(current_dict):
                if next_state in closed_set:
                    continue

                temp_g_cost = g_cost[current] + 1
                if next_state not in open_set:
                    open_set.append(next_state)
                elif temp_g_cost >= g_cost[next_state]:
                    continue

                # if this state is the best successor so far
                came_from[tuple(next_state)] = current
                g_cost[tuple(next_state)] = temp_g_cost
                total_cost[tuple(next_state)] = g_cost[tuple(next_state)] + self.heuristic(next_state)
    
    def createBoard(self):
        ## creates initial board
        board = {}
        for blue in BLUE_STARTS:
            board[blue] = 'blue'
        for green in GREEN_STARTS:
            board[green] = 'green'
        for red in RED_STARTS:
            board[red] = 'red'
        return board

    ## determining if a player can be captured in the next step
    def canBeCaptured(self, coord, next_state):
        new = self.generate_next_states(next_state)
        for space in new:
            if space in self.board and self.board[space] != self.colour:
                return True
        return False

    ## aim for corners
    def aimCorners(self, board, colour):
        ## only implemented when flag indicates to use this
        if colour == "red":
            self.exits = RED_CORNERS
        elif colour == "green":
            self.exits = GREEN_CORNERS
        else:
            self.exits = BLUE_CORNERS

    def startinPieces(self, colour):
        if colour == "red":
            pieces = RED_STARTS
        elif colour == "green":
            pieces = GREEN_STARTS
        else:
            pieces = BLUE_STARTS
        return pieces

    ## update pieces
    def updatePieces(self, board):
        pieces = []
        for piece in board.keys():
            if board[piece] == self.colour:
                pieces.append(piece)
        return pieces

    def isJumped(self, oldcoord, newcoord):
        #newcoord x,y
        x1 = newcoord[0]
        y1 = newcoord[1]

        #oldcoord x,y
        x2 = oldcoord[0]
        y2 = oldcoord[1]

        # diff x,y
        diffX = x1-x2
        diffY = y1-y2

        if(abs(diffX) == 2 and diffY == 0):
            return (x1-(1* np.sign(diffX)), y1)
        elif(abs(diffX) == 2 and abs(diffY) == 2):
            return (x1-(1* np.sign(diffX)), y1 - (1* np.sign(diffY)))
        elif(diffX == 0 and abs(diffY) == 2):
            return (x1, y1 -(1* np.sign(diffY)))
        ## hardcode this???any simpler way
    
    # update the board with a jump
    def jump_update(self, board, coord, colour):
        del board[coord]
        board[coord] = colour
        return board

    def evaluation(self, board):
        eval = []
        return eval