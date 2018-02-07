
''' 
Contains utility functions .
(logging, formatters, converters, etc.)
'''

from traceback import format_exc

from appconfig import *


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


def format_uuid_from_u8(u8_vals):
    ''' Formats a list of unsigned char representing
    a UUID as a string UUID'''

    fmt = "%02x%02x%02x%02x-%02x%02x-%02x%02x-%02x%02x-%02x%02x%02x%02x%02x%02x"
    vals = tuple(u8_vals)
    return fmt % vals
