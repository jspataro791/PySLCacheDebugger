
'''
Main entry point for program.
'''

import sys
from PyQt5 import QtCore
from application import Application

# --- PyQt5 missing exception hook fix
if QtCore.QT_VERSION >= 0x50501:
    def excepthook(type_, value, traceback_):
        traceback.print_exception(type_, value, traceback_)
        QtCore.qFatal('')
    sys.excepthook = excepthook

if __name__ == "__main__":
    app = Application()
    app.execute()
