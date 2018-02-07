
''' 
Contains utility functions .
(logging, formatters, converters, etc.)
'''


def WARN(msg):
    ''' Prints/logs a warning message. '''

    print('!!WARN: %s' % msg)


def ERROR(msg):
    ''' Prints/logs an error message. '''

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
