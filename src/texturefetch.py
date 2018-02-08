
'''
This file contains classes for handling
cache reading from the Second Life viewer
texture cache.
'''


import os
import struct
import sys
import weakref

from io import BytesIO
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

TEXTURE_CACHE_BYTE_COUNT = 600


class TextureFetchException(BaseException):
    pass


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
        self.local_texture_cache = TextureCache()

    @property
    def cache(self):
        return self.local_texture_cache

    def set_entries_path(self, entries_file_path):
        '''Sets the entries file path.'''

        if not 'texture.entries' in entries_file_path:
            ERROR('Invalid entries file path "%s"' % entries_file_path)
            raise TextureFetchException('Invalid entries file path "%s"' % entries_file_path)

        self.entries_path = entries_file_path

    def load_entry_file_contents(self):
        ''' Loads the total entry file contents. '''

        with open(self.entries_path, 'rb') as entries_file:
            return BytesIO(entries_file.read())

    def load_cache_file_contents(self):
        ''' Loads the total cache file contents. '''

        with open(self.cache_path, 'rb') as cache_file:
            return BytesIO(cache_file.read())
        

    @property
    def cache_directory(self):
        ''' Returns absolute path to cache directory. '''

        directory = os.path.dirname(self.entries_path)
        return os.path.abspath(directory)

    @property
    def cache_path(self):
        ''' Returns the path to the cache file. '''

        directory = self.cache_directory
        return os.path.join(directory, 'texture.cache')


    @property
    def header_byte_count(self):
        ''' Calculates total header byte count. '''

        total_bytes = (HEADER_ADDRESS_SIZE_BYTE_COUNT +
                       HEADER_ENCODER_VERSION_BYTE_COUNT +
                       HEADER_ENTRY_COUNT_BYTE_COUNT +
                       HEADER_VERSION_BYTE_COUNT)

        return total_bytes


    def load_header(self, entries_file_contents):
        '''Loads the texture cache header.'''

        entries_file_contents.seek(0)
        header = entries_file_contents.read(self.header_byte_count)
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


    def load_entries(self, entries_file_contents, entry_count):
        '''Loads the texture cache entries manifest.'''

        entries_file_contents.seek(self.header_byte_count)
        entries = []
        for i in range(entry_count):
            try:
                entry_bytes = entries_file_contents.read(self.entry_byte_count)
                unpack = struct.unpack(ENTRY_STRUCT_FORMAT, entry_bytes)
            except struct.error:
                WARN('Failed to load entry %i' % i)
                continue
            uuid = format_uuid_from_u8(unpack[0:16])
            new_entry = TextureCacheEntry(uuid, *unpack[16:])
            entries.append(new_entry)

        INFO('Read %i entries from texture cache.' % len(entries))

        if len(entries) != entry_count:

            WARN('Number of read entries (%i) does not match expected count (%i)'
                 % (len(entries), entry_count))

        return entries

    def load_texture_cache(self, max_count=None):
        ''' Loads texture cache in the local/memory cache. '''

        entry_file_contents = self.load_entry_file_contents()
        cache_file_contents = self.load_cache_file_contents()
        header = self.load_header(entry_file_contents)
        entries = self.load_entries(entry_file_contents, header.entry_count)

        for entry in entries:
            uuid = entry.uuid
            try:
                cache = cache_file_contents.read(TEXTURE_CACHE_BYTE_COUNT)
                self.local_texture_cache.add_cache(uuid, cache)
            except IOError as e:
                WARN('Failed to load texture cache for "%s".' % uuid)
                ERROR('', add_exception=True)
                self.local_texture_cache(uuid, None)
            
    def load_texture_body(self, uuid):

        ''' Returns the contents of a texture's body file. '''

        subdir_name = uuid[0]
        cache_dir = self.cache_directory
        texture_file = uuid + '.texture'
        path_to_body = os.path.join(cache, subdir_name,texture_file)

        if not os.path.exists(path_to_body):
            INFO('Did not find texture body for "%s"' % uuid)
            return None

        with open(path_to_body, 'rb') as body_file:
            return body_file.read()


class TextureCache(object):
    
    ''' Container/mapper for UUID and cache contents. '''
    
    def __init__(self):
        self._cache = {}

    def __len__(self):
        return len(self._cache)

    def add_cache(self, uuid, cache):
        ''' Add cache contents for UUID '''
        
        self._cache[uuid] = cache

    def get_cache(self, uuid):
        ''' Get cache contents for UUID '''
        
        try:
            return self._cache[uuid]
        except KeyError:
            WARN('Did not find UUID "%s" in local cache contents.' % uuid)

    def delete_cache(self, uuid):
        ''' Delete cache contents for UUID '''
        
        self._cache.pop(uuid)

    def clear(self):
        ''' Clear cache contents '''
        
        self._cache = {}

class TextureCacheObserver(object):
    pass

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
