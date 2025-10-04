from termcolor import cprint

from bridgeobjects import SEATS, Card
from bfgdealer import Board, Trick
from bfgcardplay import next_card

from .utilities import (get_room_from_name, passed_out, save_board,
                        get_current_player)
from .contexts import get_board_context
from .board import update_trick_scores
from .logger import log


ERROR_COLOUR = 'red'


def get_cardplay_context(params: dict[str, str]) -> dict[str, object]:
    """ Return the static context for cardplay."""
    room = get_room_from_name(params.room_name)
    board = Board().from_json(room.board)

    _setup_first_trick(board)

    if passed_out(board.bid_history):
        return {}
    suggested_card = _get_suggested_card_name(board, params)
    trick = board.tricks[-1]

    play_context = {
        'suggested_card': suggested_card,
        'current_player': board.current_player,
        'declarer': board.contract.declarer,
        'trick_cards': [card.name for card in trick.cards],
        'trick_leader': trick.leader,
        'trick_count': len(board.tricks),
    }
    state_context = get_board_context(params, room, board)
    return {**play_context, **state_context}


def _setup_first_trick(board: Board):
    if board.tricks and board.tricks[0].cards:
        return
    trick = board.setup_first_trick_for_board()
    board.tricks = [trick]


def _get_suggested_card_name(board: Board, params: dict) -> str:
    if not board.contract.name:
        return ''
    if not board.tricks[0].cards:
        return next_card(board, params.use_double_dummy).name
    return board.tricks[0].cards[0].name


def card_played_context(params: dict[str, str]) -> dict[str, object]:
    """
        Add a card to the current trick and increment current player.
        if necessary, complete the trick.
    """
    room = get_room_from_name(params.room_name)
    board = Board().from_json(room.board)
    payload = {
        'seat': board.current_player,
        'card': params.card_played,
    }
    log(params.username, 'card played', payload)

    # This section here in case a complete trick is presented by PBN
    winner = _complete_trick(board, False)
    _apply_played_card(board, params)

    # Establish trick_cards and trick_leader because the trick is
    # completed here before the card is displayed in cardplay
    trick = board.get_current_trick()
    trick_cards = [card.name for card in trick.cards]
    trick_leader = trick.leader

    # This section in case this card completes the trick
    winner = _complete_trick(board, True)

    trick_suit = _get_trick_suit(board)
    suggested_card = get_next_card(board, params)
    # Trick count is 1 on the first trick
    # The trick context has to be set here as the
    # # trick is displayed as the next card is suggested.
    trick_context = {
        'suggested_card': suggested_card,
        'trick_leader': trick_leader,
        'trick_suit': trick_suit,
        'trick_cards': trick_cards,
        'trick_count': len(board.tricks),
        'declarer': board.contract.declarer,
        'winner': winner,
    }
    save_board(room, board)  # needed to display all cards with final score
    state_context = get_board_context(params, room, board)
    context = {**state_context, **trick_context}

    return context


def _complete_trick(board: Board, update_score: bool) -> str:
    """complete the trick update the board and return trick winner."""
    trick = board.get_current_trick()
    if len(trick.cards) != 4:
        return None
    trick.complete(board.contract.denomination)
    board.current_player = trick.winner

    if update_score:
        update_trick_scores(board, trick)

    winner = trick.winner
    trick = Trick()
    trick.leader = winner
    board.tricks.append(trick)
    return winner


def _apply_played_card(board: Board, params: dict[str, object]):
    this_card = params.card_played
    trick = board.get_current_trick()
    unplayed_cards = board.hands[board.current_player].unplayed_cards
    if this_card and Card(this_card) in unplayed_cards:
        if Card(this_card) not in trick.cards:
            trick.cards.append(Card(this_card))
        unplayed_cards.remove(Card(this_card))
        board.current_player = get_current_player(trick)


def _get_trick_suit(board: Board) -> str:
    if not board.tricks[-1].suit:
        return None
    return board.tricks[-1].suit.name


def get_next_card(board: Board, params: dict) -> str:
    """Return the selected card for the current_player."""

    if not board.hands[board.current_player].unplayed_cards:
        cprint(f"No cards for player {board.current_player}", ERROR_COLOUR)

    card_to_play = next_card(board, params.use_double_dummy)
    if not card_to_play:
        return 'blank'
    return card_to_play.name


def replay_board_context(params: dict[str, str]) -> dict[str, object]:
    """Return the context for replay board."""
    room = get_room_from_name(params.room_name)
    board = Board().from_json(room.board)
    board.tricks = []
    board.NS_tricks = 0
    board.EW_tricks = 0
    for seat in SEATS:
        hand = board.hands[seat]
        hand.unplayed_cards = [card for card in hand.cards]
    # board.current_player = None
    _setup_first_trick(board)
    suggested_card = _get_suggested_card_name(board, params)
    context = {
        'suggested_card': suggested_card,
    }
    board_context = get_board_context(params, room, board)
    return {**context, **board_context}


def claim_context(params):
    room = get_room_from_name(params.room_name)
    board = Board().from_json(room.board)
    old_board = Board().from_json(room.board)

    NS_target = _get_NS_target_tricks(board, params)

    total_tricks = board.NS_tricks + board.EW_tricks
    (NS_tricks, EW_tricks) = _play_out_board(params, board, total_tricks)
    (board.NS_tricks, board.EW_tricks) = (NS_tricks, EW_tricks)

    if NS_target == board.NS_tricks:
        accepted = True
        board.NS_tricks = NS_target
        board.EW_tricks = 13 - NS_target
    else:
        accepted = False
        board = old_board

    claim_context = {
        'accept_claim': accepted,
    }
    payload = {
        'claim tricks': params.claim_tricks,
        'accepted': accepted
    }
    log(params.username, 'claim', payload)
    state_context = get_board_context(params, room, board)
    context = {**state_context, **claim_context}
    return context


def _get_NS_target_tricks(board, params):
    claim_tricks = int(params.claim_tricks)
    if claim_tricks < 0:
        claim_tricks = 13 - board.NS_tricks - board.EW_tricks + claim_tricks
    return board.NS_tricks + claim_tricks


def _play_out_board(params, board, total_tricks):
    while total_tricks < 13:
        suggested_card = get_next_card(board, params)
        params.card_played = suggested_card
        card_played_context(params)
        room = get_room_from_name(params.room_name)
        board = Board().from_json(room.board)
        total_tricks = board.NS_tricks + board.EW_tricks
    return (board.NS_tricks, board.EW_tricks)


def compare_scores_context(params):
    room = get_room_from_name(params.room_name)
    board = Board().from_json(room.board)
    old_board = Board().from_json(room.board)

    board.tricks = []
    board.get_current_trick()
    board.NS_tricks = 0
    board.EW_tricks = 0
    for seat in SEATS:
        hand = board.hands[seat]
        hand.unplayed_cards = [card for card in hand.cards]
    get_board_context(params, room, board)  # Save the board
    (NS_tricks, EW_tricks) = _play_out_board(params, board, 0)

    board = old_board
    state_context = get_board_context(params, room, board)

    claim_context = {
        'NS_tricks_target': NS_tricks,
        'EW_tricks_target': EW_tricks,
    }

    context = {**state_context, **claim_context}
    return context
