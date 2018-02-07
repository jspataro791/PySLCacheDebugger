
'''
This file contains classes for handling
cache reading from the Second Life viewer
texture cache.
'''


import os
import struct
import sys
from collections import namedtuple
from traceback import format_exc

import glymur
import numpy as np

from utils import *

HEADER_VERSION_BYTE_COUNT = 4
HEADER_ADDRESS_SIZE_BYTE_COUNT = 4
HEADER_ENCODER_VERSION_BYTE_COUNT = 32
HEADER_ENTRY_COUNT_BYTE_COUNT = 4
HEADER_STRUCT_FORMAT = 'fI32sI'

ENTRY_UUID_BYTE_COUNT = 16
ENTRY_IMAGE_SIZE_BYTE_COUNT = 4
ENTRY_BODY_SIZE_BYTE_COUNT = 4
ENTRY_TIME_BYTE_COUNT = 4
ENTRY_STRUCT_FORMAT = '16BiiI'


class TextureFetchException(BaseException):
    pass


class TextureFetchResponder(object):

    ''' Texture fetch responder. '''

    def __init__(self, data, callback):
        self.data
        self.callback

    def respond(self, result):
        self.callback(result)


class TextureFetchThumbnail(object):

    ''' Texture cache thumbnail data container. '''

    __slots__ = ['entry', 'thumbnail']

    def __init__(self, entry, thumbnail):

        self.entry = entry
        self.thumbnail = thumbnail

    @property
    def uuid(self):
        return self.entry.uuid

    @property
    def time(self):
        return self.entry.time


class TextureFetchBitmap(object):

    ''' Texture cache bitmap data container. '''

    __slots__ = ['entry', 'bitmap']

    def __init__(self, entry, bitmap):

        self.entry = entry
        self.bitmap = bitmap

    @property
    def uuid(self):
        return self.entry.uuid

    @property
    def time(self):
        return self.entry.time


class TextureCacheFetchService(object):

    ''' Handles concurrent fetching of texture cache items.'''

    def __init__(self):
        self.fetcher = None

    def set_cache_path(self, responder):
        '''Sets the cache path.

        Expects a responder containing the path to the
        "texture.entries" file and a callback that accepts
        True if set was successful or a string traceback
        if not.'''

        entries_file_path = responder.data

        try:
            self.fetcher = TextureCacheFetcher(entries_file_path)
            responder.respond(True)
        except Exception:
            responder.respond(format_exc())

    def fetch_thumbails(self, responder):
        '''Fetches texture cache thumbnails and UUID.

        Expects a responder containing the number of
        thumbnails to fetch (None for inf) and a callback
        that can handle each resulting TextureFetchThumbnail
        as they are fetched.'''

        pass

    def fetch_bitmap(self, responder):
        '''Fetches a complete texture cache bitmap.

        Expects a responder containing the UUID of the
        texture and a callback that can handle the resulting
        TextureFetchBitmap when it is fetched.'''

        pass


class TextureCacheFetcher(object):

    '''Handles texture fetch I/O.'''

    def __init__(self, entries_file_path):
        self.set_entries_path(entries_file_path)

    def set_entries_path(self, entries_file_path):
        '''Sets the entries file (texture.entries) path and
        reloads headers and entries manifest.'''

        self.entries_path = entries_file_path
        self.cache_header = self.load_header()
        self.entries_manifest = self.load_entries()

    @property
    def header_byte_count(self):
        ''' Calculates total header byte count. '''

        total_bytes = (HEADER_ADDRESS_SIZE_BYTE_COUNT +
                       HEADER_ENCODER_VERSION_BYTE_COUNT +
                       HEADER_ENTRY_COUNT_BYTE_COUNT +
                       HEADER_VERSION_BYTE_COUNT)

        return total_bytes

    def load_header(self):
        '''Loads the texture cache header.'''

        with open(self.entries_path, 'rb') as entries_file:
            header = entries_file.read(self.header_byte_count)
            try:
                unpacked = struct.unpack(HEADER_STRUCT_FORMAT, header)
            except struct.error:
                ERROR('Could not unpack texture cache header.', add_exception=True)
                raise TextureFetchException('Failed to unpack texture cache header.')
            version = '%0.2f' % unpacked[0]
            address_size = unpacked[1]
            encoder_version = unpacked[2].decode('utf-8').replace('\x00', '')
            entry_count = unpacked[3]

        INFO('Read header from texture cache.'
             ' (VERSION: %s, ADDRESS_SIZE: %i, ENCODER_VERSION: %s, ENTRY_COUNT %i)'
             % (version, address_size, encoder_version, entry_count))

        return TextureCacheHeader(version, address_size, encoder_version, entry_count)

    @property
    def entry_byte_count(self):
        ''' Calculates total entry byte count. '''

        total_bytes = (ENTRY_BODY_SIZE_BYTE_COUNT +
                       ENTRY_IMAGE_SIZE_BYTE_COUNT +
                       ENTRY_TIME_BYTE_COUNT +
                       ENTRY_UUID_BYTE_COUNT)

        return total_bytes

    def load_entries(self):
        '''Loads the texture cache entries manifest.'''

        with open(self.entries_path, 'rb') as entries_file:
            __ = entries_file.read(self.header_byte_count)
            entry_count = self.header.entry_count
            entries = []
            for i in range(entry_count):
                try:
                    entry_bytes = entries_file.read(self.entry_byte_count)
                    unpack = struct.unpack(ENTRY_STRUCT_FORMAT, entry_bytes)
                except struct.error:
                    WARN('Failed to load entry %i' % i)
                    continue
                uuid = format_uuid_from_u8(unpack[0:16])
                new_entry = TextureCacheEntry(uuid, *unpack[17])
                entries.append(new_entry)

        INFO('Read %i entries from texture cache.' % len(entries))

        if len(entries) != entry_count:

            WARN('Number of read entries (%i) does not match expected count (%i)'
                 % (len(entries), entry_count))

        return entries


class TextureCacheHeader(object):

    ''' Cache header data container. '''

    def __init__(self, version, address_size,
                 encoder_version, entry_count):

        self.version = version
        self.address_size = address_size
        self.encoder_version = encoder_version
        self.entry_count = entry_count


class TextureCacheEntry(object):

    ''' Cache entry data container. '''

    __slots__ = ['uuid', 'body_size', 'image_size', 'time']

    def __init__(self, uuid, body_size, image_size, time):

        self.uuid = uuid
        self.body_size = body_size
        self.image_size = image_size
        self.time = time
