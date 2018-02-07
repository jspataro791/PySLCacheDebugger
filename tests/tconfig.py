
'''
Test configuration and expected values.
'''

import os

# --- config

MOCK_ENTRIES_PATH = os.path.abspath(os.path.join(__file__, "../mock_texturecache/texturecache/texture.entries"))

# --- texture fetch test 

EXPECTED_HEADER_BYTE_COUNT = 44
EXPECTED_ENTRY_BYTE_COUNT = 28
EXPECTED_ENTRY_COUNT = 527