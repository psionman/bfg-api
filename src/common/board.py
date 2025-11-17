import json
import structlog

from bfgcardplay import next_card
from bridgeobjects import SEATS, VULNERABILITY, parse_pbn
from bfgdealer import DealerSolo, DealerDuo, Board, Trick

from .bidding import get_initial_auction
from .utilities import (get_unplayed_cards_for_board_hands, get_room_from_name,
                        passed_out, get_current_player)
from .contexts import get_board_context, get_pbn_string
from .constants import SOURCES, CONTRACT_BASE
from .archive import save_board_to_archive, get_board_from_archive
from .undo_cardplay import undo_cardplay

logger = structlog.get_logger()


def get_new_board(params: dict[str, str]) -> dict[str, object]:
    """Return the context after a new board has been generated."""
    room = get_room_from_name(params.room_name)
    room.board_number += 1
    board = _get_new_board(params)
    board.vulnerable = VULNERABILITY[room.board_number % 16]
    board.dealer = SEATS[(room.board_number - 1) % 4]

    board.display_stats()

    board.auction = get_initial_auction(params, board, [])
    save_board_to_archive(room, board)
    logger.info('New board clicked', user=params.username)
    seat_index = SEATS.index(board.dealer)
    for call in board.auction.calls:
        logger.info(f'<{SEATS[seat_index]}> bid made: {call.name}')
        seat_index += 1
        seat_index %= 4
    return get_board_context(params, room, board)


def _get_new_board(params: dict[str, str]) -> tuple[int, Board]:
    if params.use_set_hands:
        return _get_set_hand(params)
    return _get_random_board(params)


def _get_set_hand(params: dict[str, str]) -> tuple[Board, int]:
    """Return a set_hand."""
    room = get_room_from_name(params.room_name)
    set_hands = json.loads(room.set_hands)

    (dealer_engine, dealer) = _get_dealer_engine(params, room.board_number)
    board = dealer_engine.get_set_hand(set_hands, dealer)
    board.source = SOURCES['set-hands']
    _set_board_hands(board)
    return board


def _get_dealer_engine(params: dict[str, object],
                       board_number: int) -> tuple[object, str]:
    if params.mode == 'duo':
        dealer = SEATS[board_number % 4]
        dealer_engine = DealerDuo(dealer)
    else:
        dealer = 'N'
        dealer_engine = DealerSolo(dealer)
    return (dealer_engine, dealer)


def _set_board_hands(board: Board):
    for index in range(4):
        board.players[index].hand = board.hands[index]


def _get_random_board(params) -> Board:
    """Return a random board."""
    # Doesn't matter whether we use DealerSolo or DealerDuo
    board = DealerDuo().deal_random_board()
    board.set_hand = None
    board.source = SOURCES['random']
    _set_board_hands(board)
    print(f'{board.auction=}')
    return board


def get_room_board(params: dict[str, str]) -> dict[str, object]:
    room = get_room_from_name(params.room_name)
    board = Board().from_json(room.board)

    state_context = get_board_context(params, room, board)
    (trick_cards, trick_leader, trick_suit) = _get_trick_details(board)

    # Assign trick cards in case that new trick has no cards yet.
    if not trick_cards and len(board.tricks) > 1:
        trick_cards = [card.name for card in board.tricks[-2].cards]
        trick_leader = board.tricks[-2].leader

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
    return {**state_context, **specific_context}


def get_history_board(params) -> Board:
    room = get_room_from_name(params.room_name)
    board = get_board_from_archive(params)

    board.display_stats()

    board.auction = get_initial_auction(params, board, [])
    pbn_string = get_pbn_string(board)
    board.source = SOURCES['history']
    logger.info(f' User: <{params.username}> history board: {pbn_string}')
    return get_board_context(params, room, board)


def _get_trick_details(board: Board) -> tuple[list[str], str, str]:
    trick_cards, trick_leader, trick_suit = [], '', ''
    if board.tricks:
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


def get_board_from_pbn(params):
    """Return board from a PBN string."""
    room = get_room_from_name(params.room_name)
    board = _get_board_from_pbn_string(params)
    if not board:
        return {'error': 'Invalid pbn string'}

    board.source = SOURCES['pbn']
    get_unplayed_cards_for_board_hands(board)
    board.display_stats()

    trick_context = _trick_context_for_pbn_board(board)
    room = get_room_from_name(params.room_name)
    board_context = get_board_context(params, room, board)
    return {**board_context, **trick_context}


def _trick_context_for_pbn_board(board: Board) -> dict[str, str]:
    if not board.tricks:
        trick = board.setup_first_trick_for_board()
        board.tricks.append(trick)
    trick_context = _play_initial_cards(board)

    if suggested_card := next_card(board):
        trick_context['suggested_card'] = suggested_card.name
    return trick_context


def _play_initial_cards(board: Board) -> dict[str, str]:
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
    if not trick.cards:
        return {}
    return {
        'trick_leader': trick.leader,
        'trick_suit': trick.suit.name,
        'trick_cards': [card.name for card in trick.cards],
    }


def _get_board_from_pbn_string(params: dict[str, str]) -> Board:
    pbn_list = []
    if '\n' in params.pbn_text:
        pbn_list_raw = (params.pbn_text).split('\n')
        pbn_list.extend(item.replace('<br>', '').strip()
                        for item in pbn_list_raw)
    elif '<br>' in params.pbn_text:
        pbn_list_raw = (params.pbn_text).split('<br>')
        pbn_list.extend(item.strip() for item in pbn_list_raw)
    if not pbn_list:
        return None
    logger.info(f' User: <{params.username}> pbn board: {params.pbn_text}')
    try:
        raw_board = parse_pbn(pbn_list)[0].boards[0]
    except (ValueError, IndexError):
        return None

    board = Board()
    board.get_attributes_from_board(raw_board)
    bid_history = [call.name for call in board.auction.calls]
    board.bid_history = bid_history

    # This is necessary because the contract gets
    # lost after the call to get_initial_auction
    contract = board._contract

    board.auction = get_initial_auction(params, board, bid_history=bid_history)

    board.contract = contract
    get_unplayed_cards_for_board_hands(board)
    return board


def _get_leader(declarer: str) -> str:
    """Return the index of the board leader."""
    if not declarer:
        return ''
    seat_index = SEATS.index(declarer)
    leader_index = (seat_index + 1) % 4
    return SEATS[leader_index]


def update_trick_scores(board: Board, trick: Trick):
    if not trick.winner:
        return
    if trick.winner in 'NS':
        board.NS_tricks += 1
    elif trick.winner in 'EW':
        board.EW_tricks += 1


def undo_context(params):
    room = get_room_from_name(params.room_name)
    board = Board().from_json(room.board)
    if board.contract.name:
        logger.info(f' User: <{params.username}> clicked undo card play')
        undo_cardplay(board, params.mode)
        board.current_player = get_current_player(board.tricks[-1])
    else:
        logger.info(f' User: <{params.username}> clicked undo bid')
        _undo_bids(board, params.seat)

    return get_board_context(params, room, board)


def _undo_bids(board, seat):
    last_bid = _get_players_last_bid(board, seat)
    while board.bid_history[-1] != last_bid:
        board.bid_history = board.bid_history[:-1]
    board.bid_history = board.bid_history[:-1]


def _get_players_last_bid(board, seat):
    bidder_index = SEATS.index(board.dealer)
    calls = {seat_name: '' for seat_name in SEATS}
    for call in board.bid_history:
        bidder_seat = SEATS[bidder_index]
        calls[bidder_seat] = call
        bidder_index += 1
        bidder_index %= 4
    return calls[seat]
