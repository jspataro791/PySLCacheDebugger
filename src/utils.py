
''' 
Contains utility functions .
(logging, formatters, converters, etc.)
'''

import os
import sys
from traceback import format_exc

import glymur
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, qApp

from appconfig import *

# --- printing/logging

def WARN(msg):
    ''' Prints/logs a warning message. '''
    if not WARN_ENABLED:
        return

    print('!!WARN: %s' % msg)


def ERROR(msg, add_exception=False):
    ''' Prints/logs an error message.'''
    if not ERROR_ENABLED:
        return

    if add_exception:
        msg += '\n%s' % format_exc()

    print('!!ERROR: %s' % msg)


def INFO(msg):
    ''' Prints/logs an info message. '''
    if not INFO_ENABLED:
        return

    print('??INFO: %s' % msg)


# --- conversion

def format_uuid_from_u8(u8_vals):
    ''' Formats a list of unsigned char representing
    a UUID as a string UUID'''

    fmt = "%02x%02x%02x%02x-%02x%02x-%02x%02x-%02x%02x-%02x%02x%02x%02x%02x%02x"
    vals = tuple(u8_vals)
    return fmt % vals

def convert_j2c_to_qpixmap(uuid, j2c_contents, max_width=None):
    '''Converts the raw binary J2C file contents to a Qt pixmap. 
    Must write to disk to be accessed by Glymur library.
    
    NOTE: A QApplication MUST be instantiated before running this!'''

    
    abs_temp_dir = os.path.abspath(TEMPORARY_DIR_PATH)

    if not os.path.exists(abs_temp_dir):
        os.makedirs(abs_temp_dir)

    temp_path = os.path.abspath(os.path.join(TEMPORARY_DIR_PATH, uuid + '.j2c'))
    with open(temp_path, 'wb') as tempfile:
        tempfile.write(j2c_contents)

    try:
        img = glymur.Jp2k(temp_path)
        inmem_img = img[:]
    except Exception:
        WARN('Could not convert "%s" to pixmap. Texture stream may be incomplete.' % uuid)
        try:
            os.remove(temp_path)
        except IOError:
            WARN('Could not remove temporary file at "%s".' % temp_path)
        return None
    try:
        os.remove(temp_path)
    except IOError:
        WARN('Could not remove temporary file at "%s".' % temp_path)
    
    image = QImage(
        inmem_img, 
        inmem_img.shape[1], 
        inmem_img.shape[0], 
        inmem_img.shape[1] * 3,
        QImage.Format_RGB888
    )

    pixmap = QPixmap(image)

    if max_width is not None:
        return pixmap.scaledToWidth(max_width)

    return pixmap
