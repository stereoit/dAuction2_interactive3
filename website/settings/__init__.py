"""
Project settings are separated to
base.py  - basic application specific settings
local.py - settings specific to an installation (this should never be saved in repository)
"""
from os.path import dirname, join, exists
from .base import *

PATH = dirname(__file__)

# overrides anything
if exists(join(PATH, 'local.py')):
    from .local import *

