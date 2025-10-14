from bridgeobjects import SUITS, SEATS, Hand
from bfgdealer import Board
from common.bidding_box import BiddingBox

from .archive import get_pbn_string
from .constants import DEFAULT_SUIT_ORDER
from .utilities import save_board, three_passes, passed_out


def get_board_context(params, room, board) -> dict[str, str]:
    context = _board_context(params, room, board)
    save_board(room, board)
    return context


def _board_context(params, room, board) -> dict[str, str]:
    bb_context = _get_bb_context(params.mode, board)
    board_context = _get_board_context(board, room.board_number)
    return {**board_context, **bb_context}


def _get_bb_context(mode: str, board: Board) -> dict[str, str]:
    add_warnings = False
    if mode == 'duo':
        add_warnings = True

    (bb_names, bb_extra_names) = BiddingBox().refresh(board.bid_history,
                                                      add_warnings)
    bb_context = {
        'bid_box_names': bb_names,
        'bid_box_extra_names': bb_extra_names,
    }
    return bb_context


def _get_board_context(board: Board, board_number: int) -> dict[str, object]:
    """Return a context with the current state of the board."""
    # The trick context cannot be set here (see card_played))
    suit_order = _get_suit_order(board)
    trick_suit = ''
    if board.tricks and board.tricks[-1].suit:
        trick_suit = board.tricks[-1].suit.name

    context = {
        'dealer': board.dealer,
        'bid_history': board.bid_history,
        'board_number': board_number,
        'vulnerable': board.vulnerable,
        'suit_order': suit_order,
        'hand_cards': _sort_hand_cards(board),
        'unplayed_card_names': _unplayed_card_names(board),
        'max_suit_length': _max_suit_length(board),
        'hand_suit_length': _hand_suit_length(board),
        'current_player': board.current_player,
        'previous_player': _get_previous_player(board),
        'tricks': [
            [card.name for card in trick.cards] for trick in board.tricks
            ],
        'tricks_leaders': [trick.leader for trick in board.tricks],
        'trick_count': len(board.tricks),
        'trick_suit': trick_suit,
        'NS_tricks': board.NS_tricks,
        'EW_tricks': board.EW_tricks,
        'score': _get_score(board),
        'dummy': _get_dummy_seat(board),
        'board_pbn': get_pbn_string(board),
        'three_passes': three_passes(board.bid_history),
        'passed_out': passed_out(board.bid_history),
        'contract': board.contract.name,
        'contract_target': 6 + board.contract.level,
        'makeable_tricks': board.makeable_tricks,
        'declarer': board.declarer,
        'stage': board.stage,
        'source': board.source,
        'identifier': board.identifier,
        'test': False,
    }
    return context


def _get_suit_order(board: Board) -> list[str]:  # X
    """Return a list of suit order."""
    if three_passes(board.bid_history):
        bid_history = board.bid_history[:-3]
        while bid_history and bid_history[-1] in ['D', 'R']:
            bid_history = board.bid_history[:-1]
        contract_suit_name = bid_history[-1]
        suit = contract_suit_name[-1]
        if suit in DEFAULT_SUIT_ORDER:
            if suit == 'S':
                return DEFAULT_SUIT_ORDER
            if suit == 'H':
                return ['H', 'S', 'D', 'C']
            if suit == 'D':
                return ['D', 'S', 'H', 'C']
            if suit == 'C':
                return ['C', 'H', 'S', 'D']
        else:
            return DEFAULT_SUIT_ORDER
    else:
        return DEFAULT_SUIT_ORDER


def _sort_hand_cards(board: Board) -> list[str]:
    hands = []
    hand_cards = []
    suit_order = _get_suit_order(board)
    for index in range(4):
        hand = str(board.hands[index])
        new_hand = hand.replace('Hand(', '').replace(')', '')
        hands.append(new_hand.replace('"', ''))
        sorted_hand = Hand.sort_card_list(board.hands[index].cards, suit_order)
        hand_cards.append([card.name for card in sorted_hand])
    return hand_cards


def _unplayed_card_names(board: Board) -> dict[str, str]:
    unplayed_card_names = {}
    suit_order = _get_suit_order(board)
    for seat in SEATS:
        hand = board.hands[seat]
        hand_for_shape = Hand(hand.unplayed_cards)
        hand_for_shape.cards = [card for card in hand.unplayed_cards]
        unplayed = Hand.sort_card_list(hand_for_shape.cards, suit_order)
        unplayed_card_names[seat] = [card.name for card in unplayed]
    return unplayed_card_names


def _max_suit_length(board: Board) -> dict[str, int]:
    max_suit_length = {}
    for seat in SEATS:
        hand = board.hands[seat]
        hand_for_shape = Hand(hand.unplayed_cards)
        hand_for_shape.cards = [card for card in hand.unplayed_cards]
        max_suit_length[seat] = hand_for_shape.shape[0]
    return max_suit_length


def _hand_suit_length(board: Board) -> dict[str, int]:
    hand_suit_length = {}
    suits = _suits_by_order(board)
    for seat in SEATS:
        hand = board.hands[seat]
        hand_for_shape = Hand(hand.unplayed_cards)
        hand_for_shape.cards = [card for card in hand.unplayed_cards]
        hand_suit_length[seat] = [hand_for_shape.suit_length(suit)
                                  for suit in suits]
    return hand_suit_length


def _get_previous_player(board: Board) -> str:
    """Get previous player and allow for the fact that
        trick has been created before last card updated
    """
    if not board.current_player:
        return None
    previous_player_index = SEATS.index(board.tricks[-1].leader)
    if board.tricks[-1].cards:
        current_player_index = SEATS.index(board.current_player)
        previous_player_index = (current_player_index - 1) % 4
    elif len(board.tricks) > 1:
        leader_index = SEATS.index(board.tricks[-2].leader)
        previous_player_index = (leader_index - 1) % 4
    previous_player = SEATS[previous_player_index]
    return previous_player


def _get_score(board: Board) -> int:
    if board.NS_tricks + board.EW_tricks == 13:
        return _calculate_score(board)
    return 0


def _get_dummy_seat(board: Board) -> str | None:
    if not board.declarer:
        return None
    declarer_index = SEATS.index(board.declarer)
    dummy_index = (declarer_index + 2) % 4
    return SEATS[dummy_index]


def _suits_by_order(board: Board) -> list[str]:
    suit_order = _get_suit_order(board)
    suits = [SUITS[suit_name] for suit_name in suit_order]
    return suits


def _calculate_score(board: Board) -> int:
    """Return the score for the board."""
    vulnerable = False
    if board.contract.declarer in 'NS':
        declarers_tricks = board.NS_tricks
        if board.vulnerable in ['NS', 'Both', 'All']:
            vulnerable = True
    else:
        declarers_tricks = board.EW_tricks
        if board.vulnerable in ['EW', 'Both', 'All']:
            vulnerable = True
    return board.contract.score(declarers_tricks, vulnerable)
