"""Helper classes for BfG."""
import json
from datetime import datetime, timezone
from termcolor import cprint


from bridgeobjects import SEATS, Trick, Call, Denomination
from bfgdealer import Board

from .models import Room, User

MODULE_COLOUR = 'blue'


def get_room_from_name(name: str) -> Room:
    return Room.objects.get_or_create(name=name)[0]


def get_user_from_username(username: str) -> User:
    return User.objects.get_or_create(username=username)[0]


def update_user_activity(params: dict) -> None:
    user = get_user_from_username(params.username)
    user.last_activity = datetime.now().replace(tzinfo=timezone.utc)
    user.save()


class Params():
    def __init__(self, raw_params):
        params = json.loads(raw_params)

        self.username = params.get('username', '')
        self.partner_username = params.get('partner_username', '')
        self.board_id = params.get('board_id', '')
        self.seat = params.get('seat', 'N')
        self.room_name = params.get('room_name', '')
        self.bid = params.get('bid', '')
        self.generate_contract = params.get('generate_contract', False)
        self.set_hands = params.get('set_hands', [])
        self.display_hand_type = params.get('display_hand_type', False)
        self.use_set_hands = params.get('use_set_hands', False)
        self.mode = params.get('mode', '')
        self.card_played = params.get('card_played', '')
        self.card_player = params.get('card_player', '')
        self.board_number = params.get('board_number', '')
        self.rotation_seat = params.get('rotation_seat', '')
        self.dealer = params.get('dealer', '')
        self.claim_tricks = params.get('claim_tricks', 0)
        self.NS_tricks = params.get('NS_tricks', 0)
        self.EW_tricks = params.get('EW_tricks', 0)
        self.tester = params.get('tester', False)
        self.file_name = params.get('file_name', '')
        self.file_description = params.get('file_description', '')
        self.archive_name = params.get('archive_name', '')
        self.pbn_text = params.get('pbn_text', '')
        self.pbn_text_length = params.get('file_description', 0)
        self.browser = params.get('browser', True)
        self.use_double_dummy = params.get('use_double_dummy', True)
        self.message = params.get('message', {})
        self.payload = params.get('payload', {})
        self.user_query = params.get('user_query', '')

        self.seat_index = SEATS.index(self.seat)

        # # raw_params = unquote(raw_params)
        # params = json.loads(raw_params)
        # self.username = params.get('username')
        # self.username = self._update_attribute(params, 'username')
        # self.partner_username = self._update_attribute(params,
        #                                                'partner_username')
        # self.board_id = self._update_attribute(params, 'board_id')
        # self.seat = self._update_attribute(params, 'seat', 'N')
        # self.room_name = self._update_attribute(params, 'room_name')
        # self.bid = self._update_attribute(params, 'bid')
        # self.generate_contract = self._update_attribute(params,
        #                                                 'generate_contract',
        #                                                 False)
        # self.set_hands = self._update_attribute(params, 'set_hands', [])
        # self.display_hand_type = self._update_attribute(params,
        #                                                 'display_hand_type',
        #                                                 False)
        # self.use_set_hands = self._update_attribute(params,
        #                                             'use_set_hands', False)
        # self.file_name = self._update_attribute(params, 'file_name')
        # self.mode = self._update_attribute(params, 'mode')
        # self.card_played = self._update_attribute(params, 'card_played')
        # self.card_player = self._update_attribute(params, 'card_player')
        # self.board_number = self._update_attribute(params, 'board_number')
        # self.rotation_seat = self._update_attribute(params, 'rotation_seat')
        # self.dealer = self._update_attribute(params, 'dealer')
        # self.claim_tricks = self._update_attribute(params, 'claim_tricks', 0)
        # self.display_hand_type = self._update_attribute(params,
                                                        # 'display_hand_type')
        # self.NS_tricks = self._update_attribute(params, 'NS_tricks', 0)
        # self.EW_tricks = self._update_attribute(params, 'EW_tricks', 0)
        # self.tester = self._update_attribute(params, 'tester', False)
        # self.file_description = self._update_attribute(params,
        #                                                'file_description')
        # self.file_name = self._update_attribute(params, 'file_name')
        # self.archive_name = self._update_attribute(params, 'archive_name')
        # self.pbn_text = self._update_attribute(params, 'pbn_text', '')
        # self.pbn_text_length = self._update_attribute(params,
        #                                               'pbn_text_length', 0)

        # self.seat_index = SEATS.index(self.seat)
        # self.browser = self._update_attribute(params, 'browser', True)
        # self.use_double_dummy = self._update_attribute(
        #     params, 'use_double_dummy', True)
        # self.message = self._update_attribute(params, 'message', {})
        # self.payload = self._update_attribute(params, 'payload', {})
        # self.user_query = self._update_attribute(params, 'user_query', '')

    # @staticmethod
    # def _update_attribute(params, attribute, default=None):
    #     return params[attribute] if attribute in params else default

    def __repr__(self):
        return str(self.__dict__)


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
        cprint(f"{key}, {context[key]}", MODULE_COLOUR)
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
