'''
Application configuration
'''




# --- metadata

APPLICATION_NAME = 'PySLCacheDebugger'
APPLICATION_ID = 'pyslcachedebugger'
APPLICATION_STYLE = 'cleanlooks'

# --- debugging/logging

STDO_ENABLED = False
WARN_ENABLED = True
ERROR_ENABLED = True
INFO_ENABLED = True

# --- paths

# --- arg override

import sys
args = sys.argv

if 'debug' in args:
    STDO_ENABLED = True