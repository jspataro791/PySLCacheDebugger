'''
Contains the main backend controller.
'''

from PyQt5 import QtCore
from texturefetch import *
from utils import *


class Backend(QtCore.QObject):
    
    thumbnail_available = QtCore.pyqtSignal(str, object)
    bitmap_available = QtCore.pyqtSignal(TextureFetchBitmap)
    operation_failed = QtCore.pyqtSignal(Exception)

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)

        # --- members
        self.fetcher = TextureCacheFetcher('texture.entries')
        self.fetch_service = TextureCacheFetchService(self.fetcher)

        # --- signal/slot connection
        self.fetch_service.bitmap_available.connect(self.bitmap_available)
        self.fetch_service.thumbnail_available.connect(self.send_fetched_thumbnail)

    def send_fetched_thumbnail(self, texture_fetch_thumbnail):
        uuid = texture_fetch_thumbnail.uuid
        thumbnail = texture_fetch_thumbnail.thumbnail
        self.thumbnail_available.emit(uuid, thumbnail)

    def set_cache_path(self, path):
        INFO('Setting texture cache path as "%s"' % path)
        self.fetch_service.set_fetcher(TextureCacheFetcher(path))

    def refresh(self):
        INFO('Refreshing thumbnails.')
        self.fetch_service.clear_local_cache()
        self.fetch_service.fetch_thumbnails()
