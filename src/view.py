
'''
This file contains the definition for the main window
of the GUI/presentation.
'''


'''
Contains the view/presentation layer.
'''

from appconfig import *
from PyQt5 import QtWidgets, QtCore


class MainWindow(QtWidgets.QMainWindow):

    refresh = QtCore.pyqtSignal()
    set_cache_path = QtCore.pyqtSignal(str)
    
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        # --- members
        self.thumbnail_view = ThumbnailView()
        self.menu_bar = MenuBar()

        # --- signal/slot
        self.menu_bar.open_texture_cache.connect(self.open_texture_cache)
        self.menu_bar.close.connect(self.close)
        self.menu_bar.preferences.connect(self.show_preferences)
        self.menu_bar.refresh.connect(self.refresh_thumbnails)
        
        # --- setup
        self.setWindowTitle(APPLICATION_NAME)
        self.setMenuBar(self.menu_bar)

        # --- layout
        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setLayout(QtWidgets.QVBoxLayout())
        self.central_widget.layout().addWidget(self.thumbnail_view)
        self.setCentralWidget(self.central_widget)

    def open_texture_cache(self):
        pass

    def show_preferences(self):
        pass

    def refresh_thumbnails(self):
        pass

    def save_bitmap(self):
        pass


class ThumbnailView(QtWidgets.QListView):
    
    def __init__(self, parent=None):
        QtWidgets.QListView.__init__(self, parent)

    def add_thumbnail(self, texture_fetch_thumbnail):
        pass

class MenuBar(QtWidgets.QMenuBar):
    
    open_texture_cache = QtCore.pyqtSignal()
    preferences = QtCore.pyqtSignal()
    refresh = QtCore.pyqtSignal()
    close = QtCore.pyqtSignal()
    
    
    def __init__(self, parent=None):
        QtWidgets.QMenuBar.__init__(self, parent)

        # --- menu schema

        menus = {
            'File': [('Open Texture Cache', self.open_texture_cache.emit),
                     (None, None), # sep
                     ('Close', self.close.emit)],

            'Edit': [('Refresh', self.refresh.emit),
                     (None, None), # sep
                     ('Preferences', self.preferences.emit)],

            'Help': []
        }

        self.load_menu_schema(menus)

    def load_menu_schema(self, menu_schema):
        for menu_name, menu_actions in menu_schema.items():
            new_menu = QtWidgets.QMenu(menu_name, self)
            for action_name, action_callback in menu_actions:
                if action_name is None and action_callback is None:
                    new_menu.addSeparator()
                else:
                    new_action = QtWidgets.QAction(action_name, new_menu)
                    new_action.triggered.connect(action_callback)
                    new_menu.addAction(new_action)
            self.addMenu(new_menu)
                
