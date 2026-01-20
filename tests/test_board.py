from pathlib import Path
import json
import requests
from bridgeobjects import load_pbn
from urllib.parse import quote

from ..tests.utilities import get_board

BOARD_PATH = Path('tests', 'test_data', 'board.pbn')
APP_DOMAIN = 'http://192.168.4.28:8000/bfg'

req = {
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


boards = load_pbn(BOARD_PATH)[0].boards


def get_board_context(board_index):
    board = get_board(boards, board_index)
    pbn_str = '\n'.join(board.board_to_pbn())

    req['pbn_text'] = pbn_str
    uri = 'pbn-board'

    json_params = json.dumps(req)
    payload = quote(json_params)
    response = requests.get(f"{APP_DOMAIN}/{uri}/{payload}")
    return response.json()


def test_versions():
    uri = 'versions/'
    response = requests.get(f"{APP_DOMAIN}/{uri}")
    context = response.json()
    assert 'bfgbidding' in context
    assert 'bfgcardplay' in context
    assert 'bfgdealer' in context
    assert 'bridgeobjects' in context


# def test_board_from_pbn():
#     context = get_board_context(0)
#     assert context['dealer'] == 'E'
#     assert len(context['bid_history']) == 3
#     assert context['hand_suit_length']['N'] == [4, 1, 4, 3]
#     assert context['hand_suit_length']['W'] == [3, 1, 5, 2]
#     assert '6H' in context['hand_cards'][1]
#     assert '6H' in context['unplayed_card_names']['E']
#     assert context['source'] == 3
#     assert context['contract_target'] == 8


def test_board_from_pbn_current_player():
    context = get_board_context(1)
    assert context['current_player'] == 'W'
