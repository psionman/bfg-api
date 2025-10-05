"""Helper classes for BfG."""
import json
from termcolor import cprint

from bridgeobjects import SEATS, Trick
from bfgdealer import Board

from .models import Room

MODULE_COLOUR = 'blue'


def get_room_from_name(name: str) -> Room:
    return Room.objects.get_or_create(name=name)[0]


class Params():
    def __init__(self, raw_params):
        # raw_params = unquote(raw_params)
        params = json.loads(raw_params)
        self.username = self._update_attribute(params, 'username')
        self.partner_username = self._update_attribute(params,
                                                       'partner_username')
        self.board_id = self._update_attribute(params, 'board_id')
        self.seat = self._update_attribute(params, 'seat', 'N')
        self.room_name = self._update_attribute(params, 'room_name')
        self.bid = self._update_attribute(params, 'bid')
        self.generate_contract = self._update_attribute(params,
                                                        'generate_contract',
                                                        False)
        self.set_hands = self._update_attribute(params, 'set_hands', [])
        self.display_hand_type = self._update_attribute(params,
                                                        'display_hand_type',
                                                        False)
        self.use_set_hands = self._update_attribute(params,
                                                    'use_set_hands', False)
        self.file_name = self._update_attribute(params, 'file_name')
        self.mode = self._update_attribute(params, 'mode')
        self.card_played = self._update_attribute(params, 'card_played')
        self.board_number = self._update_attribute(params, 'board_number')
        self.rotation_seat = self._update_attribute(params, 'rotation_seat')
        self.dealer = self._update_attribute(params, 'dealer')
        self.claim_tricks = self._update_attribute(params, 'claim_tricks', 0)
        self.display_hand_type = self._update_attribute(params,
                                                        'display_hand_type')
        self.NS_tricks = self._update_attribute(params, 'NS_tricks', 0)
        self.EW_tricks = self._update_attribute(params, 'EW_tricks', 0)
        self.tester = self._update_attribute(params, 'tester', False)
        self.file_description = self._update_attribute(params,
                                                       'file_description')
        self.file_name = self._update_attribute(params, 'file_name')
        self.archive_name = self._update_attribute(params, 'archive_name')
        self.pbn_text = self._update_attribute(params, 'pbn_text', '')
        self.pbn_text_length = self._update_attribute(params,
                                                      'pbn_text_length', 0)

        self.seat_index = SEATS.index(self.seat)
        self.browser = self._update_attribute(params, 'browser', True)
        self.use_double_dummy = self._update_attribute(
            params, 'use_double_dummy', True)

    @staticmethod
    def _update_attribute(params, attribute, default=None):
        if attribute in params:
            return params[attribute]
        return default

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


def three_passes(bid_history: list[str]) -> bool:  # X
    """Return True if there are 3 passes."""
    if len(bid_history) >= 4:
        if (bid_history[-1] == 'P' and
                bid_history[-2] == 'P' and
                bid_history[-3] == 'P'):
            return True
    return False


def passed_out(bid_history: list[str]) -> bool:  # X
    """Return True if there are 4 passes."""
    if len(bid_history) == 4:
        if (bid_history[0] == 'P' and
                bid_history[1] == 'P' and
                bid_history[2] == 'P' and
                bid_history[3] == 'P'):
            return True
    return False


def save_board(room: Room, board: Board) -> None:
    get_unplayed_cards_for_board_hands(board)
    room.board = board.to_json()
    room.save()


def get_unplayed_cards_for_board_hands(board: Board) -> None:
    if _unplayed_cards_have_not_been_generated(board):
        for key, hand in board.hands.items():
            if not hand.unplayed_cards:
                hand.unplayed_cards = [card for card in hand.cards]


def _unplayed_cards_have_not_been_generated(board: Board) -> bool:
    # Only generate unplayed cards if no hand has them.
    for hand in board.hands.values():
        if hand.unplayed_cards:
            return False
    return True


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
