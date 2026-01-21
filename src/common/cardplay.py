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
    state_context = get_board_context(req, board)
    return merge_context(play_context, **state_context)


def _setup_first_trick(board: Board):
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
    _complete_trick_if_ready(board, update_score=False)

    _apply_played_card(board, req.card_played)

    winner = _complete_trick_if_ready(board, update_score=True)

    save_board(req.room, board)

    trick = board.tricks[-2] if winner else board.get_current_trick()

    trick_context = _build_trick_context(req, board, trick, winner)
    state_context = get_board_context(req, board)

    return merge_context(state_context, **trick_context)


def _build_trick_context(
        req: GameRequest,
        board: Board,
        trick: Trick,
        winner: str | None) -> dict[str, object]:
    return {
        'suggested_card': get_next_card(board, req),
        'trick_leader': trick.leader,
        'trick_suit': _get_trick_suit(trick),
        'trick_cards': [card.name for card in trick.cards],
        'trick_count': len(board.tricks),
        'declarer': board.contract.declarer,
        'winner': winner,
    }


def _complete_trick_if_ready(board: Board, update_score: bool) -> str | None:
    """
        If current trick has 4 cards:
        - completes the trick
        - updates score (optional)
        - advances current_player
        - starts next trick
        Returns the winner seat or None.
    """
    trick = board.get_current_trick()

    if len(trick.cards) != 4:
        return None

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


def _apply_played_card(board: Board, card_played: str) -> bool:
    seat = board.current_player
    if seat not in board.hands:
        return False

    if not card_played:
        return False

    this_card = Card(card_played)
    unplayed_cards = board.hands[seat].unplayed_cards
    trick = board.get_current_trick()

    if this_card not in unplayed_cards:
        return False

    if this_card in trick.cards:
        return False

    trick.cards.append(this_card)
    unplayed_cards.remove(this_card)
    board.current_player = get_current_player(trick)
    return True


def _get_trick_suit(trick: Trick) -> str | None:
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
    board_context = get_board_context(req, board)
    return merge_context(board_context, **{'suggested_card': suggested_card})


def _initialise_board(board: Board) -> None:
    board.tricks = []
    board.NS_tricks = 0
    board.EW_tricks = 0
    for seat in SEATS:
        hand = board.hands[seat]
        hand.unplayed_cards = list(hand.cards)
    _setup_first_trick(board)


def claim_context(req: GameRequest):
    board = _load_board(req)
    old_board = _load_board(req)

    NS_target = _get_NS_target_tricks(board, req)

    total_tricks = board.NS_tricks + board.EW_tricks
    (ns_tricks, ew_tricks) = _play_out_board(board, req.use_double_dummy)
    (board.NS_tricks, board.EW_tricks) = (ns_tricks, ew_tricks)

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

    logger.info(
        'claim',
        username=req.username,
        tricks=req.claim_tricks,
        accepted=accepted)
    state_context = get_board_context(req, board)

    return merge_context(state_context, **claim_context)


def _get_NS_target_tricks(board, req):
    claim_tricks = int(req.claim_tricks)
    if claim_tricks < 0:
        claim_tricks = 13 - board.NS_tricks - board.EW_tricks + claim_tricks
    return board.NS_tricks + claim_tricks


def _play_out_board(
        board: Board, use_double_dummy: bool = False) -> tuple[ int, int]:
    while board.NS_tricks + board.EW_tricks < 13:
        card = next_card(board, use_double_dummy)
        if not card:
            break
        _apply_played_card(board, card.name if card else '')
        _complete_trick_if_ready(board, update_score=True)
    return (board.NS_tricks, board.EW_tricks)


def compare_scores_context(req):
    board = _load_board(req)
    old_board = _load_board(req)

    _initialise_board(board)
    get_board_context(req, board)  # Save the board
    (ns_tricks, ew_tricks) = _play_out_board(board, req.use_double_dummy)

    board = old_board
    state_context = get_board_context(req, board)

    claim_context = {
        'NS_tricks_target': ns_tricks,
        'EW_tricks_target': ew_tricks,
    }

    return merge_context(state_context, **claim_context)
