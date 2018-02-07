
'''
This file contains the definition for the main window
of the GUI/presentation.
'''

from PyQt5 import QtWidgets


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, menu=None, list_view=None,
                 status_view=None):
        QtWidgets.QMainWindow.__init__(self)

        self.set_menu(menu) 
        self.set_list_view(list_view) 
        self.set_status_view(status_view)

    def set_menu(self, menu):
        if menu is None:
            return
        pass

    def set_list_view(self, list_view):
        if list_view is None:
            return
        pass

    def set_status_view(self, status_view):
        if status_view is None:
            return
        pass
