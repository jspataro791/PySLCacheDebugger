
'''
Tests for texture fetching.
'''

import sys
import os
import pytest

src_path = os.path.abspath(os.path.join(__file__, '../../src'))
sys.path.append(src_path)

from tconfig import *

from texturefetch import TextureCacheFetchService
from texturefetch import TextureCacheFetcher

@pytest.fixture
def texture_fetcher():
    fetcher = TextureCacheFetcher(MOCK_ENTRIES_PATH)
    return fetcher

@pytest.fixture
def texture_fetch_service():
    fetcher = TextureCacheFetcher(MOCK_ENTRIES_PATH)
    fetch_service = TextureCacheFetchService(fetcher)
    return fetch_service

def test_fetcher_path(texture_fetcher):
    assert texture_fetcher.entries_path == MOCK_ENTRIES_PATH

def test_fetcher_byte_counters(texture_fetcher):
    assert texture_fetcher.header_byte_count == EXPECTED_HEADER_BYTE_COUNT
    assert texture_fetcher.entry_byte_count == EXPECTED_ENTRY_BYTE_COUNT

def test_load_header(texture_fetcher):
    entries_file_contents = texture_fetcher.load_entry_file_contents()
    header = texture_fetcher.load_header(entries_file_contents)
    assert header.entry_count == EXPECTED_ENTRY_COUNT

def test_load_entries(texture_fetcher):
    entries_file_contents = texture_fetcher.load_entry_file_contents()
    entries = texture_fetcher.load_entries(entries_file_contents, EXPECTED_ENTRY_COUNT)
    assert len(entries) == EXPECTED_ENTRY_COUNT

def test_load_thumbnails(texture_fetch_service):
    thumbnails = []
    def add_thumbnail(thumbnail):
        thumbnails.append(thumbnail)
    texture_fetch_service.thumbnail_available.connect(add_thumbnail)
    texture_fetch_service.fetch_thumbnails()
    assert len(thumbnails) == EXPECTED_ENTRY_COUNT


