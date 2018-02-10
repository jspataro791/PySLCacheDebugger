'''
Contains the main backend controller.
'''

from PyQt5 import QtCore

from texturefetch import *
from utils import *


class Backend(QtCore.QObject):
    
    thumbnail_available = QtCore.pyqtSignal(str, object, int)
    bitmap_available = QtCore.pyqtSignal(TextureFetchBitmap)
    preview_available = QtCore.pyqtSignal(str, object)
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
        utime = texture_fetch_thumbnail.time
        self.thumbnail_available.emit(uuid, thumbnail, utime)

    def set_cache_path(self, path):
        INFO('Setting texture cache path as "%s"' % path)
        self.fetch_service.set_fetcher(TextureCacheFetcher(path))

    def preview_request(self, uuid):
        pixmap = self.fetch_service.fetch_bitmap(uuid)
        self.preview_available.emit(uuid, pixmap)

    def full_image_request(self, uuid):
        pixmap = self.fetch_service.fetch_bitmap(uuid)
        return pixmap

    def refresh(self):
        INFO('Refreshing thumbnails.')
        self.fetch_service.fetch_thumbnails(rebuild=False)

    def rebuild(self, seconds):
        INFO('Clearing.')
        self.fetch_service.clear_local_cache()
        self.fetch_service.fetch_thumbnails(max_time=seconds)
