import json
import os
from pathlib import Path

wd = os.getcwd()
p = Path(wd)

p = p.parent / 'worlde-bot'

print(p)