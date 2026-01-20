"""Helper classes for BfG."""
import json
from datetime import datetime, timezone

from dataclasses import dataclass, field
from typing import Any

from bridgeobjects import SEATS, Trick, Call, Denomination
from bfgdealer import Board

from common.models import Room, User


@dataclass(slots=True)
class GameRequest:
    username: str = ""
    partner_username: str = ""
    board_id: str = ""
    seat: str = "N"
    room_name: str = ""
    bid: str = ""
    generate_contract: bool = False
    set_hands: list = field(default_factory=list)
    display_hand_type: bool = False
    use_set_hands: bool = False
    mode: str = ""
    card_played: str = ""
    card_player: str = ""
    board_number: int = 0
    rotation_seat: str = ""
    dealer: str = ""
    claim_tricks: int = 0
    NS_tricks: int = 0
    EW_tricks: int = 0
    tester: bool = False
    file_name: str = ""
    file_description: str = ""
    archive_name: str = ""
    pbn_text: str = ""
    browser: bool = True
    use_double_dummy: bool = False
    message: dict[str, Any] = field(default_factory=dict)
    payload: dict[str, Any] = field(default_factory=dict)
    user_query: str = ""

    seat_index: int = field(init=False)

    def __post_init__(self) -> None:
        if self.seat not in SEATS:
            raise ValueError(f"Invalid seat: {self.seat}")

        self.seat_index = SEATS.index(self.seat)

        if self.mode not in {"solo", "duo", "solo-no-comments"}:
            raise ValueError(f"Invalid mode: {self.mode}")


def req_from_json(raw_params: str) -> GameRequest:
    data = json.loads(raw_params)
    return GameRequest(
        username=data.get("username", ""),
        partner_username=data.get("partner_username", ""),
        board_id=data.get("board_id", ""),
        seat=data.get("seat", "N"),
        room_name=data.get("room_name", ""),
        bid=data.get("bid", ""),
        generate_contract=bool(data.get("generate_contract", False)),
        set_hands=data.get("set_hands", []),
        display_hand_type=bool(data.get("display_hand_type", False)),
        use_set_hands=bool(data.get("use_set_hands", False)),
        mode=data.get("mode", ""),
        card_played=data.get("card_played", ""),
        card_player=data.get("card_player", ""),
        board_number=int(data.get("board_number", 0)),
        rotation_seat=data.get("rotation_seat", ""),
        dealer=data.get("dealer", ""),
        claim_tricks=int(data.get("claim_tricks", 0)),
        NS_tricks=int(data.get("NS_tricks", 0)),
        EW_tricks=int(data.get("EW_tricks", 0)),
        tester=bool(data.get("tester", False)),
        file_name=data.get("file_name", ""),
        file_description=data.get("file_description", ""),
        archive_name=data.get("archive_name", ""),
        pbn_text=data.get("pbn_text", ""),
        browser=bool(data.get("browser", True)),
        use_double_dummy=bool(data.get("use_double_dummy", False)),
        message=data.get("message", {}),
        payload=data.get("payload", {}),
        user_query=data.get("user_query", ""),
    )


class UserProxy():
    def __init__(self, username=None, seat=None, room_name=None):
        self.pk = username
        self.seat = seat
        self.room_name = room_name
        self.bid_double_click = False
        self.card_double_click = False
        self.username = ''
        self.auto_play = False

    def __repr__(self):
        return str(self.__dict__)


def get_room_from_name(name: str) -> Room:
    return Room.objects.get_or_create(name=name)[0]


def get_user_from_username(username: str) -> User:
    return User.objects.get_or_create(username=username)[0]


def update_user_activity(req: dict) -> None:
    user = get_user_from_username(req.username)
    user.last_activity = datetime.now().replace(tzinfo=timezone.utc)
    user.save()


def three_passes(bid_history: list[str]) -> bool:    # X
    """Return True if there are 3 passes."""
    return len(bid_history) >= 4 and (
        bid_history[-1] == 'P'
        and bid_history[-2] == 'P'
        and bid_history[-3] == 'P'
    )


def passed_out(bid_history: list[str]) -> bool:    # X
    """Return True if there are 4 passes."""
    return len(bid_history) == 4 and (
        bid_history[0] == 'P'
        and bid_history[1] == 'P'
        and bid_history[2] == 'P'
        and bid_history[3] == 'P'
    )


def save_board(room: Room, board: Board) -> None:
    get_unplayed_cards_for_board_hands(board)
    room.board = board.to_json()
    room.save()


def get_unplayed_cards_for_board_hands(board: Board) -> None:
    if _unplayed_cards_have_not_been_generated(board):
        for key, hand in board.hands.items():
            if not hand.unplayed_cards:
                hand.unplayed_cards = list(hand.cards)


def _unplayed_cards_have_not_been_generated(board: Board) -> bool:
    return not any(hand.unplayed_cards for hand in board.hands.values())


def dict_print(context):
    print('')
    print('='*40, 'dict print', '='*40)
    sorted_keys = sorted(context, key=lambda x: x)
    for key in sorted_keys:
        print(f"{key}, {context[key]}")
    print('='*100)
    print('')


def get_current_player(trick: Trick) -> str:
    """Return the current player from the trick."""
    if len(trick.cards) == 4:
        return trick.winner
    leader_index = SEATS.index(trick.leader)
    current_player = (leader_index + len(trick.cards)) % 4
    return SEATS[current_player]


def get_bidding_data(board: Board) -> tuple[str]:
    """Return levels and denoms to disable bid box buttons."""
    call = _get_last_call(board)
    return _get_suppress_list(board) if call else {}


def _get_suppress_list(board: Board) -> tuple:
    call = _get_last_call(board)

    denoms = []

    for denom in Denomination.SHORT_NAMES:
        denoms.append(denom)
        if denom == call[1:]:
            break

    level = int(call[0])
    if call[1:] == 'NT':
        denoms = []
        level += 1

    calls = board.bid_history
    can_double = _can_double(calls)
    can_redouble = _can_redouble(calls)

    return {
        'level': level,
        'suppress_denoms': denoms,
        'can_double': can_double,
        'can_redouble': can_redouble,
    }


def _get_last_call(board: Board) -> str:
    for call in reversed(board.bid_history):
        if Call(call).is_value_call:
            return call
    return ''


def _can_double(calls: list) -> bool:
    if calls and Call(calls[-1]).is_value_call:
        return True
    if (len(calls) >= 3
            and Call(calls[-3]).is_value_call
            and Call(calls[-2]).is_pass
            and Call(calls[-1]).is_pass):
        return True
    return False


def _can_redouble(calls: list) -> bool:
    if calls and Call(calls[-1]).is_double:
        return True
    return bool(
        (
            len(calls) >= 3
            and Call(calls[-3]).is_double
            and Call(calls[-2]).is_pass
            and Call(calls[-1]).is_pass
        )
    )
