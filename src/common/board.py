"""
Application logic for managing bridge boards, auctions, and game state.

This module provides functions to generate new boards, restart existing boards,
process boards from PBN strings, track bid and trick history, and update the
game context for users. It interacts with common utilities, constants,
contexts, bidding rules, and the archive system.

Functions:
- get_new_board: Create a new board and return its context.
- restart_board_context: Reset a board and return the updated context.
- get_room_board: Retrieve the current state of a board in a room.
- get_history_board: Return a board restored from the archive.
- get_board_from_pbn: Generate a board from a PBN string.
- undo_context: Undo card plays or bids and update context.

This module depends on common modules, bfgdealer, bfgcardplay, bridgeobjects,
and structlog for logging.
"""
import json
import uuid

import structlog
from bfgcardplay import next_card
from bridgeobjects import SEATS, VULNERABILITY, parse_pbn, Auction
from bfgdealer import DealerSolo, DealerDuo, Board, Trick

from common.bidding import get_initial_auction
from common.utilities import (
    get_unplayed_cards_for_board_hands, passed_out,
    GameRequest, get_current_player, merge_context)
from common.contexts import get_board_context
from common.constants import SOURCES, CONTRACT_BASE, Mode
from common.archive import save_board_to_archive, get_board_from_archive
from common.undo_cardplay import undo_cardplay


logger = structlog.get_logger()


def get_new_board(req: GameRequest) -> dict[str, object]:
    """
    Generate a new board and return the full board context.

    Increments the board number for the room, assigns dealer and vulnerability,
    initialises auction, updates user activity, saves the board to archive, and
    returns a dictionary containing the board state and context.
    """
    room = req.room
    room.board_number += 1

    board = _get_new_board(req)
    board.description = str(uuid.uuid1())
    board.vulnerable = VULNERABILITY[room.board_number % 16]
    board.dealer = SEATS[(room.board_number - 1) % 4]
    board.auction = get_initial_auction(req, board, [])
    save_board_to_archive(room, board)

    logger.info(
        'new-board',
        username=req.username,
        pbn=board.create_pbn_list()
        )

    _log_initial_bids(board)

    return get_board_context(req, board)


def _log_initial_bids(board: Board) -> None:
    seat_index = SEATS.index(board.dealer)
    for call in board.auction.calls:
        logger.info(
            'bid-made',
            call=call.name,
            username='system',
            seat=SEATS[seat_index])
        seat_index += 1
        seat_index %= 4


def restart_board_context(req: GameRequest) -> dict:
    """
    Reset an existing board for a room and return the updated board context.

    Clears previous tricks, resets auctions and current player, and refreshes
    unplayed cards for all hands. Returns a dictionary representing the current
    board context.
    """
    board = Board().from_json(req.room.board)
    board.tricks = [Trick()]
    board.auction = Auction()
    board.auction = get_initial_auction(req, board, [])
    board.current_player = None
    board.NS_tricks, board.EW_tricks = 0, 0

    for hand in board.hands.values():
        hand.unplayed_cards = list(hand.cards)

    for trick in board.tricks:
        trick.cards = []

    return get_board_context(req, board)


def _get_new_board(req: GameRequest) -> Board:
    """
    Select the appropriate new board based on provided parameters.

    Returns a random board or a set board depending on 'set_hands' and
    'use_set_hands' flags.
    """
    if not req.set_hands:
        return _get_random_board()
    if req.use_set_hands:
        return _get_set_hand(req)
    return _get_random_board()


def _get_set_hand(req: GameRequest) -> Board:
    """
    Generate a board from a pre-set hand for a room.

    Uses dealer engine and sets the board's source to 'set-hands'.
    """
    room = req.room
    set_hands = json.loads(room.set_hands)

    (dealer_engine, dealer) = _get_dealer_engine(req, room.board_number)
    board = dealer_engine.get_set_hand(set_hands, dealer)
    board.source = SOURCES['set-hands']
    _set_board_hands(board)
    return board


def _get_dealer_engine(req: GameRequest,
                       board_number: int) -> tuple[object, str]:
    """
    Return the dealer engine and dealer seat for a board.

    Chooses between DealerSolo and DealerDuo depending on the game mode.
    """
    if req.mode == Mode.DUO:
        dealer = SEATS[board_number % 4]
        dealer_engine = DealerDuo(dealer)
    else:
        dealer = 'N'
        dealer_engine = DealerSolo(dealer)
    return (dealer_engine, dealer)


def _set_board_hands(board: Board) -> None:
    """
    Assign the dealt hands to each player on the board.
    """
    for index in range(4):
        board.players[index].hand = board.hands[index]


def _get_random_board() -> Board:
    """
    Generate a random board and assign it to the players.

    Uses DealerDuo for dealing and marks the board source as 'random'.
    """
    # Doesn't matter whether we use DealerSolo or DealerDuo
    board = DealerDuo().deal_random_board()
    board.set_hand = None
    board.source = SOURCES['random']
    _set_board_hands(board)
    return board


def get_room_board(req: GameRequest) -> dict[str, object]:
    """
    Return the full context of the current board in a room.

    Includes bid history, contract, tricks, stage, and other relevant state.
    """
    room = req.room
    board = Board().from_json(room.board)

    return _room_board_context(req, board)


def _room_board_context(req: GameRequest, board: Board) -> dict[str, object]:

    state_context = get_board_context(req, board)
    (trick_cards, trick_leader, trick_suit) = _mutate_trick_state(board)

    specific_context = {
        'bid_history': board.bid_history,
        'warning': board.warning,
        'passed_out': passed_out(board.bid_history),
        'contract': board.contract.name,
        'declarer': board.contract.declarer,
        'trick_cards': trick_cards,
        'trick_leader': trick_leader,
        'trick_suit': trick_suit,
        'identifier': board.identifier,
        'trick_count': len(board.tricks),
        'stage': board.stage,
        'source': board.source,
        'contract_target': CONTRACT_BASE + board.contract.level,
    }
    return merge_context(state_context, **specific_context)


def _mutate_trick_state(board: Board) -> tuple[list, str, str]:
    """Assign trick cards in case that new trick has no cards yet."""
    (trick_cards, trick_leader, trick_suit) = _get_trick_details(board)
    if not trick_cards and len(board.tricks) > 1:
        trick_cards = [card.name for card in board.tricks[-2].cards]
        trick_leader = board.tricks[-2].leader
    return (trick_cards, trick_leader, trick_suit)


def _get_trick_details(board: Board) -> tuple[list[str], str, str]:
    """
    Retrieve details of the last trick for a board.

    Returns the trick cards, leader, and suit if available.
    """
    trick_cards, trick_leader, trick_suit = [], '', ''
    if not board.tricks:
        return (trick_cards, trick_leader, trick_suit)

    if board.tricks[-1].cards:
        trick_cards = [card.name for card in board.tricks[-1].cards]
        trick_leader = board.tricks[-1].leader
        trick_suit = board.tricks[-1].suit.name
    elif len(board.tricks) > 1:
        if board.tricks[-1].leader:
            trick_leader = board.tricks[-1].leader
        else:
            trick_leader = board.tricks[-2].leader
    return (trick_cards, trick_leader, trick_suit)


def get_history_board(req: GameRequest) -> dict[str, object]:
    """
    Return a board restored from the archive for a room and update context.

    Restores bid history, auction, and logs the event.
    """
    board = get_board_from_archive(req)

    # board.display_stats()

    board.auction = get_initial_auction(req, board, [])
    board.source = SOURCES['history']

    logger.info(
        'history-board',
        username=req.username,
        pbn=board.create_pbn_list())
    return get_board_context(req, board)


def get_board_from_pbn(req: GameRequest) -> dict[str, object]:
    """
    Generate a board from a PBN string and return its context.

    Updates unplayed cards, assigns source as 'pbn', and logs the board.
    """
    board = _get_board_from_pbn_string(req)
    if not board:
        return {'error': 'Invalid pbn string'}

    board.source = SOURCES['pbn']
    get_unplayed_cards_for_board_hands(board)
    logger.info(
        'pbn-board',
        username=req.username,
        pbn=board.create_pbn_list()
    )
    _update_room_for_pbn(req)

    return _get_context_for_pbn_board(req, board)


def _update_room_for_pbn(req: GameRequest) -> None:
    room = req.room
    room.saved_pbn = req.pbn_text
    room.save()


def _get_context_for_pbn_board(
        req: GameRequest, board: Board) -> dict[str, object]:
    trick_context = _trick_context_for_pbn_board(board)
    board_context = get_board_context(req, board)
    return merge_context(board_context, **trick_context)


def _trick_context_for_pbn_board(board: Board) -> dict[str, str]:
    """
    Initialise trick context for a PBN board.

    Creates the first trick if none exist and provides suggested card.
    """
    if not board.tricks:
        trick = board.setup_first_trick_for_board()
        board.tricks.append(trick)
    trick_context = _apply_initial_cards(board)

    if suggested_card := next_card(board):
        trick_context['suggested_card'] = suggested_card.name
    return trick_context


def _apply_initial_cards(board: Board) -> dict[str, str]:
    """
    Play the initial cards on a board and update trick context.

    Updates current player, completes tricks, and calculates trick scores.
    """
    trick_context = {}
    board.current_player = _get_leader(board.contract.declarer)
    for trick in board.tricks:
        if trick.cards:
            trick_context = _trick_context(trick)
            board.current_player = get_current_player(trick)

            update_trick_scores(board, trick)
        if len(trick.cards) == 4:
            trick.complete(board.contract.denomination)
            board.current_player = trick.winner
    return trick_context


def _trick_context(trick: Trick) -> dict[str, object]:
    """
    Extract trick leader, suit, and card names for a trick.
    """
    if not trick.cards:
        return {}
    return {
        'trick_leader': trick.leader,
        'trick_suit': trick.suit.name,
        'trick_cards': [card.name for card in trick.cards],
    }


def _get_board_from_pbn_string(req: GameRequest) -> Board | None:
    """
    Parse a PBN string and return a Board object.

    Handles line breaks, invalid boards, and restores auction and unplayed
    cards.
    """
    board = _parse_pbn_text(req)
    if not board:
        return None
    _mutate_board_auction(req, board)
    get_unplayed_cards_for_board_hands(board)
    return board


def _mutate_board_auction(req: GameRequest, board: Board) -> None:
    bid_history = [call.name for call in board.auction.calls]
    board.bid_history = bid_history

    # This is necessary because the contract gets
    # lost after the call to get_initial_auction
    contract = board._contract
    board.auction = get_initial_auction(req, board, bid_history=bid_history)
    board.contract = contract


def _parse_pbn_text(req: GameRequest) -> Board | None:
    pbn_list = _get_pbn_list(req)

    if not pbn_list:
        return None
    try:
        raw_board = parse_pbn(pbn_list)[0].boards[0]
    except (ValueError, IndexError):
        return None

    board = Board()
    board.get_attributes_from_board(raw_board)
    return board


def _get_pbn_list(req: GameRequest) -> list[str]:
    pbn_list = []
    if '\n' in req.pbn_text:
        pbn_list_raw = (req.pbn_text).split('\n')
        pbn_list.extend(item.replace('<br>', '').strip()
                        for item in pbn_list_raw)
    elif '<br>' in req.pbn_text:
        pbn_list_raw = (req.pbn_text).split('<br>')
        pbn_list.extend(item.strip() for item in pbn_list_raw)
    return pbn_list


def _get_leader(declarer: str) -> str:
    """
    Determine the next leader for a board based on the declarer.
    """
    if not declarer:
        return ''
    seat_index = SEATS.index(declarer)
    leader_index = (seat_index + 1) % 4
    return SEATS[leader_index]


def update_trick_scores(board: Board, trick: Trick):
    """
    Update NS and EW trick counts for a board based on the last trick winner.
    """
    if not trick.winner:
        return
    if trick.winner in 'NS':
        board.NS_tricks += 1
    elif trick.winner in 'EW':
        board.EW_tricks += 1


def undo_context(req: GameRequest) -> dict[str, object]:
    """
    Undo the last card play or bid and return the updated board context.

    Updates the auction, bid history, current player, and user activity.
    """
    board = Board().from_json(req.room.board)

    if board.contract.name:
        initial_state = _undo_card_play(req, board)
    else:
        initial_state = _undo_bidding(req, board)

    context = get_board_context(req, board)
    context['initial_state'] = initial_state
    return context


def _undo_card_play(req: GameRequest, board: Board) -> bool:
    undo_cardplay(board, req.mode)
    board.current_player = get_current_player(board.tricks[-1])
    logger.info('undo-card', username=req.username)
    return False


def _undo_bidding(req: GameRequest, board: Board) -> bool:
    new_bid_history = _undo_bids(board, req)
    auction = get_initial_auction(req, board, [])

    # Restore bid_history after "get_initial_auction()"
    board.bid_history = new_bid_history

    logger.info('undo-bid', username=req.username)

    calls = [call.name for call in auction.calls]
    if calls == board.bid_history:
        return True
    return False


def _undo_bids(board, req: GameRequest) -> list:
    """
    Undo a sequence of bids until reaching the specified bidder seat.

    Restores the board to the previous auction state if necessary.
    """
    bid_history = list(board.bid_history)
    bidder_seat_index = SEATS.index(board.dealer) + len(board.bid_history) - 1
    bidder_seat_index %= 4

    while bidder_seat_index != SEATS.index(req.seat):
        bid_history.pop(-1)
        bidder_seat_index -= 1
        bidder_seat_index %= 4

    if bid_history:
        bid_history.pop(-1)

    return list(bid_history) or [
        call.name for call in get_initial_auction(req, board).calls]
