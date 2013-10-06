'''This module defines a set of syntax checking decorators for Atlantis.

If the check performed by any of these decorators fails it raises an
exception. Otherwise the decorated function is called.

'''

def check_unsigned_integer(**kargs):
    '''Checks that arguments are integers greater or equal to 0.

    Raises TypeError if any of the arguments is not an integer, or
    ValueError if it is a negative integer.

    '''
    for k, v in kargs.items():
        try:
            if int(v) != v:
                raise TypeError('{0} value must be an integer'.format(k))
        except ValueError:
            raise TypeError('{0} value must be an integer'.format(k))
        if v < 0:
            raise ValueError('{0} value must be positive'.format(k))

def check_positive_integer(**kargs):
    '''Checks that arguments are integers greater than 0.

    Raises TypeError if any of the arguments is not an integer, or
    ValueError if it is zero or a negative integer.

    '''
    for k, v in kargs.items():
        try:
            if int(v) != v:
                raise TypeError('{0} value must be an integer'.format(k))
        except ValueError:
            raise TypeError('{0} value must be an integer'.format(k))
        if v <= 0:
            raise ValueError('{0} value must be greater than zero'.format(k))
