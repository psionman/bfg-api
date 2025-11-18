
import structlog

from bridgeobjects import SEATS, Call, Contract, Auction
from bfgbidding import comment_xrefs
from bfgdealer import Board

from .bidding_box import BiddingBox
from .models import Room
from .utilities import get_room_from_name, three_passes, passed_out
from .constants import SUGGEST_BID_TEXT, YOUR_SELECTION_TEXT, WARNINGS
from .archive import get_pbn_string
from .contexts import get_board_context

logger = structlog.get_logger()


def get_bid_made(params: dict[str, str]) -> dict[str, str]:
    if params.bid == 'restart':
        logger.info('Clicked restart board', username=params.username)
        return _restart_board(params)
    elif params.mode == 'duo':
        return bid_made_duo(params)
    return bid_made_solo(params)


def bid_made_duo(params: dict[str, str]) -> dict[str, str]:
    """Return a list of bid images after a call has been made."""
    room = get_room_from_name(params.room_name)
    board = Board().from_json(room.board)

    # Bid gets appended to bid_history here
    _get_opps_bid(params, board)

    three_passes_ = three_passes(board.bid_history)
    passed_out_ = passed_out(board.bid_history)
    if three_passes_ and not passed_out_:
        (board.declarer, board.contract) = _get_declarer_contract(board)

    board.warning = params.bid if params.bid in WARNINGS else None
    room.board = board.to_json()
    room.save()

    (bb_names, bb_extra_names) = BiddingBox().refresh(board.bid_history,
                                                      add_warnings=True)
    state_context = get_board_context(params, room, board)
    specific_context = {
        'bid_history': board.bid_history,
        'contract': board.contract.name,
        'declarer': board.declarer,
        'three_passes': three_passes,
        'passed_out': passed_out,
        'bid_box_names': bb_names,
        'bid_box_extra_names': bb_extra_names,
        'board_pbn': get_pbn_string(board),
        'contract_target': 6 + board.contract.level,
    }
    return {**specific_context, **state_context}


def bid_made_solo(params: dict[str, str]) -> dict[str, str]:
    """Validate bid made and update show comment etc.."""
    room = get_room_from_name(params.room_name)
    board = Board().from_json(room.board)

    suggested_bid = board.players[params.seat].make_bid(False)
    right_wrong = 'right' if suggested_bid.name == params.bid else 'wrong'
    (bid_comment, strategy_text) = _get_comment_and_strategy(suggested_bid)

    room.own_bid = params.bid
    room.suggested_bid = suggested_bid.name
    room.save()

    state_context = get_board_context(params, room, board)
    specific_context = {
        'selected_bid': params.bid,
        'suggested_bid': suggested_bid.name,
        'right_wrong': right_wrong,
        'bid_comment': bid_comment,
        'strategy_text': strategy_text,
        'bid_made_text': YOUR_SELECTION_TEXT,
        'correct_bid_text': SUGGEST_BID_TEXT,
    }
    return {**specific_context, **state_context}


def _restart_board(params):
    """Return the context for a restart board."""
    room = get_room_from_name(params.room_name)
    board = Board().from_json(room.board)
    board.auction = Auction()
    board.auction = get_initial_auction(params, board, [])
    board.current_player = None
    return get_board_context(params, room, board)


def _get_opps_bid(params: dict[str, str], board: Board) -> None:
    """Update the board bid history with the bid."""
    bid = params.bid
    if not bid or bid in WARNINGS:
        return

    bid_history = board.bid_history
    bid_history.append(bid)
    board.bid_history = bid_history
    if three_passes(bid_history):
        return

    opp_seat = (SEATS.index(params.seat) + 1) % 4
    board.players[opp_seat].make_bid()


def _get_declarer_contract(board: Board) -> tuple[str, Contract]:
    (declarer, contract) = ('', '')
    if board.bid_history[-4] == 'P':
        del board.bid_history[-1]
    calls = [Call(bid) for bid in board.bid_history]
    board.auction = Auction(calls, board.dealer)
    board.get_contract()
    contract = board.contract
    declarer = board.contract.declarer
    return (declarer, contract)


def _get_comment_and_strategy(suggested_bid):
    """Retrieve bid comment and strategy text."""
    if suggested_bid.call_id not in comment_xrefs:
        suggested_bid.call_id = '0000'
    suggested_bid.get_comments()
    html_comment = suggested_bid.comment_html
    strategy_html = suggested_bid.strategy_html
    return (html_comment, strategy_html)


def get_initial_auction(params: dict[str, str],
                        board: Board, bid_history=None) -> Auction:
    """Return initial bid_history."""
    board.bid_history = bid_history or []
    dealer_index = SEATS.index(board.dealer)
    (seat_diff, mod_value, initial_count) = _get_initial_bid_parameters(
        params, dealer_index)
    while (
            (len(board.bid_history) + seat_diff) % mod_value != initial_count
            and not three_passes(board.bid_history)):
        player_index = (dealer_index + len(board.bid_history)) % 4
        board.players[player_index].make_bid()
    auction_calls = [Call(call) for call in board.bid_history]
    return Auction(auction_calls, board.dealer)


def get_auction(board: Board, bid_history=None) -> Auction:
    """Return initial bid_history."""
    board.bid_history = bid_history or []
    dealer_index = SEATS.index(board.dealer)
    while not three_passes(board.bid_history):
        player_index = (dealer_index + len(board.bid_history)) % 4
        board.players[player_index].make_bid()
    auction_calls = [Call(call) for call in board.bid_history]
    return Auction(auction_calls, board.dealer)


def _get_initial_bid_parameters(params: dict[str, str],
                                dealer_index: int) -> tuple[int, int, int]:
    seat_index = SEATS.index(params.seat)

    # seat_diff represents the number of bids that are
    # required given the dealer and seat
    seat_diff = dealer_index - seat_index - 1

    # mod_value depends on whether there is one player or two
    if params.mode == 'duo':
        initial_count = 1
        mod_value = 2
    else:
        initial_count = 3
        mod_value = 4
    return (seat_diff, mod_value, initial_count)


def get_bid_context(params: dict[str, str],
                    use_suggested_bid=True) -> dict[str, str]:
    """Return context after use a bid."""
    room = get_room_from_name(params.room_name)
    board = Board().from_json(room.board)
    bid = _update_bid_history(room, board, use_suggested_bid)
    logger.info(
        'bid made', call=bid, username=params.username, seat=params.seat)
    _update_board_other_bids(board, params)
    room.board = board.to_json()
    room.save()

    (bb_names, bb_extra_names) = BiddingBox().refresh(board.bid_history,
                                                      add_warnings=False)

    state_context = get_board_context(params, room, board)
    specific_context = {
        'bid_history': board.bid_history,
        'three_passes': three_passes(board.bid_history),
        'passed_out': passed_out(board.bid_history),
        'bid_box_names': bb_names,
        'bid_box_extra_names': bb_extra_names,
        'contract': board.contract.name,
        'declarer': board.declarer,
        'board_pbn': get_pbn_string(board),
        'contract_target': 6 + board.contract.level,
    }
    return {**specific_context, ** state_context}


def _update_bid_history(room: Room, board: Board, use_suggested_bid: bool):
    bid = room.suggested_bid if use_suggested_bid else room.own_bid
    board.bid_history.append(bid)
    return bid


def _update_board_other_bids(board: Board, params: dict) -> None:
    seat_index = SEATS.index(params.seat)

    for other in range(3):
        other_seat = (seat_index + 1 + other) % 4
        bid = board.players[other_seat].make_bid()
        logger.info(
            'bid made',
            call=bid.name,
            username='system',
            seat=SEATS[other_seat])
        three_passes_ = three_passes(board.bid_history)
        passed_out_ = passed_out(board.bid_history)
        if three_passes_ and not passed_out_:
            (board.declarer, board.contract) = _get_declarer_contract(board)
            break
