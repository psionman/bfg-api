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
    'ns_tricks': 0,
    'ew_tricks': 0,
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


def test_undo_solo_ns_declarer_ew_leader_first_trick_first_card():
    board_id = 0
    board = boards[board_id]
    update_board(board_id)
    assert Card('AH') in board.hands['W'].unplayed_cards
    assert Card('2H') in board.hands['S'].unplayed_cards
    assert Card('TH') not in board.hands['E'].unplayed_cards

    context = _card_undo_context(board_id, 'solo')
    assert Card('AH') in board.hands['W'].unplayed_cards
    assert Card('2H') in board.hands['S'].unplayed_cards
    assert 'TH' not in context['unplayed_card_names']['E']


def test_undo_duo_ns_declarer_ew_leader_first_trick_first_card():
    board_id = 0
    board = boards[board_id]
    update_board(board_id)
    assert Card('AH') in board.hands['W'].unplayed_cards
    assert Card('2H') in board.hands['S'].unplayed_cards
    assert Card('TH') not in board.hands['E'].unplayed_cards

    context = _card_undo_context(board_id, 'duo')
    assert Card('AH') in board.hands['W'].unplayed_cards
    assert Card('2H') in board.hands['S'].unplayed_cards
    assert 'TH' not in context['unplayed_card_names']['E']


# NS declarer - Leader EW - first trick

def test_undo_solo_ns_declarer_ew_leader_first_trick_third_card():
    board_id = 1
    board = boards[board_id]
    update_board(board_id)
    assert Card('AH') not in board.hands['W'].unplayed_cards
    assert Card('2H') not in board.hands['S'].unplayed_cards
    assert Card('TH') not in board.hands['E'].unplayed_cards
    context = _card_undo_context(board_id, 'solo')
    assert 'AH' in context['unplayed_card_names']['W']
    assert '2H' in context['unplayed_card_names']['S']
    assert 'TH' not in context['unplayed_card_names']['E']


def test_undo_duo_ns_declarer_ew_leader_first_trick_third_card():
    board_id = 1
    board = boards[board_id]
    update_board(board_id)
    assert Card('AH') not in board.hands['W'].unplayed_cards
    assert Card('2H') not in board.hands['S'].unplayed_cards
    assert Card('TH') not in board.hands['E'].unplayed_cards
    context = _card_undo_context(board_id, 'duo')
    assert 'AH' in context['unplayed_card_names']['W']
    assert '2H' in context['unplayed_card_names']['S']
    assert 'TH' not in context['unplayed_card_names']['E']


def test_undo_solo_ns_declarer_ew_leader_first_trick_fourth_card():
    board_id = 2
    board = boards[board_id]
    update_board(board_id)
    assert Card('7D') not in board.hands['W'].unplayed_cards

    context = _card_undo_context(board_id, 'solo')
    assert '3D' in context['unplayed_card_names']['N']
    assert '7D' not in context['unplayed_card_names']['W']


def test_undo_duo_ns_declarer_ew_leader_first_trick_fourth_card():
    board_id = 2
    board = boards[board_id]
    update_board(board_id)
    assert Card('7D') not in board.hands['W'].unplayed_cards

    context = _card_undo_context(board_id, 'duo')
    assert '3D' in context['unplayed_card_names']['N']
    assert '7D' not in context['unplayed_card_names']['W']


# W declarer - Leader N - first trick
def test_undo_solo_w_declarer_n_leader_first_trick_first_card():
    board_id = 3
    board = boards[board_id]
    update_board(board_id)
    assert Card('3S') not in board.hands['W'].unplayed_cards
    assert Card('2S') not in board.hands['S'].unplayed_cards
    assert Card('KS') not in board.hands['E'].unplayed_cards
    assert Card('AS') not in board.hands['N'].unplayed_cards

    context = _card_undo_context(3, 'solo')
    assert '3S' in context['unplayed_card_names']['W']
    assert '2S' in context['unplayed_card_names']['S']
    assert 'KS' in context['unplayed_card_names']['E']
    assert 'AS' in context['unplayed_card_names']['N']


def test_undo_duo_w_declarer_n_leader_first_trick_first_card():
    board_id = 3
    board = boards[board_id]
    update_board(board_id)
    assert Card('3S') not in board.hands['W'].unplayed_cards
    assert Card('2S') not in board.hands['S'].unplayed_cards
    assert Card('KS') not in board.hands['E'].unplayed_cards
    assert Card('AS') not in board.hands['N'].unplayed_cards

    context = _card_undo_context(3, 'duo')
    assert '3S' in context['unplayed_card_names']['W']
    assert '2S' in context['unplayed_card_names']['S']
    assert 'KS' not in context['unplayed_card_names']['E']
    assert 'AS' not in context['unplayed_card_names']['N']


# E declarer - Leader S - first trick
def test_undo_solo_e_declarer_s_leader_first_trick_first_card():
    board_id = 4
    board = boards[board_id]
    update_board(board_id)
    assert Card('8D') not in board.hands['S'].unplayed_cards
    assert Card('4D') not in board.hands['W'].unplayed_cards
    context = _card_undo_context(board_id, 'solo')
    assert '8D' not in context['unplayed_card_names']['S']
    assert '4D' not in context['unplayed_card_names']['W']


def test_undo_duo_e_declarer_s_leader_first_trick_first_card():
    board_id = 4
    board = boards[board_id]
    update_board(board_id)
    assert Card('8D') not in board.hands['S'].unplayed_cards
    assert Card('4D') not in board.hands['W'].unplayed_cards
    context = _card_undo_context(board_id, 'duo')
    assert '8D' in context['unplayed_card_names']['S']
    assert '4D' in context['unplayed_card_names']['W']


# NS declarer - Leader EW - subsequent tricks
def test_undo_solo_ew_leader_subsequent_trick_first_card():
    board_id = 5
    board = boards[board_id]
    update_board(board_id)
    assert Card('QH') not in board.hands['W'].unplayed_cards
    assert Card('JH') not in board.hands['N'].unplayed_cards
    context = _card_undo_context(board_id, 'solo')
    assert 'QH' in context['unplayed_card_names']['W']
    assert 'JH' in context['unplayed_card_names']['N']


def test_undo_duo_ew_leader_subsequent_trick_first_card():
    board_id = 5
    board = boards[board_id]
    update_board(board_id)
    assert Card('QH') not in board.hands['W'].unplayed_cards
    assert Card('JH') not in board.hands['N'].unplayed_cards
    context = _card_undo_context(board_id, 'duo')
    assert 'QH' in context['unplayed_card_names']['W']
    assert 'JH' in context['unplayed_card_names']['N']


def test_undo_solo_ew_leader_subsequent_trick_third_card():
    board_id = 6
    board = boards[board_id]
    update_board(board_id)
    assert Card('QH') not in board.hands['W'].unplayed_cards
    assert Card('KH') not in board.hands['N'].unplayed_cards
    assert Card('6H') not in board.hands['E'].unplayed_cards
    context = _card_undo_context(board_id, 'solo')
    assert 'QH' not in context['unplayed_card_names']['W']
    assert 'KH' in context['unplayed_card_names']['N']
    assert '6H' in context['unplayed_card_names']['E']


def test_undo_duo_ew_leader_subsequent_trick_third_card():
    board_id = 6
    board = boards[board_id]
    update_board(board_id)
    assert Card('QH') not in board.hands['W'].unplayed_cards
    assert Card('KH') not in board.hands['N'].unplayed_cards
    assert Card('6H') not in board.hands['E'].unplayed_cards
    context = _card_undo_context(board_id, 'duo')
    assert 'QH' not in context['unplayed_card_names']['W']
    assert 'KH' in context['unplayed_card_names']['N']
    assert '6H' in context['unplayed_card_names']['E']


def test_undo_solo_ew_leader_subsequent_trick_fourth_card():
    board_id = 7
    board = boards[board_id]
    update_board(board_id)
    assert Card('QH') not in board.hands['W'].unplayed_cards
    assert Card('KH') not in board.hands['N'].unplayed_cards
    assert Card('6H') not in board.hands['E'].unplayed_cards
    assert Card('3H') not in board.hands['S'].unplayed_cards
    context = _card_undo_context(board_id, 'solo')
    assert 'QH' not in context['unplayed_card_names']['W']
    assert 'KH' in context['unplayed_card_names']['N']
    assert '6H' in context['unplayed_card_names']['E']
    assert '3H' in context['unplayed_card_names']['S']


def test_undo_duo_ew_leader_subsequent_trick_fourth_card():
    board_id = 7
    board = boards[board_id]
    update_board(board_id)
    assert Card('QH') not in board.hands['W'].unplayed_cards
    assert Card('KH') not in board.hands['N'].unplayed_cards
    assert Card('6H') not in board.hands['E'].unplayed_cards
    assert Card('3H') not in board.hands['S'].unplayed_cards
    context = _card_undo_context(board_id, 'duo')
    assert 'QH' not in context['unplayed_card_names']['W']
    assert 'KH' not in context['unplayed_card_names']['N']
    assert '6H' not in context['unplayed_card_names']['E']
    assert '3H' in context['unplayed_card_names']['S']


# NS declarer - Leader NS - subsequent tricks
def test_undo_solo_ns_leader_subsequent_trick_second_card():
    board_id = 8
    board = boards[board_id]
    update_board(board_id)
    assert Card('AS') not in board.hands['N'].unplayed_cards
    assert Card('3S') not in board.hands['E'].unplayed_cards
    context = _card_undo_context(board_id, 'solo')
    assert 'AS' in context['unplayed_card_names']['N']
    assert '3S' in context['unplayed_card_names']['E']


def test_undo_duo_ns_leader_subsequent_trick_second_card():
    board_id = 8
    board = boards[board_id]
    update_board(board_id)
    assert Card('AS') not in board.hands['N'].unplayed_cards
    assert Card('3S') not in board.hands['E'].unplayed_cards
    context = _card_undo_context(board_id, 'duo')
    assert 'AS' in context['unplayed_card_names']['N']
    assert '3S' in context['unplayed_card_names']['E']


def test_undo_solo_ns_leader_subsequent_trick_fourth_card():
    board_id = 9
    board = boards[board_id]
    update_board(board_id)
    assert Card('AS') not in board.hands['N'].unplayed_cards
    assert Card('3S') not in board.hands['E'].unplayed_cards
    assert Card('4S') not in board.hands['S'].unplayed_cards
    assert Card('2S') not in board.hands['W'].unplayed_cards
    context = _card_undo_context(board_id, 'solo')
    assert 'AS' not in context['unplayed_card_names']['N']
    assert '3S' not in context['unplayed_card_names']['E']
    assert '4S' in context['unplayed_card_names']['S']
    assert '2S' in context['unplayed_card_names']['W']


def test_undo_duo_ns_leader_subsequent_trick_fourth_card():
    board_id = 9
    board = boards[board_id]
    update_board(board_id)
    assert Card('AS') not in board.hands['N'].unplayed_cards
    assert Card('3S') not in board.hands['E'].unplayed_cards
    assert Card('4S') not in board.hands['S'].unplayed_cards
    assert Card('2S') not in board.hands['W'].unplayed_cards
    context = _card_undo_context(board_id, 'duo')
    assert 'AS' not in context['unplayed_card_names']['N']
    assert '3S' not in context['unplayed_card_names']['E']
    assert '4S' in context['unplayed_card_names']['S']
    assert '2S' in context['unplayed_card_names']['W']


# EW declarer - Leader N - subsequent tricks
def test_undo_solo_w_declarer_n_leader_subsequent_trick_fourth_card():
    board_id = 10
    board = boards[board_id]
    update_board(board_id)
    assert Card('AD') not in board.hands['N'].unplayed_cards
    assert Card('9D') not in board.hands['E'].unplayed_cards
    assert Card('8D') not in board.hands['S'].unplayed_cards
    assert Card('4D') not in board.hands['W'].unplayed_cards
    context = _card_undo_context(board_id, 'solo')
    assert 'AD' in context['unplayed_card_names']['N']
    assert '9D' in context['unplayed_card_names']['E']
    assert '8D' in context['unplayed_card_names']['S']
    assert '4D' in context['unplayed_card_names']['W']


def test_undo_duo_w_declarer_n_leader_subsequent_trick_fourth_card():
    board_id = 10
    board = boards[board_id]
    update_board(board_id)
    assert Card('AD') not in board.hands['N'].unplayed_cards
    assert Card('9D') not in board.hands['E'].unplayed_cards
    assert Card('8D') not in board.hands['S'].unplayed_cards
    assert Card('4D') not in board.hands['W'].unplayed_cards
    context = _card_undo_context(board_id, 'duo')
    assert 'AD' not in context['unplayed_card_names']['N']
    assert '9D' not in context['unplayed_card_names']['E']
    assert '8D' in context['unplayed_card_names']['S']
    assert '4D' in context['unplayed_card_names']['W']


# EW declarer - Leader S - subsequent tricks (see 13)
def test_undo_solo_w_declarer_s_leader_subsequent_trick_second_card():
    board_id = 11
    board = boards[board_id]
    update_board(board_id)
    assert Card('QS') not in board.hands['W'].unplayed_cards
    assert Card('8S') not in board.hands['S'].unplayed_cards
    context = _card_undo_context(board_id, 'solo')
    assert 'QS' in context['unplayed_card_names']['W']
    assert '8S' in context['unplayed_card_names']['S']


def test_undo_duo_w_declarer_s_leader_subsequent_trick_second_card():
    board_id = 11
    board = boards[board_id]
    update_board(board_id)
    assert Card('QS') not in board.hands['W'].unplayed_cards
    assert Card('8S') not in board.hands['S'].unplayed_cards
    context = _card_undo_context(board_id, 'duo')
    assert 'QS' in context['unplayed_card_names']['W']
    assert '8S' in context['unplayed_card_names']['S']


# EW declarer - Leader E - subsequent tricks
def test_undo_solo_w_declarer_e_leader_subsequent_trick_third_card():
    board_id = 12
    board = boards[board_id]
    update_board(board_id)
    assert Card('2H') not in board.hands['N'].unplayed_cards
    assert Card('AH') not in board.hands['E'].unplayed_cards
    assert Card('9D') not in board.hands['E'].unplayed_cards
    assert Card('AD') not in board.hands['S'].unplayed_cards
    context = _card_undo_context(board_id, 'solo')
    assert '2H' in context['unplayed_card_names']['N']
    assert 'AH' in context['unplayed_card_names']['E']
    assert '9D' in context['unplayed_card_names']['E']
    assert 'AD' in context['unplayed_card_names']['S']


def test_undo_duo_w_declarer_e_leader_subsequent_trick_third_card():
    board_id = 12
    board = boards[board_id]
    update_board(board_id)
    assert Card('2H') not in board.hands['N'].unplayed_cards
    assert Card('AH') not in board.hands['E'].unplayed_cards
    assert Card('9D') not in board.hands['E'].unplayed_cards
    assert Card('AD') not in board.hands['S'].unplayed_cards
    context = _card_undo_context(board_id, 'duo')
    assert '2H' not in context['unplayed_card_names']['N']
    assert 'AH' not in context['unplayed_card_names']['E']
    assert '9D' not in context['unplayed_card_names']['E']
    assert 'AD' in context['unplayed_card_names']['S']


# EW declarer - Leader S - subsequent tricks (see 11)
def test_undo_solo_w_declarer_s_leader_subsequent_trick_second_card_A():
    board_id = 13
    board = boards[board_id]
    update_board(board_id)
    assert Card('QC') not in board.hands['S'].unplayed_cards
    assert Card('5D') not in board.hands['W'].unplayed_cards
    assert Card('9D') not in board.hands['E'].unplayed_cards
    assert Card('3D') not in board.hands['N'].unplayed_cards
    context = _card_undo_context(board_id, 'solo')
    assert 'QC' in context['unplayed_card_names']['S']
    assert '5D' in context['unplayed_card_names']['W']
    assert '9D' not in context['unplayed_card_names']['E']
    assert '3D' not in context['unplayed_card_names']['S']


def test_undo_duo_w_declarer_s_leader_subsequent_trick_second_card_A():
    board_id = 13
    board = boards[board_id]
    update_board(board_id)
    assert Card('QC') not in board.hands['S'].unplayed_cards
    assert Card('5D') not in board.hands['W'].unplayed_cards
    assert Card('9D') not in board.hands['E'].unplayed_cards
    assert Card('3D') not in board.hands['N'].unplayed_cards
    context = _card_undo_context(board_id, 'duo')
    assert 'QC' in context['unplayed_card_names']['S']
    assert '5D' in context['unplayed_card_names']['W']
    assert '9D' not in context['unplayed_card_names']['E']
    assert '3D' not in context['unplayed_card_names']['S']


# EW declarer - Leader W - subsequent tricks
def test_undo_solo_w_declarer_w_leader_subsequent_trick_second_card():
    board_id = 14
    board = boards[board_id]
    update_board(board_id)
    assert Card('QC') not in board.hands['S'].unplayed_cards
    assert Card('5D') not in board.hands['W'].unplayed_cards
    assert Card('KD') not in board.hands['W'].unplayed_cards
    assert Card('8C') not in board.hands['N'].unplayed_cards
    context = _card_undo_context(board_id, 'solo')
    assert 'QC' not in context['unplayed_card_names']['S']
    assert '5D' not in context['unplayed_card_names']['W']
    assert 'KD' in context['unplayed_card_names']['W']
    assert '8C' in context['unplayed_card_names']['N']


def test_undo_duo_w_declarer_w_leader_subsequent_trick_second_card():
    board_id = 14
    board = boards[board_id]
    update_board(board_id)
    assert Card('QC') not in board.hands['S'].unplayed_cards
    assert Card('5D') not in board.hands['W'].unplayed_cards
    assert Card('KD') not in board.hands['W'].unplayed_cards
    assert Card('8C') not in board.hands['N'].unplayed_cards
    context = _card_undo_context(board_id, 'duo')
    assert 'QC' not in context['unplayed_card_names']['S']
    assert '5D' not in context['unplayed_card_names']['W']
    assert 'KD' in context['unplayed_card_names']['W']
    assert '8C' in context['unplayed_card_names']['N']


def test_undo_solo_w_declarer_w_leader_subsequent_trick_second_cardA():
    board_id = 15
    board = boards[board_id]
    update_board(board_id)
    assert Card('QC') not in board.hands['S'].unplayed_cards
    assert Card('3C') not in board.hands['W'].unplayed_cards
    assert Card('5C') not in board.hands['N'].unplayed_cards
    context = _card_undo_context(board_id, 'solo')
    assert 'QC' in context['unplayed_card_names']['S']
    assert '3C' in context['unplayed_card_names']['W']
    assert '3D' not in context['unplayed_card_names']['W']
    assert '5C' in context['unplayed_card_names']['N']


def test_undo_duo_w_declarer_w_leader_subsequent_trick_second_cardA():
    board_id = 15
    board = boards[board_id]
    update_board(board_id)
    assert Card('QC') not in board.hands['S'].unplayed_cards
    assert Card('JD') not in board.hands['S'].unplayed_cards
    assert Card('3C') not in board.hands['W'].unplayed_cards
    assert Card('5C') not in board.hands['N'].unplayed_cards
    context = _card_undo_context(board_id, 'duo')
    assert 'JD' in context['unplayed_card_names']['S']
    assert 'QC' in context['unplayed_card_names']['S']
    assert '3C' in context['unplayed_card_names']['W']
    assert '3D' not in context['unplayed_card_names']['W']
    assert '5C' not in context['unplayed_card_names']['N']


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
    assert context['ns_tricks'] == 2
    assert context['ew_tricks'] == 1
