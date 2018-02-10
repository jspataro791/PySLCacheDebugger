
'''
This file contains the main application class which
instantiates the application layers (GUI, backend, etc.)
and readies them for execution.
'''

import os
import sys
import traceback
import shutil

from PyQt5 import QtCore, QtWidgets

from appconfig import *
from backend import Backend
from view import MainWindow




class Application(QtWidgets.QApplication):

    def __init__(self):
        QtWidgets.QApplication.__init__(self, sys.argv)

        # --- members
        self.presentation = MainWindow()
        self.backend = Backend()
        self.backend_thread = QtCore.QThread()
        self.backend.moveToThread(self.backend_thread)

        # --- signal/slot connections

        # front to back
        self.presentation.set_cache_path.connect(self.backend.set_cache_path)
        self.presentation.refresh.connect(self.backend.refresh)
        self.presentation.rebuild.connect(self.backend.rebuild)
        self.presentation.request_preview.connect(self.backend.preview_request)
        self.presentation.request_save.connect(self.backend.save_bitmap)

        # back to front
        self.backend.thumbnail_available.connect(self.presentation.thumbnail_view.add_thumbnail)
        self.backend.bitmap_available.connect(self.presentation.save_bitmap)
        self.backend.preview_available.connect(self.presentation.show_preview)

        # --- start backend thread
        self.backend_thread.start()

        # --- misc setup
        self.setStyle(APPLICATION_STYLE)


    def execute(self):
        self.presentation.show()
        self.exec_()
