'''Unit tests for atlantis.game module'''

from atlantis.game import Turn
from atlantis.game import Game
from atlantis import game

try:
    from unittest.mock import patch  # @UnresolvedImport
    from unittest.mock import call  # @UnresolvedImport
except:
    from mock import patch  # @UnresolvedImport
    from mock import call  # @UnresolvedImport
import unittest

class TestTurn(unittest.TestCase):
    '''Test Turn class'''

    def test_constructor(self):
        '''Test Turn constructor'''
        
        # No previous turn
        t = Turn(1, 1)
        self.assertEqual(t.year, 1)
        self.assertEqual(t.month, 1)
        self.assertEqual(t.known_skills, set())
        self.assertEqual(t.new_skills, set())

        t.new_skills |= set(['COMB', 'LBOW'])
        self.assertEqual(t.new_skills, set(['COMB', 'LBOW']))

        # Previous turn
        q = Turn(1, 2, t)
        q.new_skills |= set(['RANC', 'LUMB'])
        self.assertEqual(q.year, 1)
        self.assertEqual(q.month, 2)
        self.assertEqual(q.known_skills, set(['COMB', 'LBOW']))
        self.assertEqual(q.new_skills, set(['RANC', 'LUMB']))

        j = Turn(1, 3, q)
        self.assertEqual(j.known_skills, set(['COMB', 'LBOW', 'RANC', 'LUMB']))

    def test_comparators(self):
        '''Test all Turn magic methods for comparisions'''
        t = Turn(1, 1)
        q = Turn(1, 6)
        z = Turn(2, 1)
        j = Turn(1, 1)

        self.assertTrue(t == j)
        
        self.assertTrue(t != q)
        
        self.assertTrue(q < z)
        self.assertFalse(t < j)
        
        self.assertTrue(q <= z)
        self.assertTrue(t <= j)
        
        self.assertTrue(z > q)
        self.assertFalse(j > t)
        
        self.assertTrue(z >= q)
        self.assertTrue(j >= t)

    def test_before(self):
        '''Test before method'''
        q = Turn(1, 6)
        self.assertTrue(q.before(2, 1))
        self.assertFalse(q.before(1, 6))

    def test_compute(self):
        '''Test compute method'''
        t = Turn(1, 3)
        t.new_skills = set(['COMB', 'LBOW'])
        t.known_skills = set(['ENTE'])
        q = Turn(1, 7)
        q.new_skills = set(['ENDU', 'XBOW'])
        q.known_skills = set(['COMB', 'LBOW', 'RANC'])
        s = Turn(1, 9)
        s.new_skills = set(['FORC', 'SPIR'])
        s.known_skills = set(['COMB', 'LBOW', 'RANC', 'ENDU', 'XBOW'])

        v = Turn(1, 5)
        v.new_skills = set(['SPIR', 'FARM'])
        v.known_skills = set(['COMB', 'LBOW', 'HEAL', 'ENTE'])

        q.compute(v)
        s.compute(v)

        self.assertEqual(q.known_skills,
                         set(['COMB', 'LBOW', 'RANC', 'HEAL',
                              'ENTE', 'SPIR', 'FARM']))
        self.assertEqual(q.new_skills,
                         set(['ENDU', 'XBOW']))

        self.assertEqual(s.known_skills,
                         set(['COMB', 'LBOW', 'RANC', 'HEAL',
                              'ENTE', 'SPIR', 'FARM', 'ENDU',
                              'XBOW']))
        self.assertEqual(s.new_skills,
                         set(['FORC']))


class TestGame(unittest.TestCase):
    '''Tests Game class'''
    
    def test_constructor(self):
        '''Test class constructor'''
        g = Game()
        self.assertEqual(g.turns, [])
        self.assertEqual(g.skills, dict())

    def test_set_turn(self):
        '''Test set_turn method'''
        g = Game()
        with patch(__name__ + '.game.Turn', wraps=Turn) as turn_mock:
            with patch(__name__ + '.Turn.compute') as compute_mock:
                g.set_turn(1, 3)
                turn_mock.assert_called_with(1, 3)
                self.assertEqual(len(g.turns), 1)
                self.assertEqual(compute_mock.mock_calls, [])
                turn_mock.reset_mock()
                compute_mock.reset_mock()
                
                g.set_turn(1, 7)
                turn_mock.assert_called_with(1, 7, g.turns[0])
                self.assertEqual(len(g.turns), 2)
                self.assertEqual(compute_mock.mock_calls, [])
                turn_mock.reset_mock()
                compute_mock.reset_mock()
                
                g.set_turn(1, 1)
                turn_mock.assert_called_with(1, 1)
                self.assertEqual(len(g.turns), 3)
                self.assertEqual(compute_mock.mock_calls,
                                 [call(g.turns[0]), call(g.turns[1])])
                turn_mock.reset_mock()
                compute_mock.reset_mock()

                g.set_turn(1, 6)
                turn_mock.assert_called_with(1, 6, g.turns[1])
                self.assertEqual(len(g.turns), 4)
                self.assertEqual(compute_mock.mock_calls,
                                 [call(g.turns[2])])


if __name__ == '__main__':
    unittest.main()
    
