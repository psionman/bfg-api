def get_board(boards, index):
    board = boards[index]
    played_cards = []
    for trick in board.tricks:
        played_cards += trick.cards
    for key, hand in board.hands.items():
        hand.unplayed_cards = [card for card in hand.cards if card not in played_cards]
    return board
