'''Unit tests for atlantis.rules module'''

from atlantis.rules import RulesError
from atlantis.rules import RulesWarning
from atlantis.rules import GameDefs
from atlantis.rules import Rules

try:
    from unittest.mock import MagicMock  # @UnresolvedImport
except:
    from mock import MagicMock  # @UnresolvedImport
    
import unittest

class TestRules(unittest.TestCase):
    '''Test Rules class'''
        
    def test_check_faction_type(self):
        '''Tests check_faction_type method'''
        r = Rules()
        
        r.game_defs = MagicMock(
            faction_limit_type=GameDefs.FACLIM_FACTION_TYPES,
            faction_points=5)

        # Syntax rules are checked
        self.assertRaisesRegex(Exception, 'war value', r.check_faction_type,
                               war='string', trade=3, magic=2)

        # Too many faction points
        self.assertRaises(RulesError, r.check_faction_type,
                          war=3, trade=3, magic=3)

        # Raises warning when faction limit is not used
        r.game_defs.configure_mock(
            faction_limit_type=GameDefs.FACLIM_UNLIMITED)
        self.assertRaises(RulesWarning, r.check_faction_type,
                          war=3, trade=1, magic=1)
        
        # Valid values raise no exception
        r.game_defs.configure_mock(
            faction_limit_type=GameDefs.FACLIM_FACTION_TYPES)
         
        exceptionRaised = False
        try:
            r.check_faction_type(war=3, trade=0, magic=2)
        except:
            exceptionRaised = True
        finally:
            self.assertFalse(exceptionRaised)

if __name__ == '__main__':
    unittest.main()
