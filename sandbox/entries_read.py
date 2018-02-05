
import os
import sys
import struct
from array import array
from pprint import pprint

#%% Functions


def format_uuid_from_ints(u8_vals):

    fmt = "%02x%02x%02x%02x-%02x%02x-%02x%02x-%02x%02x-%02x%02x%02x%02x%02x%02x"
    vals = tuple(u8_vals)
    return fmt % vals


#%% Open the cache entries file

entries_file = open(
    '../tests/mock_texturecache/texturecache/texture.entries',
    'rb'
)


#%% Header and entry unpacking

# HEADER STRUCT BYTE LAYOUT
#
#       Version, F32                =   4 bytes
#       AddressSize, U32            =   4 bytes
#       EncoderVersion, ??          =  32 bytes
#       Entries, U32                =   4 bytes
#                                   -----------
#                                      44 bytes
#
# NOTE: The encoder version I found from looking at the binary
# contents and seeing how many empty bytes there were after
# start of the encoder. Turns out this was 32-bytes.

header = entries_file.read(44)
unpacked = struct.unpack('fI32sI', header)

version = '%0.2f' % unpacked[0]
address_size = unpacked[1]
encoder_version = unpacked[2].decode('utf-8').replace('\x00', '')
entry_count = unpacked[3]


pprint({
    'Version': version,
    'Address Size': address_size,
    'Encoder Version': encoder_version,
    'Entry Count': entry_count
})

# ENTRY STRUCT BYTE LAYOUT
#
#       UUID            = 16 bytes
#       ImageSize, S32  =  4 bytes
#       BodySize, S32   =  4 bytes
#       Time, U32       =  4 bytes
#                       ----------
#                         28 bytes
#

entries = []
for i in range(entry_count):
    try:
        entry_bytes = entries_file.read(28)
        unpacked_entry = struct.unpack('16BiiI', entry_bytes)

        new_entry = (
            format_uuid_from_ints(unpacked_entry[0:16]),
            *unpacked_entry[17:]
        )

        entries.append(new_entry)
    except struct.error:
        break

# if this doesn't throw, we're golden!
assert len(entries) == entry_count

#%% Read entries from cache file

cache_file = open(
    '../tests/mock_texturecache/texturecache/texture.cache',
    'rb'
)

cache_file_size = os.path.getsize(
    '../tests/mock_texturecache/texturecache/texture.cache'
)

print(cache_file_size/600)


#%% Close the cache entries file
entries_file.close()
cache_file.close()
