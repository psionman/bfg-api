"""
    Archive functionality for Bfg.

    The archive is a field in the room model.
    It is a json encoded list of pbn strings.
"""
import json
from datetime import datetime

from bridgeobjects import (SEATS, SUIT_NAMES, RANKS,
                           create_pbn_board, Call, Card,)
from bfgbidding import Hand
from bfgdealer import Board, Auction

from common.models import Room
from common.utilities import get_room_from_name, GameRequest
from common.constants import MAX_ARCHIVE

DATE_FORMAT = '%d %b %Y %H:%M:%S'


def save_board_to_archive(room: Room, board: Board) -> None:
    archive = json.loads(room.archive) if room.archive else []
    board.description = datetime.now().strftime(DATE_FORMAT)
    archive.insert(0, get_pbn_string(board))
    if len(archive) >= MAX_ARCHIVE:
        archive = archive[:MAX_ARCHIVE]
    room.archive = json.dumps(archive)
    room.save()


def get_history_boards_text(
        req: GameRequest) -> dict[str, dict[str, str]]:
    boards = []
    raw_boards = []
    raw_boards = _get_raw_archive_boards(req.room_name)
    for index, board in enumerate(raw_boards):
        board_dict = _get_history_board_dict(index, board)
        boards.append(board_dict)
    return {'boards': boards,}


def save_boards_file_to_room(req):
    room = get_room_from_name(req.room_name)
    saved_boards = json.loads(room.saved_boards)
    file = {
        'name': req.file_name,
        'description': req.file_description,
        'pbn_text': req.pbn_text,
    }
    saved_boards.append(file)
    room.saved_boards = json.dumps(saved_boards)
    room.save()
    return {'boards_saved': True}


def get_user_archive_list(req):
    room = get_room_from_name(req.username)
    saved_boards = json.loads(room.saved_boards)
    archives = sorted([archive['description'] for archive in saved_boards])
    return {'archives': archives}


def get_board_file_from_room(req):
    return {
        # 'file_names': file_names
    }


def _get_raw_archive_boards(room_name: str) -> list[Board]:
    room = get_room_from_name(room_name)
    archive = json.loads(room.archive) if room.archive else []
    return _get_boards_from_pbn(archive)


def _get_boards_from_pbn(archive) -> list[Board]:
    boards = []
    for archive_board in archive:
        board = Board()
        pbn_board = archive_board.split('\n')
        board.parse_pbn_board(pbn_board)
        boards.append(board)
    return boards


def _get_history_board_dict(index: int, board: Board) -> dict[str, str]:
    hands = {}
    for seat in 'NS':
        hand = board.hands[seat]
        hands[seat] = _get_cards_by_suit(hand)
    return {
        'identifier': index + 1,
        'date': board.description,
        'hands': hands,
    }


def _get_cards_by_suit(hand: Hand) -> dict[str, list[Card]]:
    return {
        suit: _get__suit_cards_as_string(hand, suit) for suit in SUIT_NAMES}


def _get__suit_cards_as_string(hand: Hand, suit: str) -> str:
    """Return a string of card ranks."""
    unsorted_ranks = [card.rank for card in hand.cards if
                      card.suit.name == suit]
    sorted_ranks = list(reversed(RANKS[1:]))
    ranks = [rank for rank in sorted_ranks if rank in unsorted_ranks]
    return ''.join(ranks)


def get_pbn_string(board: Board) -> str:
    """Return the pbn string in a suitable form for download."""
    calls = [Call(bid) for bid in board.bid_history]
    if not board.auction.calls:
        board.auction = Auction(calls, board.dealer)
    return create_pbn_board(board)


def get_board_from_archive(req: GameRequest) -> Board:
    """Get the archived board and make it room current board."""
    archived_board_id = req.board_id
    if not archived_board_id or int(archived_board_id) == 0:
        archived_board_id = 1
    boards = _get_raw_archive_boards(req.room_name)
    board = boards[int(req.board_id) - 1]
    board.identifier = req.board_id
    return board


def rotate_archived_boards(req: GameRequest) -> dict[str, object]:
    """Rotate archive hands, placing N in the rotation_seat."""
    room = get_room_from_name(req.room_name)
    boards = _get_raw_archive_boards(req.room_name)
    rotation_index = SEATS.index(req.rotation_seat)
    for board in boards:
        board = _rotate_board(board, rotation_index)

    archive = _create_list_of_archive_boards(boards)
    room.archive = json.dumps(archive)
    room.save()
    return get_history_boards_text(req)


def _rotate_board(board: Board, rotation_index: int) -> Board:
    board.dealer = _get_dealer_for_rotated_board(board.dealer, rotation_index)
    board.vulnerable = _get_rotated_vulnerability(board, rotation_index)
    board = _rotate_board_hands(board, rotation_index)
    return board


def _rotate_board_hands(board: Board, rotation_index: int) -> Board:
    hands = [board.hands[index] for index in range(4)]
    for index, hand in enumerate(hands):
        target_index = (index + rotation_index) % 4
        target_seat = SEATS[target_index]
        board.hands[target_index] = hand
        board.hands[target_seat] = hand
    return board


def _create_list_of_archive_boards(boards: list[Board]) -> list[str]:
    archive = []
    for board in boards:
        board_pbn = get_pbn_string(board)
        archive.append(board_pbn)
    return archive


def _get_rotated_vulnerability(board: Board, rotation_index: int) -> str:
    if rotation_index % 2 == 1:
        if board.vulnerable == 'EW':
            return 'NS'
        if board.vulnerable == 'NS':
            return 'EW'
    return board.vulnerable


def _get_dealer_for_rotated_board(dealer: str, rotation_index: int) -> str:
    dealer_index = SEATS.index(dealer)
    target_dealer_index = (dealer_index + rotation_index) % 4
    return SEATS[target_dealer_index]
