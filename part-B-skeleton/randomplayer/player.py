import random

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
        self.board = self.createBoard()
        self.pieces = []
        # assign exits according to colour
        if colour == "red":
            self.pieces = RED_STARTS
            self.exits = RED_EXITS
        elif colour == "green":
            self.pieces = GREEN_STARTS
            self.exits = GREEN_EXITS
        else:
            self.pieces = BLUE_STARTS
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
        # TODO: Decide what action to take.
        movedict = {}
        for piece in self.pieces:
            if piece in self.exits:
                return self.print_move(piece, None)
            elif any(self.can_move(piece)):
                movedict[piece] = filter(None, self.can_move(piece))
        if not movedict:
            return ("PASS", None)
        else:
            randpiece = random.choice(list(movedict.keys()))
            randmove = random.choice(movedict[randpiece])
            return self.print_move(randpiece, randmove)


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

        ## take note of color not yet
        coord = action[1][0]
        new_coord = action[1][1]
        self.update_board(self.board, coord, new_coord)

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
        colour = board[coord]
        del board[coord]
        # place the player on the new coordinate
        if new_coord != EXIT_LOC:
            board[new_coord] = colour
        if colour == self.colour:
            self.pieces[self.pieces.index(coord)] = new_coord
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


    # removes a certain piece from the board
    def make_exit(self, coord, state):
        del state[coord]
        return state


    def createBoard():
        ## creates initial board
        board = {}
        for blue in BLUE_STARTS:
            board[blue] = 'blue'
        for green in GREEN_STARTS:
            board[green] = 'green'
        for red in RED_STARTS:
            board[red] = 'red'
        return board