
from bridgeobjects import SEATS


def undo_cardplay(board, mode):
    if len(board.tricks) >= 2 and len(board.tricks[-1].cards) == 0:
        board.tricks = board.tricks[: -1]
    if len(board.tricks) == 1:
        _undo_trick_one(board, mode)
    else:
        _undo_subsequent_trick(board, mode)
    _adjust_score(board)


def _undo_trick_one(board, mode):
    if mode == 'solo':
        _undo_trick_one_solo(board)
    else:
        _undo_trick_one_duo(board)


def _undo_subsequent_trick(board, mode):
    if mode == 'solo':
        _undo_subsequent_trick_solo(board)
    else:
        _undo_subsequent_trick_duo(board)


def _undo_trick_one_solo(board):
    trick = board.tricks[0]
    if board.declarer in 'NS':
        # Both N & S play cards
        if len(trick. cards) < 3:
            return

        if len(trick. cards) == 3:
            _remove_cards_from_trick(board, trick, 2, 3)
            return

        elif len(trick. cards) == 4:
            _remove_cards_from_trick(board, trick, 4, 4)

    elif board.declarer == 'W':
        # Only N can play cards
        if len(trick.cards) < 4:
            return
        _remove_cards_from_trick(board, trick, 1, 4)

    # TODO
    # elif board.declarer == 'E':
        # Only N can play cards
        # Nothing to do trick one


def _undo_trick_one_duo(board):
    trick = board.tricks[0]

    if board.declarer in 'NS':
        if len(trick.cards) == 3:
            _remove_cards_from_trick(board, trick, 2, 3)
        elif len(trick.cards) == 4:
            _remove_cards_from_trick(board, trick, 4, 4)
    else:
        if len(trick.cards) == 2:
            _remove_cards_from_trick(board, trick, 1, 2)
        elif len(trick.cards) == 4:
            _remove_cards_from_trick(board, trick, 3, 4)


# TODO refactor
def _undo_subsequent_trick_solo(board):
    trick = board.tricks[-1]
    leader_index = SEATS.index(trick.leader)

    if board.declarer in 'NS' and trick.leader in 'EW':
        if len(trick.cards) == 1:
            _remove_cards_from_trick(board, trick, 1, 1)
            board.tricks = board.tricks[:-1]
            trick = board.tricks[-1]

    if board.declarer in 'NS' and trick.leader in 'EW':
        if len(trick.cards) == 4:
            _remove_cards_from_trick(board, trick, 2, 4)
        elif len(trick.cards) == 3:
            _remove_cards_from_trick(board, trick, 2, 3)
        elif len(trick.cards) == 1:
            _remove_cards_from_trick(board, trick, 1, 1)
            board.tricks = board.tricks[0: -1]
            trick = board.tricks[-1]
            leader_index = SEATS.index(trick.leader)
            _remove_cards_from_trick(board, trick, 4, 4)

    elif board.declarer in 'NS' and trick.leader in 'NS':
        if len(trick.cards) == 2:
            _remove_cards_from_trick(board, trick, 1, 2)
        elif len(trick.cards) == 4:
            _remove_cards_from_trick(board, trick, 3, 4)

    elif board.declarer in 'EW':
        last_card = 4 - leader_index
        _remove_cards_from_trick(board, trick, 1, last_card)
        _remove_current_trick(board, 'solo')


def _undo_subsequent_trick_duo(board):
    trick = board.tricks[-1]
    if trick.leader in 'NS':
        if len(trick.cards) == 4:
            _remove_cards_from_trick(board, trick, 3, 4)
        elif len(trick.cards) == 2:
            _remove_cards_from_trick(board, trick, 1, 2)
            board.tricks = board.tricks[0: -1]
            trick = board.tricks[-1]
            _undo_subsequent_trick_duo(board)

    else:
        if len(trick.cards) == 4:
            _remove_cards_from_trick(board, trick, 4, 4)
        elif len(trick.cards) == 3:
            _remove_cards_from_trick(board, trick, 2, 3)
        elif len(trick.cards) == 1:
            _remove_cards_from_trick(board, trick, 1, 1)
            board.tricks = board.tricks[0: -1]
            trick = board.tricks[-1]
            _undo_subsequent_trick_duo(board)


def _remove_cards_from_trick(board, trick, lower_index, upper_index):
    leader_index = SEATS.index(trick.leader)
    trick.winner = ''
    for seat_index in reversed(range(lower_index, upper_index + 1)):
        player_index = (leader_index + seat_index - 1) % 4
        player_seat = SEATS[player_index]
        card = trick.cards[seat_index - 1]
        trick.cards.remove(card)
        board.hands[player_seat].unplayed_cards.append(card)


def _remove_current_trick(board, mode):
    solo_indexes = {
        'N': (1, 4),
        'E': (4, 4),
        'S': (3, 4),
        'W': (2, 4),
    }
    duo_indexes = {
        'N': (1, 4),
        'E': (4, 4),
        'S': (3, 4),
        'W': (2, 4),
    }
    if mode == 'solo':
        indexes = solo_indexes
    else:
        indexes = duo_indexes
    board.tricks = board.tricks[0: -1]
    trick = board.tricks[-1]

    (lower_index, upper_index) = indexes[trick.leader]
    _remove_cards_from_trick(board, trick, lower_index, upper_index)


def _adjust_score(board):
    # Adjust the score after undo
    board.ns_tricks = 0
    board.ew_tricks = 0
    for trick in board.tricks:
        if trick.winner:
            if trick.winner in 'NS':
                board.ns_tricks += 1
            if trick.winner in 'EW':
                board.ew_tricks += 1
