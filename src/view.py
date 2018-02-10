
'''
This file contains the definition for the main window
of the GUI/presentation.
'''


'''
Contains the view/presentation layer.
'''

from PyQt5 import QtCore, QtGui, QtWidgets

from appconfig import *
from utils import *


class MainWindow(QtWidgets.QMainWindow):

    refresh = QtCore.pyqtSignal()
    rebuild = QtCore.pyqtSignal(int)
    set_cache_path = QtCore.pyqtSignal(str)
    request_preview = QtCore.pyqtSignal(str)
    request_save = QtCore.pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        # --- members
        self.thumbnail_view = ThumbnailView()
        self.menu_bar = MenuBar()
        self.status = QtWidgets.QLabel()

        # --- signal/slot
        self.menu_bar.open_texture_cache.connect(self.open_texture_cache)
        self.menu_bar.close.connect(self.close)
        self.menu_bar.refresh.connect(self.refresh_thumbnails)

        self.thumbnail_view.request_preview.connect(self.request_preview)
        self.thumbnail_view.request_save.connect(self.save_bitmap)
        self.thumbnail_view.load_count_changed.connect(self.update_load_count)
        
        # --- setup
        self.setWindowTitle(APPLICATION_NAME)
        self.setMenuBar(self.menu_bar)

        # --- layout
        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setLayout(QtWidgets.QVBoxLayout())
        self.central_widget.layout().addWidget(self.thumbnail_view)
        self.central_widget.layout().addWidget(self.status)
        self.setCentralWidget(self.central_widget)

    def open_texture_cache(self):
        
        path = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open texture cache',
            '', 'Cache Entries File (*.entries)',
        )[0]

        if path:
            self.set_cache_path.emit(path)
            time_window = TimeEntryView()
            time_window.exec_()
            seconds = time_window.seconds
            self.thumbnail_view.clear()
            self.rebuild.emit(seconds)


    def refresh_thumbnails(self):
        self.refresh.emit()

    def show_preview(self, uuid, image):
        INFO('Showing preview for "%s".' % uuid)
        preview_window = TexturePreviewView(uuid, image, self)
        preview_window.show()

    def update_load_count(self, count):
        self.status.setText('Loaded %i Textures' % count)

    def save_bitmap(self, uuid, extension):
        
        if extension == ".bmp":
            save_filter = "Bitmap (*.bmp)"
        elif extension == ".png":
            save_filter = "Portable Network Graphics (*.png)"
        else:
            ERROR('Bad image extension "%s".' % extension)
            return

        path = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Save Image',
            '', save_filter
        )[0]
        if path:
            self.request_save.emit(uuid, path)
        


class ThumbnailView(QtWidgets.QListView):
    
    request_preview = QtCore.pyqtSignal(str)
    request_save = QtCore.pyqtSignal(str, str)
    load_count_changed = QtCore.pyqtSignal(int)
    
    def __init__(self, parent=None):
        QtWidgets.QListView.__init__(self, parent)

        # --- members
        self.local_item_model = QtGui.QStandardItemModel()
        self.sort_proxy = QtCore.QSortFilterProxyModel()
        self.refresher = QtCore.QTimer()
        self.thumbnail_bulk = []
        self.load_count = 0

        # --- signal/slot
        self.doubleClicked.connect(self.handle_double_click)
        

        # --- setup
        #self.sort_proxy.setSourceModel(self.local_item_model)
        #self.sort_proxy.setSortRole(QtCore.Qt.UserRole)
        #self.setModel(self.sort_proxy)
        self.setModel(self.local_item_model)
        self.setIconSize(QtCore.QSize(512,512))
        self.setWordWrap(True)
        self.setTextElideMode(QtCore.Qt.ElideRight)
        self.refresher.timeout.connect(self.purge_bulk)
        self.refresher.start(1000)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)

    def handle_double_click(self, index):
        item = self.local_item_model.itemFromIndex(index)
        if item is None:
            return
        uuid = item.text()
        self.request_preview.emit(uuid)

    def context_menu(self, pos):
        global_pos = self.mapToGlobal(pos)
        index = self.indexAt(pos)
        item = self.local_item_model.itemFromIndex(index)
        INFO('Context menu request on thumbnail view for item "%r"' % item.text())
        if item is None:
            return
        menu = QtWidgets.QMenu()
        menu.addAction('Copy UUID', lambda: self.copy_item_uuid(item))
        menu.addAction('Save (BMP)', lambda: self.request_save.emit(item.text(), '.bmp'))
        menu.addAction('Save (PNG)', lambda: self.request_save.emit(item.text(), '.png'))
        menu.exec_(global_pos)
        self.persist_menu = menu
    
    def copy_item_uuid(self, item):
        copy_str_to_clipboard(item.text())
        

    def clear(self):
        self.local_item_model.clear()
        self.load_count = 0
        self.load_count_changed.emit(self.load_count)

    def add_thumbnail(self, uuid, thumbnail, time):
        
        if thumbnail is None:
            return

        new_model_item = QtGui.QStandardItem(uuid)
        new_model_item.setIcon(QtGui.QIcon(thumbnail))
        new_model_item.setData(time, QtCore.Qt.UserRole)
        new_model_item.setEditable(False)
        self.thumbnail_bulk.append(new_model_item)
        self.load_count += 1
        self.load_count_changed.emit(self.load_count)
    
    def purge_bulk(self):
        for item in self.thumbnail_bulk:
            self.local_item_model.appendRow(item)
        self.thumbnail_bulk = []


class TexturePreviewView(QtWidgets.QDialog):

    def __init__(self, uuid, image, parent=None):
        QtWidgets.QDialog.__init__(self, parent)

        # --- members
        self.image_widget = QtWidgets.QLabel()

        # --- setup
        self.setWindowTitle('Preview: %s' % uuid)
        self.image_widget.setPixmap(image)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.image_widget)




class MenuBar(QtWidgets.QMenuBar):
    
    open_texture_cache = QtCore.pyqtSignal()
    refresh = QtCore.pyqtSignal()
    close = QtCore.pyqtSignal()
    about = QtCore.pyqtSignal()
    
    
    def __init__(self, parent=None):
        QtWidgets.QMenuBar.__init__(self, parent)

        # --- menu schema

        menus = {
            'File': [('Open Texture Cache', self.open_texture_cache.emit),
                     (None, None), # sep
                     ('Refresh', self.refresh.emit),
                     (None, None), # sep
                     ('Close', self.close.emit)],

            'Help': [('About', self.about)]
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

class TimeEntryView(QtWidgets.QDialog):

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)

        # --- members
        self.label = QtWidgets.QLabel('Load texture cache for the last:')
        self.days = QtWidgets.QSpinBox()
        self.hours = QtWidgets.QSpinBox()
        self.minutes = QtWidgets.QSpinBox()
        self.ok = QtWidgets.QPushButton('OK')

        # --- setup
        self.setWindowTitle('Cache time')

        self.days.setSuffix(' days')
        self.hours.setSuffix(' hours')
        self.minutes.setSuffix(' minutes')

        self.days.setMinimum(0)
        self.hours.setMinimum(0)
        self.minutes.setMinimum(0)

        # --- layout
        self.time_layout = QtWidgets.QHBoxLayout()
        self.time_layout.addWidget(self.days)
        self.time_layout.addWidget(self.hours)
        self.time_layout.addWidget(self.minutes)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.label)
        self.layout().addLayout(self.time_layout)
        self.layout().addWidget(self.ok)

        # --- signal/slot
        self.ok.clicked.connect(self.close)



    @property
    def seconds(self):
        return 86400*self.days.value() + 3600*self.hours.value() + 60 * self.minutes.value()
