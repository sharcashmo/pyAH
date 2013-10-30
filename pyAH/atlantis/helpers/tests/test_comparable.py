"""Unit tests for :mod:`atlantis.helpers.json`."""

from atlantis.helpers.comparable import RichComparable

import unittest


class TestRichComparable(unittest.TestCase):
    """Test :class:`~atlantis.helpers.comparable.RichComparable`."""

    def test_comparable(self):
        """Test :class:`TestRichComparable` added functionality."""
        
        class A(RichComparable):
            def __init__(self, a, b, c):
                self.a = a
                self.b = b
                self.c = c
        
        o1 = A(2, [5, 8, 12], 'pedro')
        o2 = A(2, [5, 8, 12], 'pedro')
        
        self.assertEqual(o1, o2)
        
        l1 = [o1]
        l2 = [o2]
        self.assertEqual(l1, l2)

if __name__ == '__main__':
    unittest.main()
