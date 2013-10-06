'''Unit tests for atlantis.faction module'''

from atlantis.rules import GameDefs
from atlantis.rules import RulesError
from atlantis.rules import RulesWarning
from atlantis.faction import Faction
from atlantis import faction  # @UnusedImport

try:
    from unittest.mock import patch  # @UnresolvedImport @UnusedImport
except:
    from mock import patch  # @UnresolvedImport @Reimport
    
import unittest

class TestFaction(unittest.TestCase):
    '''Test Faction class'''

    def test_set_type(self):
        '''Test set_type method'''

        f = Faction()

        # Syntax rules are checked
        self.assertRaisesRegex(Exception, 'trade value', f.set_type,
                               war=1, trade=-1, magic=4)

        # Mocks game defs
        with patch(
                __name__ + '.faction.r.game_defs',
                faction_limit_type=GameDefs.FACLIM_FACTION_TYPES,
                faction_points=5) as gamedefs_mock:

            # Too many faction points
            f.type = { 'war': 1, 'trade': 1, 'magic': 1 }
            self.assertRaises(RulesError, f.set_type,
                              war=2,trade=2,magic=2)
            self.assertEqual(f.type, { 'war': 1, 'trade': 1, 'magic': 1 })
            
            # Faction limit is not used
            gamedefs_mock.configure_mock(
                faction_limit_type=GameDefs.FACLIM_UNLIMITED)
            self.assertRaises(RulesWarning, f.set_type,
                              war=2,trade=1,magic=2)
            self.assertEqual(f.type, { 'war': 1, 'trade': 1, 'magic': 1 })

            # Valid values are provided, faction type set
            gamedefs_mock.configure_mock(
                faction_limit_type=GameDefs.FACLIM_FACTION_TYPES)
            try:
                f.set_type(war=2, trade=1, magic=2)
            except:
                self.fail()
            else:
                self.assertEqual(f.type, { 'war': 2, 'trade': 1, 'magic': 2 })
            

if __name__ == '__main__':
    unittest.main()
