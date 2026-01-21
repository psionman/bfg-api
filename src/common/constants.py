"""Constants for BfG."""
try:
    from enum import StrEnum
except ImportError:
    from backports.strenum import StrEnum
from enum import auto

DEFAULT_SUIT_ORDER = ['S', 'H', 'C', 'D']

MAXIMUM_BIDS_ALLOWED_FOR = 24
MAX_ARCHIVE = 25

YOUR_SELECTION_TEXT = 'Your selection:'
SUGGEST_BID_TEXT = 'Suggested bid:'
WARNINGS = ('alert', 'stop')

PACKAGES = [
    'bfgbidding',
    'bfgcardplay',
    'bfgdealer',
    'bridgeobjects',
]

source_names = [
    'random',
    'set-hands',
    'history',
    'pbn'
    ]

sources = {}
for index, item in enumerate(source_names):
    sources[index] = item
    sources[item] = index

SOURCES = sources

CONTRACT_BASE = 6


class Mode(StrEnum):
    SOLO = auto()
    SOLO_NO_COMMENTS = auto()
    DUO = auto()
