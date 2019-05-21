import rule_implementation

CUTOFF_DEPTH = 3
# scaling factors for eval function
DIST_SCALE = 10/7
PIECE_SCALE = 10
EXIT_SCALE = 10/4

# determines if maxn should be cut off
def should_cutoff(self, depth, exits):
    if depth >= CUTOFF_DEPTH:
        return True
    for player in exits:
        if player >= 4:
            return True
    return False


def piece_eval(self, player, state, exits):
    numpieces = self.find_numpieces(player, state)
    if numpieces != 0:
        ratio = (WINNING_EXITS - exits[PLAYER_LIST.index(player)]) / self.find_numpieces(player, state)
    else:
        ratio = (WINNING_EXITS - exits[PLAYER_LIST.index(player)])
    if (1 - abs(1 - ratio)) <= 0:
        return 0
    return (1 - abs(1 - ratio)) * PIECE_SCALE


def evaluation(self, state, exits):
    evals = []
    weights = [4, 3, 2]
    captured_weight = 1
    for player in PLAYER_LIST:
        if (self.find_numpieces(player, state) + exits[PLAYER_LIST.index(player)] < 4):
            captured_weight = 3
            weights = [2, 3, 5]
        elif (self.find_numpieces(player, state) + exits[PLAYER_LIST.index(player)] > 5):
            weights = [2, 2, 4]
        distance_eval = (MAX_DISTANCE - self.exit_distances(state, player)) * DIST_SCALE
        exits_eval = exits[PLAYER_LIST.index(player)] * EXIT_SCALE
        piece_eval = self.piece_eval(player, state, exits)
        captured = self.canBeCaptured(state, player)
        player_val = weights[0] * distance_eval + weights[1] * exits_eval + weights[
            2] * piece_eval + captured_weight * captured
        evals.append(player_val)
    return evals


def maxn(self, state, player, depth, exits):
    tmp_exits = exits.copy()
    player_index = PLAYER_LIST.index(player)
    if self.should_cutoff(depth, tmp_exits):
        return (self.evaluation(state, tmp_exits), None)
    v_max = [-math.inf, -math.inf, -math.inf]
    best_action = None
    for next_state in self.generate_next_states(state, player):
        action_coords = self.state_diff(state, next_state)
        if action_coords[0] is not None and action_coords[1] is None:
            tmp_exits[player_index] += 1
        next_v = self.maxn(next_state, self.next_player(player), depth + 1, tmp_exits)[0]
        if next_v[player_index] > v_max[player_index]:
            v_max = next_v
            best_action = self.format_move(action_coords[0], action_coords[1])
        tmp_exits = exits.copy()
    return (v_max, best_action)