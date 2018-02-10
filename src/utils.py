
''' 
Contains utility functions .
(logging, formatters, converters, etc.)
'''

import io
import os
import sys
from traceback import format_exc

import glymur
import numpy as np
from PyQt5.QtGui import QImage, QPixmap, qRgb
from PyQt5.QtWidgets import QApplication, qApp

from appconfig import *

# --- printing/logging

def WARN(msg):
    ''' Prints/logs a warning message. '''
    if not WARN_ENABLED:
        return
    if not STDO_ENABLED:
        return

    print('!!WARN: %s' % msg)


def ERROR(msg, add_exception=False):
    ''' Prints/logs an error message.'''
    if not ERROR_ENABLED:
        return
    if not STDO_ENABLED:
        return

    if add_exception:
        msg += '\n%s' % format_exc()

    print('!!ERROR: %s' % msg)


def INFO(msg):
    ''' Prints/logs an info message. '''
    if not INFO_ENABLED:
        return
    if not STDO_ENABLED:
        return

    print('??INFO: %s' % msg)


# --- conversion

def format_uuid_from_u8(u8_vals):
    ''' Formats a list of unsigned char representing
    a UUID as a string UUID'''

    fmt = "%02x%02x%02x%02x-%02x%02x-%02x%02x-%02x%02x-%02x%02x%02x%02x%02x%02x"
    vals = tuple(u8_vals)
    return fmt % vals


def convert_j2c_to_qpixmap(uuid, j2c_contents, thumbnail=False):
    '''Converts the raw binary J2C file contents to a Qt pixmap. 
    
    NOTE: A QApplication MUST be instantiated before running this!'''
    
    
    abs_temp_dir = os.path.abspath(TEMPORARY_DIR_PATH)

    if not os.path.exists(abs_temp_dir):
        os.makedirs(abs_temp_dir)

    temp_path = os.path.abspath(os.path.join(TEMPORARY_DIR_PATH, uuid + '.j2c'))
    with open(temp_path, 'wb') as tempfile:
        tempfile.write(j2c_contents)

    try:
        img = glymur.Jp2k(temp_path)
        if thumbnail:
            inmem_img = img[::8,::8]
        else:
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
    
    pixmap = QPixmap(ndarray_to_qimage(inmem_img))

    return pixmap

def ndarray_to_qimage(im, copy=False):
    ''' Converts a Numpy ndarray to a QImage.
    Credit: https://gist.github.com/smex/5287589'''

    try:
        if im is None:
            return QImage()

        if im.dtype == np.uint8:
            if len(im.shape) == 2:
                qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_Indexed8)
                qim.setColorTable(gray_color_table)
                return qim.copy() if copy else qim

            elif len(im.shape) == 3:
                if im.shape[2] == 3:
                    qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_RGB888);
                    return qim.copy() if copy else qim
                elif im.shape[2] == 4:
                    qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_ARGB32);
                    return qim.copy() if copy else qim

        return QImage()
    except Exception as e:
        WARN('Unknown error converting ndarray to pixmap.\n%s' % format_exc())
        return QImage()
