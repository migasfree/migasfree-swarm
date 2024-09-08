import os
from context import ContextLoader, get_stacks

from pathlib import Path


# PROGRAM
# =======

# Cluster Context
cl = ContextLoader()
CONTEXT = cl.context
cl.save()

cl.load_stack(" |".join(get_stacks()))
CONTEXT = cl.context
cl.save_stack()