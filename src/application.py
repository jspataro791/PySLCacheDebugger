
'''
This file contains the main application class which
instantiates the application layers (GUI, backend, etc.)
and readies them for execution.
'''

import sys
from PyQt5 import QtWidgets
from view import MainWindow


class Application(QtWidgets.QApplication):

    def __init__(self):
        QtWidgets.QApplication.__init__(self, sys.argv)

        self.main_window = MainWindow()

    def execute(self):
        self.main_window.show()
        self.exec_()
