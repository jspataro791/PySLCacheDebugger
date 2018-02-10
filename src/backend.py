'''
Contains the main backend controller.
'''

from PyQt5 import QtCore
from texturefetch import *

class Backend(QtCore.QObject):
    
    thumbnail_available = QtCore.pyqtSignal(TextureFetchThumbnail)
    bitmap_available = QtCore.pyqtSignal(TextureFetchBitmap)
    operation_failed = QtCore.pyqtSignal(Exception)

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)

        # --- members
        self.fetcher = TextureCacheFetcher('texture.entries')
        self.fetch_service = TextureCacheFetchService(self.fetcher)

        # --- signal/slot connection
        self.fetch_service.bitmap_available.connect(self.bitmap_available)
        self.fetch_service.thumbnail_available.connect(self.thumbnail_available)


    def set_cache_path(self, path):
        try:
            self.fetch_service.set_fetcher(TextureCacheFetcher(path))
        except Exception as e:
            self.operation_failed.emit(e)

    def refresh(self):
        try:
            self.fetch_service.fetch_thumbnails()
        except Exception as e:
            self.operation_failed.emit(e)
