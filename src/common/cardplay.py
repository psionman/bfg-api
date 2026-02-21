"""
Cardplay context module for bridge game backend.

Provides functions to:
- Load board state from a request
- Generate context for cardplay, trick updates, and board replay
- Handle claims and compare scores
- Suggest next card using AI or double-dummy logic

Dependencies:
- bridgeobjects, bfgdealer, bfgcardplay
- common.utilities, common.contexts, common.board
"""

import structlog

from bridgeobjects import SEATS, Card
from bfgdealer import Board, Trick
from bfgcardplay import next_card

from common.utilities import (
    passed_out, save_board, get_current_player, GameRequest, merge_context)
from common.contexts import get_board_context
from common.board import update_trick_scores

logger = structlog.get_logger()


def _load_board(req: GameRequest) -> Board:
    return Board().from_json(req.room.board)


def _clone_board(board: Board) -> Board:
    return Board().from_json(board.to_json())


def get_cardplay_context(req: GameRequest) -> dict[str, object]:
    """ Return the static context for cardplay."""
    board = _load_board(req)

    _setup_first_trick(board)

    if passed_out(board.bid_history):
        return {}

    suggested_card = _get_suggested_card_name(board, req)
    trick = board.tricks[-1]

    play_context = {
        'suggested_card': suggested_card,
        'current_player': board.current_player,
        'declarer': board.contract.declarer,
        'trick_cards': [card.name for card in trick.cards],
        'trick_leader': trick.leader,
        'trick_count': len(board.tricks),
    }
    # state_context = get_board_context(req, board)
    # return merge_context(play_context, **state_context)
    return _with_state_context(req, board, play_context)


def _setup_first_trick(board: Board) -> None:
    if board.tricks and board.tricks[0].cards:
        return
    trick = board.setup_first_trick_for_board()
    board.tricks = [trick]


def _get_suggested_card_name(board: Board, req: GameRequest) -> str:
    if not board.contract.name:
        return ''

    if not board.tricks[0].cards:
        card = next_card(board, req.use_double_dummy)
        return card.name if card else ''

    return board.tricks[0].cards[0].name


def card_played_context(req: GameRequest) -> dict[str, object]:
    """
        Add a card to the current trick and increment current player.
        if necessary, complete the trick.
    """
    board = _load_board(req)

    logger.info(
        'card-played',
        card=req.card_played,
        username=req.card_player,
        seat=board.current_player,
    )

    # Handle pre-filled trick (e.g. PBN)
    winner = False
    if _is_trick_complete(board.get_current_trick()):
        winner = _finalize_trick(board, update_score=True)

    _play_card_if_valid(board, req.card_played)

    if _is_trick_complete(board.get_current_trick()):
        winner = _finalize_trick(board, update_score=True)

    save_board(req.room, board)

    trick = board.tricks[-2] if winner else board.get_current_trick()

    trick_state = _build_trick_context(req, board, trick, winner)
    return _with_state_context(req, board, trick_state)


def _build_trick_context(
        req: GameRequest,
        board: Board,
        trick: Trick,
        winner: str | None) -> dict[str, object]:
    return {
        'suggested_card': get_next_card(board, req),
        'trick_leader': trick.leader,
        'trick_suit': _get_trick_suit(board),
        'trick_cards': [card.name for card in trick.cards],
        'trick_count': len(board.tricks),
        'declarer': board.contract.declarer,
        'winner': winner,
    }


def _is_trick_complete(trick: Trick) -> bool:
    return len(trick.cards) == 4


def _finalize_trick(board: Board, update_score: bool) -> str | None:
    """
        - completes the trick
        - updates score (optional)
        - advances current_player
        - starts next trick
        Returns the winner seat or None.
    """
    trick = board.get_current_trick()

    trick.complete(board.contract.denomination)
    board.current_player = trick.winner

    if update_score:
        update_trick_scores(board, trick)

    _start_next_trick(board, leader=trick.winner)
    return trick.winner


def _start_next_trick(board: Board, leader: str) -> None:
    next_trick = Trick()
    next_trick.leader = leader
    board.tricks.append(next_trick)


def _can_play_card(board: Board, card: Card) -> bool:
    seat = board.current_player
    if seat not in board.hands:
        return False
    if card not in board.hands[seat].unplayed_cards:
        return False
    if card in board.get_current_trick().cards:
        return False
    return True


def _play_card(board: Board, card: Card) -> None:
    trick = board.get_current_trick()
    trick.cards.append(card)
    board.hands[board.current_player].unplayed_cards.remove(card)
    board.current_player = get_current_player(trick)


def _play_card_if_valid(board: Board, card_played: str) -> bool:
    card = Card(card_played)
    if not _can_play_card(board, card):
        return False

    _play_card(board, card)
    return True


def _get_trick_suit(board: Board) -> str | None:
    trick = board.tricks[-1]
    return trick.suit.name if trick.suit else None


def get_next_card(board: Board, req: GameRequest) -> str:
    """Return the selected card for the current_player."""

    if board.current_player not in board.hands:
        return ''

    if not board.hands[board.current_player].unplayed_cards:
        logger.error('no-unplayed-cards', player=board.current_player,)
        return ''

    card_to_play = next_card(board, req.use_double_dummy)
    if not card_to_play:
        return 'blank'
    return card_to_play.name


def replay_board_context(req: GameRequest) -> dict[str, object]:
    """Return the context for replay board."""
    board = _load_board(req)
    _initialise_board(board)
    suggested_card = _get_suggested_card_name(board, req)
    # board_context = get_board_context(req, board)
    # return merge_context(board_context, **{'suggested_card': suggested_card})
    return _with_state_context(req, board, {'suggested_card': suggested_card})


def _initialise_board(board: Board) -> None:
    board.tricks = []
    board.NS_tricks = 0
    board.EW_tricks = 0
    for seat in SEATS:
        hand = board.hands[seat]
        hand.unplayed_cards = list(hand.cards)
    _setup_first_trick(board)


def claim_context(req: GameRequest) -> dict[str, object]:
    board = _load_board(req)
    snapshot = _clone_board(board)

    ns_target = _get_ns_target_tricks(board, req)

    (ns_tricks, ew_tricks) = _auto_play_remaining_tricks(
        board, req.use_double_dummy)
    (board.NS_tricks, board.EW_tricks) = (ns_tricks, ew_tricks)

    accepted = ns_tricks == ns_target

    if accepted:
        board.NS_tricks = ns_target
        board.EW_tricks = 13 - ns_target
    else:
        board = snapshot

    logger.info(
        'claim',
        username=req.username,
        claimed=req.claim_tricks,
        estimated=ns_tricks,
        accepted=accepted)
    return _with_state_context(req, board, {'accept_claim': accepted})


def _get_ns_target_tricks(board, req) -> int:
    claim_tricks = int(req.claim_tricks)
    if claim_tricks < 0:
        claim_tricks = 13 - board.NS_tricks - board.EW_tricks + claim_tricks
    return board.NS_tricks + claim_tricks


def _auto_play_remaining_tricks(
        board: Board, use_double_dummy: bool = False) -> tuple[int, int]:
    while board.NS_tricks + board.EW_tricks < 13:
        card = next_card(board, use_double_dummy)
        if not card:
            break
        _play_card_if_valid(board, card.name if card else '')
        if _is_trick_complete(board.get_current_trick()):
            _finalize_trick(board, update_score=True)
    return (board.NS_tricks, board.EW_tricks)


def compare_scores_context(req) -> dict[str, object]:
    board = _load_board(req)
    snapshot = _clone_board(board)

    _initialise_board(board)
    # get_board_context(req, board)  # Save the board
    (ns_tricks, ew_tricks) = _auto_play_remaining_tricks(
        board, req.use_double_dummy)

    board = snapshot
    # state_context = get_board_context(req, board)

    claim_result = {
        'ns_tricks_target': ns_tricks,
        'ew_tricks_target': ew_tricks,
    }

    # return merge_context(state_context, **claim_result)
    return _with_state_context(req, board, claim_result)


def _with_state_context(
        req: GameRequest, board: Board, extra) -> dict[str, object]:
    return merge_context(get_board_context(req, board), **extra)
