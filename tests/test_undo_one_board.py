"""
See https://psionman.netlify.app/projects/bfg_card_undo.html for documentation and board xref
"""
from pathlib import Path
import json
import requests
from bridgeobjects import load_pbn, Card
from bfgdealer import Board
from urllib.parse import quote

BOARD_PATH = Path('tests', 'test_data', 'undo.pbn')
APP_DOMAIN = 'http://192.168.4.28:8000/bfg'


BOARD_PARAMS = {
    'username': 'test',
    'partner_username': None,
    'board_id': None,
    'seat': 'N',
    'room_name': 'test',
    'bid': None,
    'generate_contract': False,
    'set_hands': [],
    'display_hand_type': False,
    'use_set_hands': False,
    'pbn_text': '',
    'file_description': None,
    'file_name': None,
    'mode': 'solo',
    'card_played': None,
    'board_number': None,
    'rotation_seat': None,
    'dealer': None,
    'claim_tricks': 0,
    'NS_tricks': 0,
    'EW_tricks': 0,
    'tester': True,
    'seat_index': 0,
}

req = {
    'room_name': 'test',
    'seat': 'N',
    'username': 'test',
    'use_set_hands': False
    }

event = load_pbn(BOARD_PATH)[0]
board_list = [Board().get_attributes_from_board(board) for board in event.boards]

boards = {}
for raw_board in event.boards:
    board = Board()
    board.get_attributes_from_board(raw_board)
    boards[int(board.identifier)] = board


def update_board(board_index):
    """
        Return the response when a board is created from a pbn string.
        Necessary to get the api in correct state for further processing.
    """
    board = boards[board_index]
    pbn_str = '\n'.join(board.board_to_pbn())

    req = {key: item for key, item in BOARD_PARAMS.items()}
    req['pbn_text'] = pbn_str
    uri = 'pbn-board'

    json_params = json.dumps(req)
    payload = quote(json_params)
    response = requests.get(f"{APP_DOMAIN}/{uri}/{payload}")
    return response


def _card_undo_context(board_index, mode):
    response = update_board(board_index)
    uri = 'undo'
    req['mode'] = mode

    json_params = json.dumps(req)
    payload = quote(json_params)
    response = requests.get(f"{APP_DOMAIN}/{uri}/{payload}")
    context = response.json()
    return context

# D8 D9 DQ DK
# D3 C5 C2 DJ
# CQ C3



def test_undo_solo_NS_declarer_EW_leader_only_one_card_in_trick():
    board_id = 16
    board = boards[board_id]
    update_board(board_id)
    assert Card('6C') not in board.hands['N'].unplayed_cards
    assert Card('2C') not in board.hands['W'].unplayed_cards
    assert Card('KC') not in board.hands['E'].unplayed_cards
    Board.NS_tricks = 2
    Board.EW_tricks = 2
    context = _card_undo_context(board_id, 'solo')
    assert '6C' in context['unplayed_card_names']['N']
    assert 'KC' in context['unplayed_card_names']['E']
    assert '2C' not in context['unplayed_card_names']['W']
    assert context['NS_tricks'] == 2
    assert context['EW_tricks'] == 1
