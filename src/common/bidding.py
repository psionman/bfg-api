"""
Bridge bidding logic for handling bids, auctions, and game context updates.

This module provides functions for processing bids in both solo and duo modes,
updating board state, generating initial auctions, and retrieving bid context.
It interacts with Room and Board models, BiddingBox utilities, and logging.
"""
import structlog

from bridgeobjects import SEATS, Call, Contract, Auction
from bfgbidding import comment_xrefs
from bfgdealer import Board

from common.bidding_box import BiddingBox
from common.models import Room
from common.utilities import (
    get_room_from_name, three_passes, passed_out, get_bidding_data, GameRequest,
    update_user_activity)
from common.constants import SUGGEST_BID_TEXT, YOUR_SELECTION_TEXT, WARNINGS
from common.archive import get_pbn_string
from common.contexts import get_board_context

logger = structlog.get_logger()

CONTRACT_BASE = 6


def get_bid_made(req: GameRequest) -> dict[str, str]:
    """
    Process a bid made by a player and return the updated context.

    Routes to duo or solo bid handling depending on the game mode.
    """
    if req.mode == 'duo':
        return bid_made_duo(req)
    return bid_made_solo(req)


def bid_made_duo(req: GameRequest) -> dict[str, str]:
    """
    Handle a bid made in duo mode and return board and bid context.

    Updates bid history, determines declarer and contract, and updates the
    BiddingBox and board context.
    """
    room = get_room_from_name(req.room_name)
    board = Board().from_json(room.board)

    _get_opps_bid(req, board)

    three_passes_ = three_passes(board.bid_history)
    passed_out_ = passed_out(board.bid_history)
    if three_passes_ and not passed_out_:
        (board.declarer, board.contract) = _get_declarer_contract(board)

    board.warning = req.bid if req.bid in WARNINGS else None
    room.board = board.to_json()
    room.save()

    (bb_names, bb_extra_names) = BiddingBox().refresh(board.bid_history,
                                                      add_warnings=True)
    bidding_params = get_bidding_data(board)

    state_context = get_board_context(req, room, board)
    specific_context = {
        'bid_history': board.bid_history,
        'contract': board.contract.name,
        'declarer': board.declarer,
        'three_passes': three_passes_,
        'passed_out': passed_out_,
        'bid_box_names': bb_names,
        'bid_box_extra_names': bb_extra_names,
        'board_pbn': get_pbn_string(board),
        'contract_target': CONTRACT_BASE + board.contract.level,
        'bidding_params': bidding_params,
    }
    return {**specific_context, **state_context}


def bid_made_solo(req: GameRequest) -> dict[str, str]:
    """
    Handle a bid made in solo mode and return board and bid context.

    Validates the bid, compares with suggested bid, and returns comments
    and strategy text.
    """
    room = get_room_from_name(req.room_name)
    board = Board().from_json(room.board)

    suggested_bid = board.players[req.seat].make_bid(False)
    right_wrong = 'right' if suggested_bid.name == req.bid else 'wrong'
    (bid_comment, strategy_text) = _get_comment_and_strategy(suggested_bid)

    room.own_bid = req.bid
    room.suggested_bid = suggested_bid.name
    room.save()

    state_context = get_board_context(req, room, board)
    bidding_params = get_bidding_data(board)

    specific_context = {
        'selected_bid': req.bid,
        'suggested_bid': suggested_bid.name,
        'right_wrong': right_wrong,
        'bid_comment': bid_comment,
        'strategy_text': strategy_text,
        'bid_made_text': YOUR_SELECTION_TEXT,
        'correct_bid_text': SUGGEST_BID_TEXT,
        'bidding_params': bidding_params,
    }
    return {**specific_context, **state_context}


def _get_opps_bid(req: GameRequest, board: Board) -> None:
    """
    Update the board bid history with the player's bid.

    Also triggers opponent bids unless the board has three consecutive passes.
    """
    bid = req.bid
    if not bid or bid in WARNINGS:
        return

    bid_history = board.bid_history
    bid_history.append(bid)
    board.bid_history = bid_history
    if three_passes(bid_history):
        return

    opp_seat = (SEATS.index(req.seat) + 1) % 4
    board.players[opp_seat].make_bid()


def _get_declarer_contract(board: Board) -> tuple[str, Contract]:
    """
    Determine the declarer and contract from the board's current bid history.

    Sets up the auction object and retrieves contract information.
    """
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
    """
    Retrieve the HTML comment and strategy for a suggested bid.

    Returns default values if the bid does not have a registered comment.
    """
    if suggested_bid.call_id not in comment_xrefs:
        suggested_bid.call_id = '0000'
    suggested_bid.get_comments()
    html_comment = suggested_bid.comment_html
    strategy_html = suggested_bid.strategy_html
    return (html_comment, strategy_html)


def get_initial_auction(req: GameRequest, board: Board, bid_history=None) -> Auction:
    """
    Generate the initial auction for a board and return an Auction object.

    Simulates player bids until the initial board state is complete.
    """
    board.bid_history = bid_history or []
    dealer_index = SEATS.index(board.dealer)
    (seat_diff, mod_value, initial_count) = _get_initial_bid_parameters(
        req, dealer_index)
    while (
            (len(board.bid_history) + seat_diff) % mod_value != initial_count
            and not three_passes(board.bid_history)):
        player_index = (dealer_index + len(board.bid_history)) % 4
        board.players[player_index].make_bid()
    auction_calls = [Call(call) for call in board.bid_history]
    return Auction(auction_calls, board.dealer)


def get_auction(board: Board, bid_history=None) -> Auction:
    """
    Generate the full auction for a board and return an Auction object.

    Simulates player bidding until the board reaches three consecutive passes.
    """
    board.bid_history = bid_history or []
    dealer_index = SEATS.index(board.dealer)
    while not three_passes(board.bid_history):
        player_index = (dealer_index + len(board.bid_history)) % 4
        board.players[player_index].make_bid()
    auction_calls = [Call(call) for call in board.bid_history]
    return Auction(auction_calls, board.dealer)


def _get_initial_bid_parameters(
        req: GameRequest, dealer_index: int) -> tuple[int, int, int]:
    """
    Calculate parameters needed to start the auction.

    Determines seat difference, mod value, and initial bid count based on mode.
    """
    seat_index = SEATS.index(req.seat)

    seat_diff = dealer_index - seat_index - 1

    if req.mode == 'duo':
        initial_count = 1
        mod_value = 2
    else:
        initial_count = 3
        mod_value = 4
    return (seat_diff, mod_value, initial_count)


def get_bid_context(
        req: GameRequest, use_suggested_bid=True) -> dict[str, str]:
    """
    Return the context for the board after a bid has been made.

    Updates bid history, board state, BiddingBox, and returns combined context.
    """
    room = get_room_from_name(req.room_name)
    board = Board().from_json(room.board)
    bid = _update_bid_history(room, board, use_suggested_bid)
    logger.info(
        'bid-made', call=bid, username=req.username, seat=req.seat)
    update_user_activity(req)
    _update_board_other_bids(board, req)
    room.board = board.to_json()
    room.save()

    (bb_names, bb_extra_names) = BiddingBox().refresh(board.bid_history,
                                                      add_warnings=False)

    state_context = get_board_context(req, room, board)
    specific_context = {
        'bid_history': board.bid_history,
        'three_passes': three_passes(board.bid_history),
        'passed_out': passed_out(board.bid_history),
        'bid_box_names': bb_names,
        'bid_box_extra_names': bb_extra_names,
        'contract': board.contract.name,
        'declarer': board.declarer,
        'board_pbn': get_pbn_string(board),
        'contract_target': CONTRACT_BASE + board.contract.level,
    }
    return {**specific_context, ** state_context}


def _update_bid_history(room: Room, board: Board, use_suggested_bid: bool):
    """
    Append the selected bid to the board's bid history.

    Returns the bid used for logging and context updates.
    """
    bid = room.suggested_bid if use_suggested_bid else room.own_bid
    board.bid_history.append(bid)
    return bid


def _update_board_other_bids(board: Board, req: GameRequest) -> None:
    """
    Simulate bids for other players on the board after a player's bid.

    Updates bid history, logs the calls, and recalculates declarer and contract.
    """
    seat_index = SEATS.index(req.seat)
    print(board.bid_history)
    for other in range(3):
        print(other)
        other_seat = (seat_index + 1 + other) % 4
        bid = board.players[other_seat].make_bid()
        logger.info(
            'bid-made',
            call=bid.name,
            username='system',
            seat=SEATS[other_seat])
        three_passes_ = three_passes(board.bid_history)
        passed_out_ = passed_out(board.bid_history)
        if three_passes_ and not passed_out_:
            (board.declarer, board.contract) = _get_declarer_contract(board)
            break
