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

BOARD_EDGE = 3
MAX_DISTANCE = 7

MOVE_DISTANCE = 1
JUMP_DISTANCE = 2

RED_EXITS = [(3, -3), (3, -2), (3, -1), (3, 0)]
GREEN_EXITS = [(-3, 3), (-2, 3), (-1, 3), (0, 3)]
BLUE_EXITS = [(0, -3), (-1, -2), (-2, -1), (-3, 0)]

EXIT_DICT = {'red': RED_EXITS, 'blue': BLUE_EXITS, 'green': GREEN_EXITS}

RED_CORNERS = [(3, -3), (3, 0)]
GREEN_CORNERS = [(-3, 3), (0, 3)]
BLUE_CORNERS = [(0, -3), (-3, 0)]

RED_STARTS = [(-3, 0), (-3, 1), (-3, 2), (-3, 3)]
GREEN_STARTS = [(0, -3), (1, -3), (2, -3), (3, -3)]
BLUE_STARTS = [(0, 3), (1, 2), (2, 1), (3, 0)]

# temporary holding place for exiting pieces
EXIT_LOC = (3, 1)

PLAYER_LIST = ['red', 'green', 'blue']

WINNING_EXITS = 4

CUTOFF_DEPTH = 3

# scaling factors for eval function
DIST_SCALE = 10/7
PIECE_SCALE = 10
EXIT_SCALE = 10/4



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
        # set up state representation
        self.colour = colour
        self.board = self.createBoard()
        self.updated_board = self.createBoard()
        self.numexits = [0, 0, 0]
        # assign exits according to colour
        if colour == "red":
            self.exits = RED_EXITS
        elif colour == "green":
            self.exits = GREEN_EXITS
        else:
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
        searched = self.maxn(self.board, self.colour, 0, self.numexits)[1]
        if searched:
            return searched
        else :
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

        if action[0] == 'PASS':
            pass
        # if the action is a jump or move
        elif isinstance(action[1][0], tuple):
            coord = action[1][0]
            new_coord = action[1][1]
            self.updated_board = self.update_board(self.updated_board, coord, new_coord)
            # change the colour of a piece that is jumped over
            if action[0] == 'JUMP':
                jumpedover = self.jumped_piece(coord, new_coord)
                self.updated_board = self.jump_update(self.updated_board, jumpedover, colour)
        # if the action is an exit
        elif action[0] == 'EXIT':
            colour_index = PLAYER_LIST.index(colour)
            self.numexits[colour_index] += 1
            coord = action[1]
            self.updated_board = self.make_exit(coord, self.updated_board)
        # make final updates
        self.board = dict(self.updated_board)

    def startinPieces(self, colour):
        """
        This function finds the initial piece locations for a player.
        :param colour: the colour of the player in question
        :return: a list of the piece coordinates
        """

        if colour == "red":
            pieces = RED_STARTS
        elif colour == "green":
            pieces = GREEN_STARTS
        else:
            pieces = BLUE_STARTS
        return pieces

    def createBoard(self):
        """
        This function creates the initial board state.
        """
        board = {}
        for blue in BLUE_STARTS:
            board[blue] = 'blue'
        for green in GREEN_STARTS:
            board[green] = 'green'
        for red in RED_STARTS:
            board[red] = 'red'
        return board

    def exit_distances(self, state, colour):
        """
        This function averages the distance of all a player's pieces from the exits.
        :param state: the current board state
        :param colour: the colour of the player
        :return: the average distance from the exits
        """
        state_val = 0
        piece_count = 0
        exits = EXIT_DICT[colour]
        # iterate through all pieces on the board
        for piece in self.dict_to_tuple(state):
            min_piece_distance = MAX_DISTANCE
            # ignore other player pieces
            if piece[1] == colour:
                piece_count += 1
                # calculate the distance from the piece to each of the exits
                for exit_location in exits:
                    if self.distance(piece[0], exit_location) < min_piece_distance:
                        min_piece_distance = self.distance(piece[0], exit_location)
                # add the distance to the closest exit to the overall state value
                state_val += min_piece_distance
        # assume the average distance of no pieces is in the middle
        if piece_count == 0:
            return MAX_DISTANCE / 2
        return state_val / piece_count

    def z_coordinate(self, coord):
        """
        Gives the mathematical z-coordinate of a space, given its x and y coordinates
        :param coord: a two-tuple containing the x and y coordinates of a space
        :return: the value of the z-coordinate
        """
        return -(coord[X]) - coord[Y]

    def distance(self, coord1, coord2):
        """
        Calculates the Euclidean heaxagonal distance between two spaces
        :param coord1: a tuple containing an x and y coordinate
        :param coord2: a second tuple containing an x and y coordinate
        :return: the number of spaces need to traverse from coord1 to coord2
        """
        z_coord1 = self.z_coordinate(coord1)
        z_coord2 = self.z_coordinate(coord2)
        return int((abs(coord2[X] - coord1[X]) + abs(coord2[Y] - coord1[Y]) + abs(z_coord2 - z_coord1)) / 2)

    def is_empty_space(self, coord):
        """
        Determines if a space has a piece on it.
        :param coord: the x and y coordinates of the space
        :return: a boolean value indicating True if there is no piece on the space, False otherwise.
        """
        if not self.is_on_board(coord[X], coord[Y]):
            return False
        elif coord not in self.board or self.board[coord] == "":
            return True
        return False

    def is_on_board(self, x, y):
        """
        Determines if a space is part of the game board.
        :param x: x coordinate of the space
        :param y: y coordinate of the space
        :return: boolean True if the space is part of the game board, False otherwise
        """
        if abs(x) > BOARD_EDGE or abs(y) > BOARD_EDGE or abs(self.z_coordinate((x, y))) > BOARD_EDGE:
            return False
        return True

    def can_exit(self, state, piece):
        """
        Determines if a particular piece is able to exit.
        :param state: the current game state
        :param piece: a tuple indicating the coordinates of the piece
        :return: a boolean value of True if the piece is located on an exit of its colour
        """
        if state[piece] == 'red':
            if piece in RED_EXITS:
                return True
        elif state[piece] == 'green':
            if piece in GREEN_EXITS:
                return True
        elif state[piece] == 'blue':
            if piece in BLUE_EXITS:
                return True
        return False

    def can_move(self, coord):
        """
        Finds all the legal moves or jumps a piece can make
        :param coord: the location of the piece
        :return: a list containing the coordinates of the piece's next possible locations
        """
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

    def action_type(self, old_coord, new_coord):
        """
        Determines what type of action is made by a piece
        :param old_coord: the location of the piece before the move
        :param new_coord: the location of the piece after the move
        :return: a string indicating the action type
        """
        if old_coord is None:
            return "PASS"
        elif new_coord is None:
            return "EXIT"
        elif self.distance(old_coord, new_coord) == MOVE_DISTANCE:
            return "MOVE"
        elif self.distance(old_coord, new_coord) == JUMP_DISTANCE:
            return "JUMP"
        else:
            return None

    def dict_to_tuple(self, state):
        return tuple(state.items())

    def update_board(self, board, coord, new_coord):
        """
        Updates a board state, given a certain action.
        :param board: the current board state
        :param coord: the initial coordinate of the piece taking action
        :param new_coord: the final coordinate of the piece taking action
        :return: the updated board state
        """
        # remove the old coordinate's player
        color = board[coord]
        # change colour of a piece that gets jumped over
        if self.distance(coord, new_coord) == JUMP_DISTANCE:
            self.jump_update(board, self.jumped_piece(coord, new_coord), color)
        del board[coord]
        # place the player on the new coordinate
        if new_coord != EXIT_LOC:
            board[new_coord] = color
        return board

    def format_move(self, old_coord, new_coord=None):
        """
        Formats an action according to referee specifications
        :param old_coord: initial location of the piece taking action
        :param new_coord: final location of the piece taking action
        :return: a tuple containing the action's type and old and new locations
        """
        action = self.action_type(old_coord, new_coord)
        # if the action is an exit, remove piece from board
        if old_coord is None:
            return (action, None)
        if new_coord is None:
            return (action, tuple(old_coord))
        # if the action is a move or jump, move piece to its next location
        else:
            return (action, (tuple(old_coord), tuple(new_coord)))

    def generate_next_states(self, state, colour):
        """
        Generates all the possible states after a player makes an action.
        :param state: the game state before the player takes action
        :param colour: the colour of the player
        :return: a list of all state values that would result from the player's next action
        """
        next_state = []
        for piece in state:
            if state[piece] == colour:
                if self.can_exit(state, piece):
                    tmp_board = state.copy()
                    tmp_board = self.make_exit(piece, tmp_board)
                    next_state.append(tmp_board)
                # if the piece can move or jump, generate a new state for its possible actions
                for move in self.can_move(piece):
                    if move:
                        tmp_board = state.copy()
                        tmp_board = self.update_board(tmp_board, piece, move)
                        next_state.append(tmp_board)
        # if the player must pass, the board state will remain the same
        if len(next_state) == 0:
            next_state.append(state)
            return next_state
        return next_state

    def state_diff(self, state1, state2):
        """
        Finds the old and new coordinates of a piece that has moved
        :param state1: the board state before a move
        :param state2: the board state after a move
        :return: the filled spaces that have changed between the states
        """
        diff = [None, None]
        for piece in state1:
            if piece not in state2:
                diff[0] = piece
                # if a piece has exited between states, there is no new location
                if len(state2) < len(state1):
                    return diff
                # if a piece has moved between states, find new location
                for new_piece in state2:
                    if new_piece not in state1:
                        diff[1] = new_piece
        return diff

    def make_exit(self, coord, state):
        """
        Removes a certain piece from the board
        :param coord: the location where the piece exits from
        :param state: the board state before the exit is made
        :return: the new state
        """
        del state[coord]
        return state

    def jumped_piece(self, oldcoord, newcoord):
        """
        Finds the piece that is jumped over
        :param oldcoord: the initial location of a piece that jumps
        :param newcoord: the location the jumping piece jumps to
        :return: the coordinates of the space that was jumped over
        """
        x1 = newcoord[0]
        y1 = newcoord[1]
        x2 = oldcoord[0]
        y2 = oldcoord[1]

        # the difference in x and y values
        diffX = x1 - x2
        diffY = y1 - y2

        # for a horizontal jump
        if abs(diffX) == JUMP_DISTANCE and diffY == 0:
            return (x1 - int(1 * np.sign(diffX)), y1)
        # for a diagonal jump
        elif abs(diffX) == JUMP_DISTANCE and abs(diffY) == JUMP_DISTANCE:
            return (x1 - int(1 * np.sign(diffX)), y1 - int(1 * np.sign(diffY)))
        elif diffX == 0 and abs(diffY) == JUMP_DISTANCE:
            return (x1, y1 - int(1 * np.sign(diffY)))


    def find_numpieces(self, colour, state):
        """
        Finds the number of pieces a player has on the board
        :param colour: the player's colour
        :param state: the current board state
        :return: the number of pieces of the player's colour on the board
        """
        numpieces = 0
        for piece in self.dict_to_tuple(state):
            if piece[1] == colour:
                numpieces += 1
        return numpieces

    def jump_update(self, board, coord, colour):
        """
        Updates the colour of a piece being jumped
        :param board: the initial board state
        :param coord: the coordinate of the piece being jumped
        :param colour: the new colour of the converted piece
        :return: the new board state
        """
        board[coord] = colour
        return board

    def next_player(self, colour):
        """
        Finds the colour of the next player to make an action
        :param colour: the colour of the current player
        :return: the next player's colour
        """
        next_player_index = (PLAYER_LIST.index(colour) + 1) % len(PLAYER_LIST)
        return PLAYER_LIST[next_player_index]

    def generate_surroundings(self, coord):
        """
        Finds the spaces surrounding a given space
        :param coord: the coordinates of the space
        :return: a list of the spaces immediately adjacent to the space
        """
        x = coord[0]
        y = coord[1]
        move_list = []
        # show all directions
        move_list.append((x + 1, y))
        move_list.append((x + 1, y - 1))
        move_list.append((x, y + 1))
        move_list.append((x - 1, y))
        move_list.append((x - 1, y + 1))
        move_list.append((x, y - 1))
        return move_list

    def find_captors(self, state, colour):
        """
        Estimates the number of enemies can capture a piece in a given state.
        :param state: the current board state
        :param colour: the colour of the pieces that may be captured
        :return: the number of enemy pieces adjacent to player pieces
        """
        evaluation_num = 0
        for space in list(state.keys()):
            # check surroundings
            if state[space] == colour:
                surroundings = self.generate_surroundings(space)
                for possible_enemy in surroundings:
                    if possible_enemy in list(state.keys()) and state[possible_enemy] != colour:
                        evaluation_num += 1
                    else:
                        continue

        return evaluation_num

    def should_cutoff(self, depth, exits):
        """
        Determines if the maxn search should be cut off
        :param depth: the current depth of the tree
        :param exits: the list of exits that have been made
        :return: boolean value True if the game has been won, False otherwise
        """
        if depth >= CUTOFF_DEPTH:
            return True
        for player in exits:
            if player >= 4:
                return True
        return False

    def piece_eval(self, player, state, exits):
        """
        Function for evaluating the number of a player's pieces
        :param player: the colour of the player
        :param state: the projected board state
        :param exits: the projected list of exits made
        :return: scaled value of the number of pieces
        """
        numpieces = self.find_numpieces(player, state)
        if numpieces != 0:
            ratio = (WINNING_EXITS - exits[PLAYER_LIST.index(player)]) / self.find_numpieces(player, state)
        else:
            ratio = (WINNING_EXITS - exits[PLAYER_LIST.index(player)])
        if (1 - abs(1 - ratio)) <= 0:
            return 0
        return (1 - abs(1 - ratio)) * PIECE_SCALE

    def evaluation(self, state, exits):
        """
        Evaluates the board state
        :param state: the board state
        :param exits: the number of exits made at the time of the board state
        :return: a list of the state evaluation for each player
        """
        evals = []
        # criteria in order: distance, exit and number of pieces
        weights = [4, 3, 2]
        captured_weight = 1
        for player in PLAYER_LIST:
            # adjust weighting according to the number of pieces left
            if self.find_numpieces(player, state) + exits[PLAYER_LIST.index(player)] < 4:
                captured_weight = 3
                weights = [2, 3, 5]
            elif self.find_numpieces(player, state) + exits[PLAYER_LIST.index(player)] > 5:
                weights = [2, 2, 4]
            # evaluate criteria
            distance_eval = (MAX_DISTANCE - self.exit_distances(state, player)) * DIST_SCALE
            exits_eval = exits[PLAYER_LIST.index(player)] * EXIT_SCALE
            piece_eval = self.piece_eval(player, state, exits)
            captured = self.find_captors(state, player)
            # add up the criteria values, adjusted for weight
            player_val = weights[0] * distance_eval + weights[1] * exits_eval + weights[
                2] * piece_eval + captured_weight * captured
            evals.append(player_val)
        return evals

    def maxn(self, state, player, depth, exits):
        """
        Runs the maxn algorithm, derived from pseudocode provided to students of COMP30024 by Matt Farrugia
        :param state: the state to be evaluated
        :param player: the player aiming to maximise its states
        :param depth: the current depth being looked at
        :param exits: the number of exits made at this state
        :return: a tuple containing the evaluation, as well as the best action to take
        """
        tmp_exits = exits.copy()
        player_index = PLAYER_LIST.index(player)
        # check if this is a cutoff state
        if self.should_cutoff(depth, tmp_exits):
            return (self.evaluation(state, tmp_exits), None)
        v_max = [-math.inf, -math.inf, -math.inf]
        best_action = None
        # generate the next states
        for next_state in self.generate_next_states(state, player):
            # keep track of any exits made in projected state
            action_coords = self.state_diff(state, next_state)
            if action_coords[0] is not None and action_coords[1] is None:
                tmp_exits[player_index] += 1
            # evaluate projected state
            next_v = self.maxn(next_state, self.next_player(player), depth + 1, tmp_exits)[0]
            # if this is the best outcome so far
            if next_v[player_index] > v_max[player_index]:
                v_max = next_v
                best_action = self.format_move(action_coords[0], action_coords[1])
            tmp_exits = exits.copy()
        return (v_max, best_action)