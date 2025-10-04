from pathlib import Path
from clipboard import copy

FILE_PATH = Path(Path.home(), 'projects', 'bfg_rest', 'test.pbn')

with open(FILE_PATH, 'r') as f_pbn:
    text = f_pbn.read()
    pbn = text.split('\n')
    copy(str(pbn))
