'''Unit tests for atlantis.syntaxrules module'''

from atlantis.syntaxrules import check_unsigned_integer
from atlantis.syntaxrules import check_positive_integer

import unittest

class TestCheckFunctions(unittest.TestCase):
    '''Tests all check_* functions'''

    def test_check_unsigned_integer(self):
        '''Tests check_unsigned_integer function'''
        # Not integer parameter raises TypeError
        self.assertRaisesRegex(TypeError, 'foo value', check_unsigned_integer,
                          bar=3, foo='string', bla=1)
        
        # Negative integer parameter raises ValueError
        self.assertRaisesRegex(ValueError, 'bla value', check_unsigned_integer,
                          bar=1, foo=0, bla=-1)
        
        # Valid values raise no exception
        exceptionRaised = False
        try:
            check_unsigned_integer(bar=1, foo=0, bla=3)
        except:
            exceptionRaised = True
        finally:
            self.assertFalse(exceptionRaised)

    def test_check_positive_integer(self):
        '''Tests check_positive_integer function'''
        # Not integer parameter raises TypeError
        self.assertRaisesRegex(TypeError, 'foo value', check_positive_integer,
                          bar=3, foo='string', bla=1)
        
        # Negative or zero integer parameter raises ValueError
        self.assertRaisesRegex(ValueError, 'bla value', check_positive_integer,
                          bar=1, foo=2, bla=-1)
        self.assertRaisesRegex(ValueError, 'foo value', check_positive_integer,
                          bar=1, foo=0, bla=2)
        
        # Valid values raise no exception
        exceptionRaised = False
        try:
            check_positive_integer(bar=1, foo=1, bla=3)
        except:
            exceptionRaised = True
        finally:
            self.assertFalse(exceptionRaised)

if __name__ == '__main__':
    unittest.main()
