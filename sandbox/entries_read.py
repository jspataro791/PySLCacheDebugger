

'''
SANDBOX FILE
THIS FILE IS NOT SOURCE CODE

Cache header reading is explored here for proof of concept. To be formalized
into actual source.

"texture.entries" contains a general 44-byte header and N 28-byte entry headers
"texture.cache" contains N 600-byte entries
'''

import os
import shutil
import struct
import sys
from array import array
from pprint import pprint

import glymur
import numpy as np
from scipy.misc import imsave

BASE_CACHE_PATH = '..\\tests\\mock_texturecache\\texturecache'


def format_uuid_from_ints(u8_vals):

    fmt = "%02x%02x%02x%02x-%02x%02x-%02x%02x-%02x%02x-%02x%02x%02x%02x%02x%02x"
    vals = tuple(u8_vals)
    return fmt % vals


# --- Open the cache entries file

entries_file = open(
    os.path.join(BASE_CACHE_PATH, 'texture.entries'),
    'rb'
)


# --- Header and entry unpacking

# HEADER STRUCT BYTE LAYOUT
#
#       Version, F32                =   4 bytes
#       AddressSize, U32            =   4 bytes
#       EncoderVersion, ??          =  32 bytes
#       Entries, U32                =   4 bytes
#                                   -----------
#                                      44 bytes
#
# NOTE: The encoder version was found by looking at the binary
# contents and seeing how many empty bytes there were after
# start of the encoder. Turns out this was 32-bytes.

header = entries_file.read(44)
unpacked = struct.unpack('fI32sI', header)

version = '%0.2f' % unpacked[0]
address_size = unpacked[1]
encoder_version = unpacked[2].decode('utf-8').replace('\x00', '')
entry_count = unpacked[3]


print('VERSION:', version)
print('ADDRESS SIZE:', address_size)
print('ENCODER VERSION:', encoder_version)
print('ENTRY COUNT:', entry_count)


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


print('ENTRIES:', len(entries))

# if this doesn't throw, we're golden!
assert len(entries) == entry_count


# --- Read entries from cache file

cache_file = open(
    os.path.join(BASE_CACHE_PATH, 'texture.cache'),
    'rb'
)

chunks = []
for i in range(entry_count):
    chunks.append(cache_file.read(600))

print('CHUNKS:', len(chunks))

assert len(chunks) == entry_count

# --- Find the rest of the cache chunk

# The first 600 bytes of the .j2c is located in the texture.cache file
# while the remainder is inside various .texture files.

bad_path_count = 0
good_path_count = 0
body_chunks = []
for entry in entries:

    uuid = entry[0]
    uuid_start = uuid[0]

    path_to_texture = os.path.join(
        BASE_CACHE_PATH,
        uuid_start,
        uuid + ".texture"
    )

    if not os.path.exists(path_to_texture):
        body_chunks.append(None)
        bad_path_count += 1
    else:
        with open(path_to_texture, 'rb') as texfile:
            body_chunks.append(texfile.read())
            good_path_count += 1

print('TOTAL BODIES:', len(body_chunks))
print('GOOD BODIES:', good_path_count)
print('MISSING BODIES:', bad_path_count)

# --- Combine chunks to form full image

complete_chunks = []
for start, body in zip(chunks, body_chunks):

    if body is not None:
        complete_chunks.append(start + body)
    else:
        complete_chunks.append(start)

print('COMPLETE CHUNKS:', len(complete_chunks))

# --- Check to see if the result of combining chunks matches the
# --- image size in the entry headers.

for entry, chunk in zip(entries, complete_chunks):

    # why is there a 600-byte deficit written
    # into the expected size? looks like
    # it's really the size of the body

    expected_size = entry[1] + 600
    actual_size = len(chunk)

    if expected_size != actual_size:
        print('MISMATCH:', expected_size, actual_size)

    # also be sure the chunk starts with a J2C header (FF, 4F, FF, 51)
    if chunk[0:4].hex() != 'ff4fff51':
        print('BAD START:', chunk[0:4].hex())

# --- Should have everything needed to recreate the image
# --- using JPEG2000.

if not os.path.exists('./output_j2c'):
    os.makedirs('./output_j2c')

if not os.path.exists('output_bmp'):
    os.makedirs('./output_bmp')

for entry, chunk in zip(entries, complete_chunks):

    uuid = entry[0]
    outp_path = os.path.join('output_j2c', uuid + '.j2c')

    with open(outp_path, 'wb') as outfile:
        outfile.write(chunk)

    try:
        img = glymur.Jp2k(outp_path)
        inmem_img = img[:]
        imsave(os.path.join('output_bmp', uuid + '.bmp'), inmem_img)
    except glymur.lib.openjp2.OpenJPEGLibraryError:
        print('Failed to export "%s"' % uuid)


# --- Close open files
entries_file.close()
cache_file.close()
