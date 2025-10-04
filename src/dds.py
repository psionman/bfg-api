from endplay.dds import analyse_play,calc_dd_table
from endplay.types import Deal, Player, Denom
from endplay import solve_board

# Generate a random deal
deal = Deal(
    "AK5.843.65.KQT32 T642.J9.QJ8732.A 3.AKQ762.A9.7654 QJ987.T5.KT4.J98",
    first=Player.west)

deal.pprint()
deal.trump = Denom.hearts
table = calc_dd_table(deal)
print(table)
table.pprint()

# for card, tricks in solve_board(deal):
#     print(card, tricks)
