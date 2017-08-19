#!/usr/bin/env python
from IPython.terminal.embed import embed


import run
import asyncio

from get_it_done.models import *
from get_it_done.tasks.gmail_gtd import *
loop = asyncio.get_event_loop()

embed()
