"""Unit tests for module atlantis.gamedata.skill."""

from atlantis.gamedata.skill import Skill, SkillLevel, SkillDays

from io import StringIO

import json
import unittest


class TestSkill(unittest.TestCase):
    """Test Skill class."""
    
    def test_constructor(self):
        """Test Skill constructor.
        
        Test skill constructor.
        
        """
        sk = Skill('COMB', name='combat')
        self.assertEqual(sk.abr, 'COMB')
        self.assertEqual(sk.name, 'combat')

    def test_json_methods(self):
        """Test implementation of JsonSerializable interface."""
        io = StringIO()
        
        sk = Skill('STEA', name='stealth')
        json.dump(sk, io, default=Skill.json_serialize)
        io.seek(0)
        sk_new = Skill.json_deserialize(json.load(io))
        
        self.assertEqual(sk, sk_new)


class TestSkillLevel(unittest.TestCase):
    """Test SkillLevel class."""
    
    def test_constructor(self):
        """Test SkillLevel constructor."""
        sk = SkillLevel('COMB', 'combat', 3)
        self.assertEqual(sk.abr, 'COMB')
        self.assertEqual(sk.name, 'combat')
        self.assertEqual(sk.level, 3)

    def test_json_methods(self):
        """Test implementation of JsonSerializable interface."""
        io = StringIO()
        
        sk = SkillLevel('STEA', 'stealth', 1)
        json.dump(sk, io, default=SkillLevel.json_serialize)
        io.seek(0)
        sk_new = SkillLevel.json_deserialize(json.load(io))
        
        self.assertEqual(sk, sk_new)


class TestSkillDays(unittest.TestCase):
    """Test SkillDays class."""
    
    def test_constructor(self):
        """Test SkillDays constructor."""
        sk = SkillDays('COMB', 'combat', 3, 180)
        self.assertEqual(sk.abr, 'COMB')
        self.assertEqual(sk.name, 'combat')
        self.assertEqual(sk.level, 3)
        self.assertEqual(sk.days, 180)

    def test_json_methods(self):
        """Test implementation of JsonSerializable interface."""
        io = StringIO()
        
        sk = SkillDays('STEA', 'stealth', 1, 60)
        json.dump(sk, io, default=SkillDays.json_serialize)
        io.seek(0)
        sk_new = SkillDays.json_deserialize(json.load(io))
        
        self.assertEqual(sk, sk_new)
        
        io.seek(0)
        io.truncate()
        sk = SkillDays('STEA', 'stealth', 1, 60, 5)
        json.dump(sk, io, default=SkillDays.json_serialize)
        io.seek(0)
        sk_new = SkillDays.json_deserialize(json.load(io))
        
        self.assertEqual(sk, sk_new)


if __name__ == '__main__':
    unittest.main()
