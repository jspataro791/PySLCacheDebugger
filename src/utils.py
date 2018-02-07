
''' 
Contains utility functions .
(logging, formatters, converters, etc.)
'''

from traceback import format_exc


def WARN(msg):
    ''' Prints/logs a warning message. '''

    print('!!WARN: %s' % msg)


def ERROR(msg, add_exception=False):
    ''' Prints/logs an error message.'''

    if add_exception:
        msg += '\n%s' % format_exc()

    print('!!ERROR: %s' % msg)


def INFO(msg):
    ''' Prints/logs an info message. '''

    print('INFO: %msg')


def format_uuid_from_u8(u8_vals):
    ''' Formats a list of unsigned char representing
    a UUID as a string UUID'''

    fmt = "%02x%02x%02x%02x-%02x%02x-%02x%02x-%02x%02x-%02x%02x%02x%02x%02x%02x"
    vals = tuple(u8_vals)
    return fmt % vals
