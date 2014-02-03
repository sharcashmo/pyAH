"""Unit tests for atlantis.reportparser module"""

from atlantis.parsers.reportparser import ReportReader
from atlantis.parsers.reportparser import ReportParser
from atlantis.parsers import reportparser  # @UnusedImport

from atlantis.gamedata.item import Item, ItemAmount, ItemMarket, ItemUnit
from atlantis.gamedata.skill import Skill, SkillDays

try:
    from unittest.mock import patch  # @UnresolvedImport @UnusedImport
    from unittest.mock import mock_open  # @UnresolvedImport @UnusedImport
    from unittest.mock import MagicMock  # @UnresolvedImport @UnusedImport
    from unittest import mock  # @UnresolvedImport @UnusedImport
except:
    from mock import patch  # @UnresolvedImport @Reimport
    from mock import mock_open  # @UnresolvedImport @Reimport
    from mock import MagicMock  # @UnresolvedImport @Reimport
    import mock  # @UnresolvedImport @Reimport

import unittest


class TestReportReader(unittest.TestCase):
    """Test ReportReader class
    
    Tests run by this class are:
    test_nowrapped_lines  Test report reader when there're no wrapped
                          lines
    test_wrapped_lines    Test real report with several wrapped lines
    
    """

    def test_nowrapped_lines(self):
        """Tests the simplest case: no wrapped lines.

        Lines will be returned the same way they are in the file.

        """
        
        m = mock_open()
        lines = ['Atlantis Report For:\n',
                 'Mathoyoh (3) (War 2, Trade 1, Magic 2)\n',
                 'July, Year 2\n',
                 '\n',
                 'Atlantis Engine Version: 5.1.0\n',
                 'Havilah, Version: 1.0.0 (beta)\n',
                 '\n',
                 'REMINDER: You have not set a password for your faction!\n',
                 '']
        m().readline = MagicMock(side_effect=lines)
        with patch(__name__ + '.open', m, create=True):
            with open('report.x') as f:
                reader = ReportReader(f)
                for l, r in zip(reader, lines):
                    self.assertEqual(l, r)

    def test_wrapped_lines(self):
        """Test a more complicated case.

        This includes:
        - Wrapped lines (events)
        - Hex report, with separator and Exits line.
        - An object.
        - Some wrapped units in the hex
        - Template orders (shouldn't be unwrapped)

        """
        
        lines = [
            'Atlantis Report For:\n',
            'Mathoyoh (3) (War 2, Trade 1, Magic 2)\n',
            'July, Year 2\n',
            '\n',
            'Events during turn:\n',
            'Comb (557): Gives 100 silver [SILV] to Ranc (615).\n',
            'Lumb master (526): Gives 19 silver [SILV] to Lumb (679).\n',
            'SQ Bidswaul B - Lbow (560): Gives 533 silver [SILV] to Obse '
            'master\n',
            '  (669).\n',
            'Sail (563): Gives 6 silver [SILV] to Lumb (679).\n',
            '\n',
            'forest (13,41) in Bidswaul, 1248 peasants (wood elves), $624.\n',
            '------------------------------------------------------------\n',
            '  It was monsoon season last month; it will be clear next '
            'month.\n',
            '  Wages: $12.5 (Max: $489).\n',
            '  Wanted: none.\n',
            '  For Sale: 49 wood elves [WELF] at $50, 9 leaders [LEAD] at '
            '$100.\n',
            '  Entertainment available: $30.\n',
            '  Products: 36 grain [GRAI], 43 wood [WOOD], 11 furs [FUR], 18 '
            'herbs\n',
            '    [HERB].\n',
            '\n',
            'Exits:\n',
            '  North : forest (13,39) in Bidswaul, contains Bunrulwick '
            '[village].\n',
            '  Northeast : forest (14,40) in Bidswaul.\n',
            '  Southeast : forest (14,42) in Bidswaul.\n',
            '  South : ocean (13,43) in Havilah Ocean.\n',
            '  Southwest : ocean (12,42) in Havilah Ocean.\n',
            '  Northwest : ocean (12,40) in Havilah Ocean.\n',
            '\n',
            '* Lumb master (494), Mathoyoh (3), avoiding, behind, won\'t '
            'cross\n',
            '  water, leader [LEAD], 10 wood [WOOD]. Weight: 60. Capacity:\n',
            '  0/0/15/0. Skills: lumberjack [LUMB] 4 (345).\n',
            '\n',
            '+ Building [1] : Timber Yard.\n',
            '  * Lumb (654), Mathoyoh (3), avoiding, behind, won\'t cross '
            'water,\n',
            '    wood elf [WELF], axe [AXE]. Weight: 11. '
            'Capacity: 0/0/15/0.\n',
            '    Skills: lumberjack [LUMB] 3 (180).\n',
            '\n',
            'Orders Template (Short Format):\n',
            'unit 494\n',
            'form 1\n',
            '  name unit Child\n',
            '  buy 10 welf\n',
            '  @study lumb\n',
            '']
        expected_output = [
            'Atlantis Report For:\n',
            'Mathoyoh (3) (War 2, Trade 1, Magic 2)\n',
            'July, Year 2\n',
            '\n',
            'Events during turn:\n',
            'Comb (557): Gives 100 silver [SILV] to Ranc (615).\n',
            'Lumb master (526): Gives 19 silver [SILV] to Lumb (679).\n',
            'SQ Bidswaul B - Lbow (560): Gives 533 silver [SILV] to Obse '
            'master (669).\n',
            'Sail (563): Gives 6 silver [SILV] to Lumb (679).\n',
            '\n',
            'forest (13,41) in Bidswaul, 1248 peasants (wood elves), $624.\n',
            '------------------------------------------------------------\n',
            '  It was monsoon season last month; it will be clear next '
            'month.\n',
            '  Wages: $12.5 (Max: $489).\n',
            '  Wanted: none.\n',
            '  For Sale: 49 wood elves [WELF] at $50, 9 leaders [LEAD] at '
            '$100.\n',
            '  Entertainment available: $30.\n',
            '  Products: 36 grain [GRAI], 43 wood [WOOD], 11 furs [FUR], 18 '
            'herbs [HERB].\n',
            '\n',
            'Exits:\n',
            '  North : forest (13,39) in Bidswaul, contains Bunrulwick '
            '[village].\n',
            '  Northeast : forest (14,40) in Bidswaul.\n',
            '  Southeast : forest (14,42) in Bidswaul.\n',
            '  South : ocean (13,43) in Havilah Ocean.\n',
            '  Southwest : ocean (12,42) in Havilah Ocean.\n',
            '  Northwest : ocean (12,40) in Havilah Ocean.\n',
            '\n',
            '* Lumb master (494), Mathoyoh (3), avoiding, behind, won\'t '
            'cross water, leader [LEAD], 10 wood [WOOD]. Weight: 60. Capacity: '
            '0/0/15/0. Skills: lumberjack [LUMB] 4 (345).\n',
            '\n',
            '+ Building [1] : Timber Yard.\n',
            '  * Lumb (654), Mathoyoh (3), avoiding, behind, won\'t cross '
            'water, wood elf [WELF], axe [AXE]. Weight: 11. Capacity: '
            '0/0/15/0. Skills: lumberjack [LUMB] 3 (180).\n',
            '\n',
            'Orders Template (Short Format):\n',
            'unit 494\n',
            'form 1\n',
            '  name unit Child\n',
            '  buy 10 welf\n',
            '  @study lumb\n',
            '']
        m = mock_open()
        m().readline = MagicMock(side_effect=lines)
        with patch(__name__ + '.open', m, create=True):
            with open('report.x') as f:
                reader = ReportReader(f)
                for l, r in zip(reader, expected_output):
                    self.assertEqual(l, r)

class TestReportParser(unittest.TestCase):
    """Unit tests for ReportParser class"""
    
    def test_parse_battle(self):
        """Test parse_battle method"""
        with patch(__name__ + '.reportparser.ReportConsumer') as consumer_mock:
            parser = ReportParser(consumer_mock())
            
            # Battle start
            b = 'SQ Decec A - Ridi (512) attacks City Guard (65) in plain ' \
                '(18,38) in Decec!'
            parser.parse_battle(b)    
            consumer_mock().battle.assert_called_with(
                    att={'num': 512, 'name': 'SQ Decec A - Ridi'},
                    tar={'num': 65, 'name': 'City Guard'},
                    reg={'xloc': 18, 'yloc': 38, 'name': 'Decec',
                         'type': 'plain'})
            
            # Assassination attempt
            # TODO
            
            # Side
            b = 'Attackers:'
            consumer_mock.reset_mock()
            parser.parse_battle(b)    
            consumer_mock().battle_side.assert_called_with(side='attacker')
            
            # Battle unit
            b = 'Mage eart (397), behind, leader [LEAD], 2 wolves [WOLF] ' \
                '(Combat 2/2, Attacks 1, Hits 1, Tactics 1), sword [SWOR], ' \
                'tactics 3.'
            consumer_mock.reset_mock()
            parser.parse_battle(b)    
            consumer_mock().battle_side_unit.assert_called_with(
                    num=397, name='Mage eart', behind=True,
                    items=[{'amt': 1, 'abr': 'LEAD', 'name': 'leader'},
                           {'amt': 2, 'abr': 'WOLF', 'names': 'wolves',
                            'monster': {'attackLevel': 2, 'defense': 2,
                                        'numAttacks': 1, 'hits': 1,
                                        'tactics': 1}},
                           {'amt': 1, 'abr': 'SWOR', 'name': 'sword'}],
                    skills=[{'name': 'tactics', 'level': 3}])
            
            b = 'Mage eart (397) Mathoyoh (13), behind, leader [LEAD], 2 ' \
                'wolves [WOLF] (Combat 2/2, Attacks 1, Hits 1, Tactics 1), ' \
                'sword [SWOR], tactics 3.'
            consumer_mock.reset_mock()
            parser.parse_battle(b)    
            consumer_mock().battle_side_unit.assert_called_with(
                    num=397, name='Mage eart', behind=True,
                    faction={'num': 13, 'name': 'Mathoyoh'},
                    items=[{'amt': 1, 'abr': 'LEAD', 'name': 'leader'},
                           {'amt': 2, 'abr': 'WOLF', 'names': 'wolves',
                            'monster': {'attackLevel': 2, 'defense': 2,
                                        'numAttacks': 1, 'hits': 1,
                                        'tactics': 1}},
                           {'amt': 1, 'abr': 'SWOR', 'name': 'sword'}],
                    skills=[{'name': 'tactics', 'level': 3}])
            
            # Free round
            b = 'Mage demo/necr (617) gets a free round of attacks.'
            consumer_mock.reset_mock()
            parser.parse_battle(b)    
            consumer_mock().battle_round.assert_called_with(
                    unit={'num':617, 'name':'Mage demo/necr'}, num='free')
            
            # Normal round
            b = 'Round 1:'
            consumer_mock.reset_mock()
            parser.parse_battle(b)    
            consumer_mock().battle_round.assert_called_with(
                    num=1)
            
            # Cast shield
            b = 'Mage eart (397) casts Force Shield.'
            consumer_mock.reset_mock()
            parser.parse_battle(b)    
            consumer_mock().battle_round_shield.assert_called_with(
                    unit={'num': 397, 'name': 'Mage eart'},
                    shielddesc='Force Shield')
            
            # Special attack, deflected
            b = 'Mage eart (397) shoots a Fireball, but it is deflected.'
            consumer_mock.reset_mock()
            parser.parse_battle(b)    
            consumer_mock().battle_round_special.assert_called_with(
                    soldier={'num': 397, 'name': 'Mage eart'},
                    spelldesc='shoots a Fireball', deflected=True)
            
            # Special attack, hits
            b = 'Other mage (314) strikes fear into enemy mounts, causing 8 ' \
                'mounts to panic.'
            consumer_mock.reset_mock()
            parser.parse_battle(b)    
            consumer_mock().battle_round_special.assert_called_with(
                    soldier={'num': 314, 'name': 'Other mage'},
                    spelldesc='strikes fear into enemy mounts',
                    spelldesc2='causing', tot=8, spelltarget='mounts to panic')
            
            # Regenerate
            b = 'Big monster (666) regenerates 8 hits bringing it to 272/300.'
            consumer_mock.reset_mock()
            parser.parse_battle(b)    
            consumer_mock().battle_round_regenerate.assert_called_with(
                    soldier={'num': 666, 'name': 'Big monster'},
                    regenerate='regenerate', hits=272, maxhits=300, damage=8)
            
            b = 'Big monster (666) takes 8 hits bringing it to 252/300.'
            consumer_mock.reset_mock()
            parser.parse_battle(b)    
            consumer_mock().battle_round_regenerate.assert_called_with(
                    soldier={'num': 666, 'name': 'Big monster'},
                    regenerate='take', hits=252, maxhits=300, damage=8)
            
            b = 'Big monster (666) takes no hits leaving it at 122/300.'
            consumer_mock.reset_mock()
            parser.parse_battle(b)    
            consumer_mock().battle_round_regenerate.assert_called_with(
                    soldier={'num': 666, 'name': 'Big monster'},
                    regenerate='take', hits=122, maxhits=300, damage=0)
            
            # Loses
            b = 'City Guard (67) loses 13.'
            consumer_mock.reset_mock()
            parser.parse_battle(b)    
            consumer_mock().battle_loses.assert_called_with(
                    unit={'num': 67, 'name': 'City Guard'}, loses=13)
            
            # End
            b = 'City Guard (67) is routed!'
            consumer_mock.reset_mock()
            parser.parse_battle(b)    
            consumer_mock().battle_end.assert_called_with(
                    unit={'num': 67, 'name': 'City Guard'}, result='routed')
            
            b = 'City Guard (67) is destroyed!'
            consumer_mock.reset_mock()
            parser.parse_battle(b)    
            consumer_mock().battle_end.assert_called_with(
                    unit={'num': 67, 'name': 'City Guard'}, result='destroyed')
            
            b = 'The battle ends indecisively.'
            consumer_mock.reset_mock()
            parser.parse_battle(b)    
            consumer_mock().battle_end.assert_called_with(result='tie')
            
            # Casualties
            b = 'Total Casualties:'
            consumer_mock.reset_mock()
            parser.parse_battle(b)    
            consumer_mock().battle_casualties.assert_called_with()
            
            # Heals
            b = 'Curandero (27) heals 6.'
            consumer_mock.reset_mock()
            parser.parse_battle(b)    
            consumer_mock().battle_casualties_heal.assert_called_with(
                    unit={'num': 27, 'name': 'Curandero'}, heal=6)
            
            # Damaged units
            b = 'Damaged units: 465, 462, 463, 651, 469.'
            consumer_mock.reset_mock()
            parser.parse_battle(b)
            consumer_mock().battle_casualties_units.assert_called_with(
                    units=[{'num': 465}, {'num': 462}, {'num': 463},
                           {'num': 651}, {'num': 469}])
            
            # Spoils
            b = 'Spoils: 18 swords [SWOR], 899 silver [SILV].'
            consumer_mock.reset_mock()
            parser.parse_battle(b)
            consumer_mock().battle_spoils.assert_called_with(
                    items=[{'abr': 'SWOR', 'names': 'swords', 'amt': 18},
                           {'abr': 'SILV', 'names': 'silver', 'amt': 899}])
            
            # Assassination
            b = 'Easy Target (43) is assassinated in plain (18,38) in Decec!'
            consumer_mock.reset_mock()
            parser.parse_battle(b)
            consumer_mock().battle.assert_called_with(ass=True,
                    tar={'num': 43, 'name': 'Easy Target'},
                    reg={'xloc': 18, 'yloc': 38, 'name': 'Decec',
                         'type': 'plain'})
            
            # Raised undead
            b = '3 skeletons [SKEL] and undead [UNDE] rise from the grave ' \
                'to join Wandering Monster (123).'
            consumer_mock.reset_mock()
            parser.parse_battle(b)
            consumer_mock().battle_raise.assert_called_with(
                    undead=[{'amt': 3, 'abr': 'SKEL', 'names': 'skeletons'},
                            {'amt': 1, 'abr': 'UNDE', 'name': 'undead'}],
                    unit={'num': 123, 'name': 'Wandering Monster'})
            
            b = 'skeleton [SKEL] rise from the grave to seek vengeance.'
            consumer_mock.reset_mock()
            parser.parse_battle(b)
            consumer_mock().battle_raise.assert_called_with(
                    undead=[{'amt': 1, 'abr': 'SKEL', 'name': 'skeleton'}])
    
    def test_parse_faction(self):
        """Test parse_faction method"""
        with patch(__name__ + '.reportparser.ReportConsumer') as consumer_mock:
            parser = ReportParser(consumer_mock())
            
            f = 'Mathoyoh (3) (War 3, Trade 1, Magic 1)'
            parser.parse_faction(f)
            consumer_mock().faction.assert_called_with(
                    name='Mathoyoh', num=3,
                    factype={'war': 3, 'trade': 1, 'magic': 1})
            
            f = 'July, Year 1'
            consumer_mock.reset_mock()
            parser.parse_faction(f)
            consumer_mock().faction_date.assert_called_with(
                    year=1, month='July')
            
            f = 'Atlantis Engine Version: 5.1.0'
            consumer_mock.reset_mock()
            parser.parse_faction(f)
            consumer_mock().atlantis_version.assert_called_with(
                    version='5.1.0')
            
            f = 'Havilah, Version: 1.0.0 (beta)'
            consumer_mock.reset_mock()
            parser.parse_faction(f)
            consumer_mock().atlantis_rules.assert_called_with(
                    name='Havilah', version='1.0.0 (beta)')
            
            f = 'Note: The Times is not being sent to you.'
            consumer_mock.reset_mock()
            parser.parse_faction(f)
            consumer_mock().faction_warn.assert_called_with(notimes=True)
            
            f = 'REMINDER: You have not set a password for your faction!'
            consumer_mock.reset_mock()
            parser.parse_faction(f)
            consumer_mock().faction_warn.assert_called_with(nopassword=True)
            
            f = 'WARNING: You have 3 turns until your faction is ' \
                'automatically removed due to inactivity!'
            consumer_mock.reset_mock()
            parser.parse_faction(f)
            consumer_mock().faction_warn.assert_called_with(inactive=3)
                
            f = 'You restarted your faction this turn. This faction has been ' \
                'removed, and a new faction has been started for you. (Your ' \
                'new faction report will come in a separate message.)'
            consumer_mock.reset_mock()
            parser.parse_faction(f)
            consumer_mock().faction_warn.assert_called_with(
                    quitgame='restart')
                
            f = 'I\'m sorry, the game has ended. Better luck in the next ' \
                'game you play!'
            consumer_mock.reset_mock()
            parser.parse_faction(f)
            consumer_mock().faction_warn.assert_called_with(
                    quitgame='gameover')
                
            f = 'Congratulations, you have won the game!'
            consumer_mock.reset_mock()
            parser.parse_faction(f)
            consumer_mock().faction_warn.assert_called_with(
                    quitgame='won')
            
            f = 'I\'m sorry, your faction has been eliminated.'
            consumer_mock.reset_mock()
            parser.parse_faction(f)
            consumer_mock().faction_warn.assert_called_with(
                    quitgame='eliminated')
            
            f = 'Tax Regions: 5 (40)'
            consumer_mock.reset_mock()
            parser.parse_faction(f)
            consumer_mock().faction_status.assert_called_with(
                    what='Tax Regions', num=5, allowed=40)
            
            f = 'Trade Regions: 0 (10)'
            consumer_mock.reset_mock()
            parser.parse_faction(f)
            consumer_mock().faction_status.assert_called_with(
                    what='Trade Regions', num=0, allowed=10)
            
            f = 'Mages: 1 (1)'
            consumer_mock.reset_mock()
            parser.parse_faction(f)
            consumer_mock().faction_status.assert_called_with(
                    what='Mages', num=1, allowed=1)
            
            f = 'Acolytes: 0 (3)'
            consumer_mock.reset_mock()
            parser.parse_faction(f)
            consumer_mock().faction_status.assert_called_with(
                    what='Acolytes', num=0, allowed=3)
            
            f = 'Declared Attitudes (default Neutral):'
            consumer_mock.reset_mock()
            parser.parse_faction(f)
            consumer_mock().faction_attitudes.assert_called_with(
                    default='neutral')
            
            f = 'Hostile : none.'
            consumer_mock.reset_mock()
            parser.parse_faction(f)
            consumer_mock().faction_attitudes.assert_called_with(
                    hostile=[])
            
            f = 'Unfriendly : Creatures (2).'
            consumer_mock.reset_mock()
            parser.parse_faction(f)
            consumer_mock().faction_attitudes.assert_called_with(
                    unfriendly=[{'num': 2, 'name': 'Creatures'}])
            
            f = 'Unclaimed silver: 430.'
            consumer_mock.reset_mock()
            parser.parse_faction(f)
            consumer_mock().faction_unclaimed.assert_called_with(
                    unclaimed=430)
        
    def test_parse_event(self):
        """Test parse_event method"""
        with patch(__name__ + '.reportparser.ReportConsumer') as consumer_mock:
            parser = ReportParser(consumer_mock())
            
            e = 'Mage eart (397): Casts Clear Skies.'
            parser.parse_event('event', e)    
            consumer_mock().faction_event.assert_called_with(
                    message_type='event', message='Casts Clear Skies',
                    unit={'num': 397, 'name': 'Mage eart'})
    
    def test_parse_skill(self):
        """Tests parse_skill method"""
        with patch(__name__ + '.reportparser.ReportConsumer') as consumer_mock:
            parser = ReportParser(consumer_mock())
            
            skill = 'mining [MINI] 4: No skill report.'
            parser.parse_skill(skill)
            consumer_mock().skill.assert_called_with(
                    name='mining', abbr='MINI', level=4,
                    descr='No skill report.')
            
            # Resource production skill
            skill = 'lumberjack [LUMB] 1: This skill deals with all aspects ' \
                    'of various wood production. Wood is most often found in ' \
                    'forests, but may also be found elsewhere. A unit with ' \
                    'this skill may PRODUCE wood [WOOD] at a rate of 1 per ' \
                    'man-month. This skill costs 10 silver per month of study.'
            consumer_mock.reset_mock()
            parser.parse_skill(skill)
            consumer_mock().skill.assert_called_with(
                    name='lumberjack', abbr='LUMB', level=1, descr=mock.ANY,
                    # skilldescr is often given only at level 1
                    skilldescr='This skill deals with all aspects of various ' \
                               'wood production. Wood is most often found in ' \
                               'forests, but may also be found elsewhere.',
                    cost=10, # Only level 1 skills state their cost
                    production={'command': 'produce',
                                'items': [{'abr': 'WOOD', 'names': 'wood',
                                           'pOut': 1, 'pMonths': 1}]})
            
            # Resource production, higher level, advanced items, and buildings
            skill = 'lumberjack [LUMB] 3: A unit with this skill may PRODUCE ' \
                    'ironwood [IRWD] at a rate of 1 per man-month. A unit ' \
                    'with this skill is able to determine if a region ' \
                    'contains ironwood. A unit with this skill may BUILD a ' \
                    'Timber Yard from 10 wood [WOOD] or stone [STON] or a ' \
                    'Forest Preserve from 20 ironwood [IRWD].'
            consumer_mock.reset_mock()
            parser.parse_skill(skill)
            consumer_mock().skill.assert_called_with(
                    name='lumberjack', abbr='LUMB', level=3, descr=mock.ANY,
                    production={'command': 'produce',
                                'items': [{'abr': 'IRWD', 'names': 'ironwood',
                                           'pOut': 1, 'pMonths': 1}]},
                    discovers=[{'names': 'ironwood'}],
                    builds=[
                            {'name': 'Timber Yard', 'cost': 10,
                             'item': [{'abr': 'WOOD', 'name': 'wood'},
                                      {'abr': 'STON', 'name': 'stone'}]},
                            {'name': 'Forest Preserve', 'cost': 20,
                             'item': [{'abr': 'IRWD', 'name': 'ironwood'}]}])
            
            # Resource and item production
            skill = 'herb lore [HERB] 1: This skill deals with all aspects ' \
                    'of herb production. A unit with this skill may PRODUCE ' \
                    'herbs [HERB] at a rate of 1 per man-month, lassoes ' \
                    '[LASS] from herb [HERB] at a rate of 1 per man-month, ' \
                    'and bags [BAG] from herb [HERB] at a rate of 1 per ' \
                    'man-month. This skill costs 10 silver per month of study.'
            consumer_mock.reset_mock()
            parser.parse_skill(skill)
            consumer_mock().skill.assert_called_with(
                    name='herb lore', abbr='HERB', level=1, descr=mock.ANY,
                    # skilldescr is often given only at level 1
                    skilldescr='This skill deals with all aspects of herb ' \
                               'production.',
                    cost=10, # Only level 1 skills state their cost
                    production={'command': 'produce',
                                'items': [{'abr': 'HERB', 'names': 'herbs',
                                           'pOut': 1, 'pMonths': 1},
                                          {'abr': 'LASS', 'names': 'lassoes',
                                           'pOut': 1, 'pMonths': 1,
                                           'pInput': [{'abr': 'HERB',
                                                       'name': 'herb',
                                                       'amt': 1}]},
                                          {'abr': 'BAG', 'names': 'bags',
                                           'pOut': 1, 'pMonths': 1,
                                           'pInput': [{'abr': 'HERB',
                                                       'name': 'herb',
                                                       'amt': 1}]}
                                          ]
                                })
            
            # Item production, with two input items and slower rate
            skill = 'weaponsmith [WEAP] 2: A unit with this skill may ' \
                    'PRODUCE battle axes [BAXE] from iron [IRON] and wood ' \
                    '[WOOD] at a rate of 1 per 2 man-months.'
            consumer_mock.reset_mock()
            parser.parse_skill(skill)
            consumer_mock().skill.assert_called_with(
                    name='weaponsmith', abbr='WEAP', level=2, descr=mock.ANY,
                    production={
                            'command': 'produce',
                            'items': [{'abr': 'BAXE', 'names': 'battle axes',
                                       'pOut': 1, 'pMonths': 2,
                                       'pInput': [{'abr': 'IRON',
                                                   'name': 'iron',
                                                   'amt': 1},
                                                  {'abr': 'WOOD',
                                                   'name': 'wood',
                                                   'amt': 1}]
                                       }]
                                })
            
            # Item production, input item is plural
            skill = 'carpenter [CARP] 5: A unit with this skill may PRODUCE ' \
                    'gliders [GLID] from 2 floater hides [FLOA] at a rate of ' \
                    '1 per 2 man-months.'
            consumer_mock.reset_mock()
            parser.parse_skill(skill)
            consumer_mock().skill.assert_called_with(
                    name='carpenter', abbr='CARP', level=5, descr=mock.ANY,
                    production={
                            'command': 'produce',
                            'items': [{'abr': 'GLID', 'names': 'gliders',
                                       'pOut': 1, 'pMonths': 2,
                                       'pInput': [{'abr': 'FLOA',
                                                   'names': 'floater hides',
                                                   'amt': 2}]
                                       }]
                                })
            
            # Building skill
            skill = 'building [BUIL] 1: This skill deals with the ' \
                    'construction of fortifications, roads and other ' \
                    'buildings, except for most trade structures. A unit ' \
                    'with this skill may BUILD a Tower from 10 stone [STON], ' \
                    'a Fort from 40 stone [STON], a Castle from 160 stone ' \
                    '[STON] or a Citadel from 640 stone [STON]. This skill ' \
                    'costs 10 silver per month of study.'
            consumer_mock.reset_mock()
            parser.parse_skill(skill)
            consumer_mock().skill.assert_called_with(
                    name='building', abbr='BUIL', level=1, descr=mock.ANY,
                    # skilldescr is often given only at level 1
                    skilldescr='This skill deals with the construction of ' \
                               'fortifications, roads and other buildings, ' \
                               'except for most trade structures.',
                    cost=10, # Only level 1 skills state their cost
                    builds=[{'name': 'Tower', 'cost': 10,
                             'item': [{'abr': 'STON', 'name': 'stone'}]},
                            {'name': 'Fort', 'cost': 40,
                             'item': [{'abr': 'STON', 'name': 'stone'}]},
                            {'name': 'Castle', 'cost': 160,
                             'item': [{'abr': 'STON', 'name': 'stone'}]},
                            {'name': 'Citadel', 'cost': 640,
                             'item': [{'abr': 'STON', 'name': 'stone'}]}])
            
            # Complex (invented) shipbuilding description
            skill = 'shipbuilding [SHIP] 7: A unit with this skill may BUILD ' \
                    'Airships [AIRS] from 60 floater hides [FLOA] and 60 ' \
                    'wood [WOOD], Longships [LONG] from 10 wood [WOOD] and ' \
                    'Rafts [RAFT] from 15 wood [WOOD] and 15 iron [IRON].'
            consumer_mock.reset_mock()
            parser.parse_skill(skill)
            consumer_mock().skill.assert_called_with(
                    name='shipbuilding', abbr='SHIP', level=7, descr=mock.ANY,
                    production={
                            'command': 'build',
                            'items': [{'abr': 'AIRS', 'names': 'Airships',
                                       'pInput': [{'abr': 'FLOA',
                                                   'names': 'floater hides',
                                                   'amt': 60},
                                                  {'abr': 'WOOD',
                                                   'names': 'wood',
                                                   'amt': 60}],
                                       'pMonths': 60},
                                      {'abr': 'LONG', 'names': 'Longships',
                                       'pInput': [{'abr': 'WOOD',
                                                   'names': 'wood',
                                                   'amt': 10}],
                                       'pMonths': 10},
                                      {'abr': 'RAFT', 'names': 'Rafts',
                                       'pInput': [{'abr': 'WOOD',
                                                   'names': 'wood',
                                                   'amt': 15},
                                                  {'abr': 'IRON',
                                                   'names': 'iron',
                                                   'amt': 15}],
                                       'pMonths': 15}
                                      ]
                                })
            
            # Foundation skill
            skill = 'force [FORC] 1: The Force skill is not directly useful ' \
                    'to a mage, but is rather one of the Foundation skills ' \
                    'on which other magical skills are based. The Force ' \
                    'skill determines the power of the magical energy that a ' \
                    'mage is able to use. Note that a Force skill level of 0 ' \
                    'does not indicate that a mage cannot use magical ' \
                    'energy, but rather can only perform magical acts that ' \
                    'do not require great amounts of power. This skill costs ' \
                    '100 silver per month of study.'
            consumer_mock.reset_mock()
            parser.parse_skill(skill)
            consumer_mock().skill.assert_called_with(
                    name='force', abbr='FORC', level=1, descr=mock.ANY,
                    skilldescr=mock.ANY, cost=100, foundation=True)
            
            # Combat skill
            skill = 'fire [FIRE] 1: A mage with this skill can cast a ' \
                    'fireball in battle. This ability does between 2 and 10 ' \
                    'times the skill level of the mage energy attacks. In ' \
                    'order to use this spell in combat, the mage should use ' \
                    'the COMBAT order to set it as his combat spell. This ' \
                    'skill requires force [FORC] 1 to begin to study. This ' \
                    'skill costs 100 silver per month of study.'
            consumer_mock.reset_mock()
            parser.parse_skill(skill)
            consumer_mock().skill.assert_called_with(
                    name='fire', abbr='FIRE', level=1, descr=mock.ANY,
                    cost=100, specialstr=\
                        'a fireball in battle. This ability does between ' \
                        '2 and 10 times the skill level of the mage energy ' \
                        'attacks.',
                    depends=[{'abbr': 'FORC', 'name': 'force', 'level': 1}],
                    combat=True,
                    special={'damage': [
                        {'type': 'energy', 'expandLevel': True,
                         'minnum': 2, 'maxnum': 10}]})
            
            # Defensive bonus + shield skill
            skill = 'force shield [FSHI] 1:  A mage with this skill can cast ' \
                    'a force shield in battle. This spell provides a shield ' \
                    'against all ranged attacks against the entire army at a ' \
                    'level equal to the skill level of the ability. This ' \
                    'spell provides a defensive bonus of 1 per skill level ' \
                    'versus melee attacks to the user. In order to use this ' \
                    'spell in combat, the mage should use the COMBAT order ' \
                    'to set it as his combat spell. This skill requires ' \
                    'force [FORC] 1 to begin to study. This skill costs 100 ' \
                    'silver per month of study.'
            consumer_mock.reset_mock()
            parser.parse_skill(skill)
            consumer_mock().skill.assert_called_with(
                    name='force shield', abbr='FSHI', level=1, descr=mock.ANY,
                    cost=100, specialstr=mock.ANY,
                    depends=[{'abbr': 'FORC', 'name': 'force', 'level': 1}],
                    combat=True,
                    special={'defs': [
                        {'type': 'melee', 'val': 1, 'expandLevel': True}],
                             'shield': [
                        {'type': 'ranged'}]})
            
            # No buildings
            skill = 'earthquake [EQUA] 1:  A mage with this skill can cast ' \
                    'an earthquake in battle. This ability will only target ' \
                    'units inside structures, with the exception of the ' \
                    'following structures: Magical Tower, Magical Fortress, ' \
                    'Magical Castle, or Magical Citadel. The bonus given to ' \
                    'units inside buildings is not effective against this ' \
                    'ability. This ability does between 2 and 100 times the ' \
                    'skill level of the mage melee attacks. In order to use ' \
                    'this spell in combat, the mage should use the COMBAT ' \
                    'order to set it as his combat spell. This skill ' \
                    'requires force [FORC] 1 and pattern [PATT] 1 to begin ' \
                    'to study. This skill costs 100 silver per month of study.'
            consumer_mock.reset_mock()
            parser.parse_skill(skill)
            consumer_mock().skill.assert_called_with(
                    name='earthquake', abbr='EQUA', level=1, descr=mock.ANY,
                    cost=100, specialstr=mock.ANY,
                    depends=[{'abbr': 'FORC', 'name': 'force', 'level': 1},
                             {'abbr': 'PATT', 'name': 'pattern', 'level': 1}],
                    combat=True,
                    special={'damage': [{'type': 'melee', 'minnum': 2,
                                         'maxnum': 100, 'expandLevel': True}],
                             'nobuilding': True,
                             'buildingexcept': True,
                             'buildings': [{'name': 'Magical Tower'},
                                           {'name': 'Magical Fortress'},
                                           {'name': 'Magical Castle'},
                                           {'name': 'Magical Citadel'}]})
            
            # No monsters
            skill = 'create aura of fear [FEAR] 1:  A mage with this skill ' \
                    'can cast cause fear in battle. This ability will not ' \
                    'target creatures which are currently affected by fear. ' \
                    'This ability cannot target monsters. This ability does ' \
                    'between 2 and 20 times the skill level of the mage ' \
                    'spirit attacks. Each attack causes the target to be ' \
                    'effected by fear (-2 to attack, -2 versus melee ' \
                    'attacks, -2 versus riding attacks) for the rest of the ' \
                    'battle. In order to use this spell in combat, the mage ' \
                    'should use the COMBAT order to set it as his combat ' \
                    'spell. This skill requires necromancy [NECR] 1 to begin ' \
                    'to study. This skill costs 100 silver per month of study.'
            consumer_mock.reset_mock()
            parser.parse_skill(skill)
            consumer_mock().skill.assert_called_with(
                    name='create aura of fear', abbr='FEAR', level=1,
                    descr=mock.ANY, cost=100, specialstr=mock.ANY,
                    depends=[{'abbr': 'NECR', 'name': 'necromancy',
                              'level': 1}],
                    combat=True,
                    special={'damage': [{'type': 'spirit', 'minnum': 2,
                                        'maxnum': 20, 'expandLevel': True,
                                        'effectstr': mock.ANY,
                                        'effect': {'name': 'fear',
                                                   'oneshot': False,
                                                   'attackVal': -2,
                                                   'defMods':[
                                                       {'type': 'melee',
                                                        'val': -2},
                                                       {'type': 'riding',
                                                        'val': -2}]
                            }}],
                             'nomonster': True, 'effectexcept': True,
                             'effects': [{'name': 'fear'}],
                             })
            
            # A last special skill
            skill = 'banish undead [BUND] 1:  A mage with this skill can ' \
                    'cast banish undead in battle. This ability will only ' \
                    'target skeletons [SKEL], undead [UNDE], or liches ' \
                    '[LICH]. This ability does between 2 and 50 times the ' \
                    'skill level of the mage non-resistable attacks. In ' \
                    'order to use this spell in combat, the mage should use ' \
                    'the COMBAT order to set it as his combat spell. This ' \
                    'skill requires necromancy [NECR] 1 to begin to study. ' \
                    'This skill costs 100 silver per month of study.'
            consumer_mock.reset_mock()
            parser.parse_skill(skill)
            consumer_mock().skill.assert_called_with(
                    name='banish undead', abbr='BUND', level=1,
                    descr=mock.ANY, cost=100, specialstr=mock.ANY,
                    depends=[{'abbr': 'NECR', 'name': 'necromancy',
                              'level': 1}],
                    combat=True,
                    special={'damage': [{'type': 'non-resistable', 'minnum': 2,
                                         'maxnum': 50, 'expandLevel': True}],
                             'soldierif': True,
                             'targets': [{'abr': 'SKEL', 'names': 'skeletons'},
                                         {'abr': 'UNDE', 'names': 'undead'},
                                         {'abr': 'LICH', 'names': 'liches'}]})
            
            # Cast skill
            skill = 'gate lore [GATE] 1: Gate Lore is the art of detecting ' \
                    'and using magical Gates, which are spread through the ' \
                    'world. The Gates are spread out randomly, so there is ' \
                    'no correlation between the Gate number and the Gate\'s ' \
                    'location. A mage with skill 1 in Gate Lore can see a ' \
                    'Gate if one exists in the same region as the mage. This ' \
                    'detection is automatic; the Gate will appear in the ' \
                    'region report. A mage with skill 1 in Gate Lore may ' \
                    'also jump through a Gate into another region on the ' \
                    'same level containing a gate, selected at random. To ' \
                    'use Gate Lore in this manner, use the syntax CAST ' \
                    'Gate_Lore RANDOM UNITS <unit> ... UNITS is followed by ' \
                    'a list of units to follow the mage through the Gate ' \
                    '(the mage always jumps through the Gate). At level 1, ' \
                    'the mage may carry 15 weight units through the Gate ' \
                    '(including the weight of the mage). This skill requires ' \
                    'pattern [PATT] 1 and spirit [SPIR] 1 to begin to study. ' \
                    'This skill costs 100 silver per month of study.'
            consumer_mock.reset_mock()
            parser.parse_skill(skill)
            consumer_mock().skill.assert_called_with(
                    name='gate lore', abbr='GATE', level=1, descr=mock.ANY,
                    cost=100, skilldescr=mock.ANY,
                    depends=[{'abbr': 'PATT', 'name': 'pattern', 'level': 1},
                             {'abbr': 'SPIR', 'name': 'spirit', 'level': 1}],
                    cast=True)
            
            # Magic production. Amount less than 100
            skill = 'summon wind [SWIN] 5: A mage with this skill has a 20 ' \
                    'percent times their level chance to create a Cloudship ' \
                    '[CLOU] via magic at a cost of 75 floater hides [FLOA] ' \
                    'and 75 ironwood [IRWD]. To use this spell, the mage ' \
                    'should CAST Summon_Wind.'
            consumer_mock.reset_mock()
            parser.parse_skill(skill)
            consumer_mock().skill.assert_called_with(
                    name='summon wind', abbr='SWIN', level=5, descr=mock.ANY,
                    mProduction={
                        'command': 'cast',
                        'items': [{'abr': 'CLOU', 'name': 'Cloudship',
                                   'mOut': 20,
                                   'mInput': [{'amt': 75, 'abr': 'FLOA',
                                               'names': 'floater hides'},
                                              {'abr': 'IRWD', 'amt': 75,
                                               'names': 'ironwood'}
                                              ]
                                   }]
                                 },
                    cast=True)
            
            # Magic production. Amount more than 100
            skill = 'wolf lore [WOLF] 1: A mage with Wolf Lore skill may ' \
                    'summon wolves, who will fight for him in combat. A mage ' \
                    'may summon a number of wolves averaging 200 percent ' \
                    'times his skill level, and control a total number of ' \
                    'his skill level squared times 4 wolves; the wolves will ' \
                    'be placed in the mages inventory. Note, however, that ' \
                    'wolves may only be summoned in mountain and forest ' \
                    'regions. To summon wolves, the mage should issue the ' \
                    'order CAST Wolf_Lore. A mage with this skill may create ' \
                    '2 times their level in wolves [WOLF] via magic. To use ' \
                    'this spell, the mage should CAST Wolf_Lore. This skill ' \
                    'requires earth lore [EART] 1 to begin to study. This ' \
                    'skill costs 100 silver per month of study.'
            consumer_mock.reset_mock()
            parser.parse_skill(skill)
            consumer_mock().skill.assert_called_with(
                    name='wolf lore', abbr='WOLF', level=1, descr=mock.ANY,
                    cost=100,skilldescr=mock.ANY,
                    mProduction={
                            'command': 'cast',
                            'items': [{'abr': 'WOLF', 'names': 'wolves',
                                       'mOut': 200}]},
                    depends=[{'abbr': 'EART', 'name': 'earth lore',
                              'level': 1}],
                    cast=True)
            
            # Magic production. Amount is 100
            skill = 'bird lore [BIRD] 3: A mage with Bird Lore 3 can summon ' \
                    'eagles to join him, who will aid him in combat, and ' \
                    'provide for flying transportation. A mage may summon an ' \
                    'average of 200 percent times his skill level minus 2 ' \
                    'eagles per month, and may control a number equal to his ' \
                    'skill level minus 2, squared, times two. To summon an ' \
                    'eagle, issue the order CAST Bird_Lore EAGLE; the eagles ' \
                    'will appear in his inventory. A mage with this skill ' \
                    'may create their level in eagles [EAGL] via magic. To ' \
                    'use this spell, the mage should CAST Bird_Lore.'
            consumer_mock.reset_mock()
            parser.parse_skill(skill)
            consumer_mock().skill.assert_called_with(
                    name='bird lore', abbr='BIRD', level=3, descr=mock.ANY,
                    skilldescr=mock.ANY,
                    mProduction={
                            'command': 'cast',
                            'items': [{'abr': 'EAGL', 'names': 'eagles',
                                       'mOut': 100}]},
                    cast=True)
            
            # Apprentice
            skill = 'manipulation [MANI] 1: A unit with this skill becomes ' \
                    'an acolyte. While acolytes cannot cast spells directly, ' \
                    'they can use magic items normally only usable by mages. ' \
                    'This skill costs 100 silver per month of study.'
            consumer_mock.reset_mock()
            parser.parse_skill(skill)
            consumer_mock().skill.assert_called_with(
                    name='manipulation', abbr='MANI', level=1, descr=mock.ANY,
                    skilldescr=mock.ANY, cost=100, apprentice=True)
    
    def test_parse_item(self):
        '''Tests parse_item method'''
        with patch(__name__ + '.reportparser.ReportConsumer') as consumer_mock:
            parser = ReportParser(consumer_mock())
            
            # Max inventory
            item = 'balrog [BALR], weight 250, walking capacity 50, riding ' \
                   'capacity 50, flying capacity 50, moves 6 hexes per ' \
                   'month. This is a monster. This monster attacks with a ' \
                   'combat skill of 6. This monster has a resistance of 6 to ' \
                   'melee attacks. This monster has a resistance of 6 to ' \
                   'energy attacks. This monster has a resistance of 6 to ' \
                   'spirit attacks. This monster has a resistance of 6 to ' \
                   'weather attacks. This monster has a resistance of 5 to ' \
                   'riding attacks. This monster has a resistance of 0 to ' \
                   'ranged attacks. Monster can cast cause fear in battle at ' \
                   'a skill level of 6. This ability will not target ' \
                   'creatures which are currently affected by fear. This ' \
                   'ability cannot target monsters. This ability does ' \
                   'between 2 and 120 spirit attacks. Each attack causes the ' \
                   'target to be effected by fear (-2 to attack, -2 versus ' \
                   'melee attacks, -2 versus riding attacks) for the rest of ' \
                   'the battle. This monster has 200 melee attacks per round ' \
                   'and takes 200 hits to kill. This monster has a tactics ' \
                   'score of 5, a stealth score of 1, and an observation ' \
                   'score of 2. This monster might have magic items and ' \
                   'silver as treasure. A unit may have at most 1 balrog ' \
                   '[BALR].'
            parser.parse_item(item)
            consumer_mock().item.assert_called_with(
                    name='balrog', abr='BALR', weight=250, walking=50,
                    riding=50, flying=50, speed=6,
                    max_inventory=1,
                    descr=mock.ANY,
                    monster={'attackLevel': 6,
                             'defense': {'melee': 6, 'energy': 6, 'spirit': 6,
                                         'weather': 6, 'riding': 5, 'ranged': 0},
                             'atts': 200, 'hits': 200, 'tactics': 5,
                             'stealth': 1, 'obs': 2, 'spoils': 'magic',
                             'specialstr': mock.ANY, 
                             'special': {'name': 'cause fear',
                                         'level': 6,
                                         'nomonster': True,
                                         'damage': \
                                             [{'type': 'spirit',
                                               'minnum': 2, 'maxnum': 120,
                                               'effectstr': mock.ANY,
                                               'effect': \
                                                   {'name': 'fear',
                                                    'oneshot': False,
                                                    'attackVal': -2,
                                                    'defMods': \
                                                        [{'type': 'melee',
                                                          'val': -2},
                                                         {'type': 'riding',
                                                          'val': -2}]}
                                         }],
                                         'effectexcept': True,
                                         'effects': [{'name': 'fear'}]}
                             })
            
            # Can't give
            item = 'wolf [WOLF], weight 10, walking capacity 5, riding ' \
                   'capacity 5, moves 4 hexes per month. This is a monster. ' \
                   'This monster attacks with a combat skill of 2. This ' \
                   'monster has a resistance of 2 to melee attacks. This ' \
                   'monster has a resistance of 2 to energy attacks. This ' \
                   'monster has a resistance of 0 to spirit attacks. This ' \
                   'monster has a resistance of 2 to weather attacks. This ' \
                   'monster has a resistance of 3 to riding attacks. This ' \
                   'monster has a resistance of 0 to ranged attacks. This ' \
                   'monster has 1 melee attack per round and takes 1 hit to ' \
                   'kill. This monster has a tactics score of 1, a stealth ' \
                   'score of 2, and an observation score of 3. This monster ' \
                   'might have silver as treasure. This item cannot be given ' \
                   'to other units.'
            consumer_mock.reset_mock()
            parser.parse_item(item)
            consumer_mock().item.assert_called_with(
                    name='wolf', abr='WOLF', weight=10, walking=5, riding=5,
                    speed=4, cantgive=True,
                    monster={'attackLevel': 2,
                             'defense': {'weather': 2, 'melee': 2, 'spirit': 0,
                                         'energy': 2, 'riding': 3, 'ranged': 0},
                             'atts': 1, 'hits': 1, 'tactics': 1, 'stealth': 2,
                             'obs': 3},
                    descr=mock.ANY)
            
            # Food & Trade resource
            item = 'livestock [LIVE], weight 50, can walk, moves 2 hexes per ' \
                   'month, costs 37 silver to withdraw. This item is a trade ' \
                   'resource. This item can be eaten to provide 10 silver ' \
                   'towards a unit\'s maintenance cost.'
            consumer_mock.reset_mock()
            parser.parse_item(item)
            consumer_mock().item.assert_called_with(
                    name='livestock', abr='LIVE', weight=50, walking=0, speed=2,
                    food=10, resource=True, withdraw=37,
                    descr=mock.ANY)
            
            # Battle item
            item = 'amulet of invulnerability [XXXX], weight 0. This item is ' \
                   'a miscellaneous combat item. This item provides ' \
                   'invulnerability in battle at a skill level of 5. This ' \
                   'ability provides the wielder with a defence bonus of 5 ' \
                   'against all all attacks.'
            consumer_mock.reset_mock()
            parser.parse_item(item)
            consumer_mock().item.assert_called_with(
                    name='amulet of invulnerability', abr='XXXX', weight=0,
                    descr=mock.ANY,
                    battle={'specialstr':
                                    'invulnerability in battle at a skill ' \
                                    'level of 5. This ability provides ' \
                                    'the wielder with a defence bonus of ' \
                                    '5 against all all attacks.',
                            'shield': True,
                            'special': {
                                    'name': 'invulnerability',
                                    'level': 5,
                                    'shield': [{'type': 'all'}]}})
            
            item = 'wooden shield [WSHD], weight 1, costs 100 silver to ' \
                   'withdraw. This item is a miscellaneous combat item. This ' \
                   'item provides a physical shield in battle at a skill ' \
                   'level of 2. This ability provides the wielder with a ' \
                   'defence bonus of 2 against all ranged attacks.'
            consumer_mock.reset_mock()
            parser.parse_item(item)
            consumer_mock().item.assert_called_with(
                    name='wooden shield', abr='WSHD', weight=1, withdraw=100,
                    descr=mock.ANY,
                    battle={'specialstr':
                                    'a physical shield in battle at a skill ' \
                                    'level of 2. This ability provides the ' \
                                    'wielder with a defence bonus of 2 ' \
                                    'against all ranged attacks.',
                            'shield': True,
                            'special': {
                                    'name': 'a physical shield',
                                    'level': 2, 'shield': True,
                                    'shield': [{'type': 'ranged'}]}})
            
            # Battle item. Damage and effect
            item = 'runesword [RUNE], weight 1. This is a slashing weapon. ' \
                   'No skill is needed to wield this weapon. This weapon ' \
                   'grants a bonus of 4 on attack and defense. Wielders of ' \
                   'this weapon, if mounted, get their riding skill bonus on ' \
                   'combat attack and defense. There is a 50% chance that ' \
                   'the wielder of this weapon gets a chance to attack in ' \
                   'any given round. This weapon attacks versus the ' \
                   'target\'s defense against melee attacks. This weapon ' \
                   'allows a number of attacks equal to half the skill level ' \
                   '(rounded up) of the attacker per round. This item is a ' \
                   'miscellaneous combat item. This item can cast cause fear ' \
                   'in battle at a skill level of 3. This ability will not ' \
                   'target creatures which are currently affected by fear. ' \
                   'This ability cannot target monsters. This ability does ' \
                   'between 2 and 60 spirit attacks. Each attack causes the ' \
                   'target to be effected by fear (-2 to attack, -2 versus ' \
                   'melee attacks, -2 versus riding attacks) for the rest of ' \
                   'the battle.'
            consumer_mock.reset_mock()
            parser.parse_item(item)
            consumer_mock().item.assert_called_with(
                    name='runesword', abr='RUNE', weight=1,
                    descr=mock.ANY,
                    weapon={'class': 'slashing', 'attackType': 'melee',
                            'defenseBonus': 4, 'attackBonus': 4,
                            'ridingbonus': True,
                            'numAttacks': {'atts': 0,
                                           'attacksHalfSkill': True}},
                    battle={
                        'specialstr':
                            'cause fear in battle at a skill level of 3. ' \
                            'This ability will not target creatures which ' \
                            'are currently affected by fear. This ability ' \
                            'cannot target monsters. This ability does ' \
                            'between 2 and 60 spirit attacks. Each attack ' \
                            'causes the target to be effected by fear (-2 to ' \
                            'attack, -2 versus melee attacks, -2 versus ' \
                            'riding attacks) for the rest of the battle.',
                        'special': {
                            'name': 'cause fear', 'level': 3,
                            'damage': [
                                {'type': 'spirit', 'minnum': 2, 'maxnum': 60,
                                 'effectstr': \
                                     'fear (-2 to attack, -2 versus melee ' \
                                     'attacks, -2 versus riding attacks) for ' \
                                     'the rest of the battle.',
                                 'effect': {
                                     'name': 'fear', 'attackVal': -2,
                                     'oneshot': False,
                                     'defMods': [
                                         {'type': 'melee', 'val': -2},
                                         {'type': 'riding', 'val': -2}
                                      ]
                                 }
                                }],
                        'nomonster': True, 'effectexcept': True,
                        'effects': [{'name': 'fear'}]}})
            
            # Battle item. Defensive bonus
            item = 'censer of protection [CNSR], weight 0. This item is a ' \
                   'miscellaneous combat item. This item may only be used by ' \
                   'a mage or an acolyte. This item can cast a force shield ' \
                   'in battle at a skill level of 3. This spell provides a ' \
                   'shield against all ranged attacks against the entire ' \
                   'army at a level equal to the skill level of the ability. ' \
                   'This spell provides a defensive bonus of 3 versus melee ' \
                   'attacks to the user.'
            consumer_mock.reset_mock()
            parser.parse_item(item)
            consumer_mock().item.assert_called_with(
                    name='censer of protection', abr='CNSR', weight=0,
                    descr=mock.ANY,
                    battle={
                        'specialstr':
                            'a force shield in battle at a skill level of 3. ' \
                            'This spell provides a shield against all ranged ' \
                            'attacks against the entire army at a level ' \
                            'equal to the skill level of the ability. This ' \
                            'spell provides a defensive bonus of 3 versus ' \
                            'melee attacks to the user.',
                        'mageonly': True, 
                        'special': {
                            'name': 'a force shield', 'level': 3,
                            'defs': [{'type': 'melee', 'val': 3}],
                            'shield': [{'type': 'ranged'}]
                        }})
            
            # Grant skill item
            item = 'gate crystal [GTCR], weight 0. This item allows its ' \
                   'possessor to CAST the gate lore spell as if their skill ' \
                   'in gate lore was the highest of their manipulation, ' \
                   'pattern, force and spirit skills, up to a maximum of ' \
                   'level 3. This item may only be used by a mage or an ' \
                   'acolyte.'
            consumer_mock.reset_mock()
            parser.parse_item(item)
            consumer_mock().item.assert_called_with(
                    name='gate crystal', abr='GTCR', weight=0,
                    descr=mock.ANY, mageonly=True,
                    grantSkill={'name': 'gate lore',
                                'maxGrant': 3,
                                'fromSkills': [{'name': 'manipulation'},
                                               {'name': 'pattern'},
                                               {'name': 'force'},
                                               {'name': 'spirit'}]})
            
            # Attribute wind
            item = 'windchime [WCHM], weight 0. The possessor of this item ' \
                   'will add 2 movement points to ships requiring up to 24 ' \
                   'sailing skill points. This bonus is not cumulative with ' \
                   'a mage\'s summon wind skill. This item may only be used ' \
                   'by a mage or an acolyte.'
            consumer_mock.reset_mock()
            parser.parse_item(item)
            consumer_mock().item.assert_called_with(
                    name='windchime', abr='WCHM', weight=0,
                    descr=mock.ANY, mageonly=True,
                    wind={'windBoost': 2, 'val': 24})
            
            # Attribute stealth
            item = 'ring of invisibility [RING], weight 0. This item grants ' \
                   'a 3 point bonus to a unit\'s stealth skill (note that a ' \
                   'unit must possess one RING for each man to gain this ' \
                   'bonus). A Ring of Invisibility has one limitation; a ' \
                   'unit possessing a RING cannot assassinate, nor steal ' \
                   'from, a unit with an Amulet of True Seeing.'
            consumer_mock.reset_mock()
            parser.parse_item(item)
            consumer_mock().item.assert_called_with(
                    name='ring of invisibility', abr='RING', weight=0,
                    descr=mock.ANY,
                    stealth={'perman': True, 'val': 3})
            
            # Attribute observation
            item = 'amulet of true seeing [AMTS], weight 0. This item grants ' \
                   'a 2 point bonus to a unit\'s observation skill. Also, a ' \
                   'unit with an Amulet of True Seeing cannot be ' \
                   'assassinated by, nor have items stolen by, a unit with ' \
                   'a Ring of Invisibility (note that the unit must have at ' \
                   'least one Amulet of True Seeing per man in order to ' \
                   'repel a unit with a Ring of Invisibility).'
            consumer_mock.reset_mock()
            parser.parse_item(item)
            consumer_mock().item.assert_called_with(
                    name='amulet of true seeing', abr='AMTS', weight=0,
                    descr=mock.ANY,
                    observation={'val': 2})
            
            # Money
            item = 'silver [SILV], weight 0. This is the currency of Havilah.'
            consumer_mock.reset_mock()
            parser.parse_item(item)
            consumer_mock().item.assert_called_with(
                    name='silver', abr='SILV', weight=0,
                    descr=mock.ANY, money=True)
            
            # Mount
            item = 'winged horse [WING], weight 50, walking capacity 20, ' \
                   'riding capacity 20, flying capacity 20, moves 6 hexes ' \
                   'per month. This is a mount. This mount requires riding ' \
                   '[RIDI] of at least level 3 to ride in combat. This mount ' \
                   'gives a minimum bonus of +3 when ridden into combat. ' \
                   'This mount gives a maximum bonus of +5 when ridden into ' \
                   'combat. This mount gives a maximum bonus of +3 when ' \
                   'ridden into combat in terrain which allows ridden mounts ' \
                   'but not flying mounts.'
            consumer_mock.reset_mock()
            parser.parse_item(item)
            consumer_mock().item.assert_called_with(
                    name='winged horse', abr='WING', weight=50, walking=20,
                    riding=20, flying=20, speed=6,
                    descr=mock.ANY,
                    mount={'minBonus': 3, 'maxBonus': 5, 'maxHamperedBonus': 3,
                           'skill': {'name': 'riding', 'abbr': 'RIDI'}})
            
            # Trade good
            item = 'ivory [IVOR], weight 1. This is a trade good. This item ' \
                   'can be bought for between 60 and 114 silver. This item ' \
                   'can be sold for between 150 and 210 silver.'
            consumer_mock.reset_mock()
            parser.parse_item(item)
            consumer_mock().item.assert_called_with(
                    name='ivory', abr='IVOR', weight=1,
                    descr=mock.ANY,
                    trade={'minbuy': 60, 'maxbuy': 114,
                           'minsell': 150, 'maxsell': 210})
            
            # Tool
            item = 'pick [PICK], weight 1, costs 150 silver to withdraw. ' \
                   'This is a piercing weapon. No skill is needed to wield ' \
                   'this weapon. This weapon grants a bonus of 1 on attack ' \
                   'and defense. Wielders of this weapon, if mounted, get ' \
                   'their riding skill bonus on combat attack and defense. ' \
                   'There is a 50% chance that the wielder of this weapon ' \
                   'gets a chance to attack in any given round. This weapon ' \
                   'attacks versus the target\'s defense against melee ' \
                   'attacks. This weapon allows 1 attack per round. This is ' \
                   'a tool. This item increases the production of iron ' \
                   '[IRON] by 1, stone [STON] by 1, mithril [MITH] by 1, ' \
                   'and rootstone [ROOT] by 1.'
            consumer_mock.reset_mock()
            parser.parse_item(item)
            consumer_mock().item.assert_called_with(
                    name='pick', abr='PICK', weight=1, withdraw=150,
                    descr=mock.ANY,
                    weapon={'class': 'piercing', 'attackType': 'melee',
                            'attackBonus': 1, 'defenseBonus': 1,
                            'ridingbonus': True,
                            'numAttacks': {'atts': 1}},
                    tool={'items':
                            [{'abr': 'IRON', 'name': 'iron', 'val': 1},
                             {'abr': 'STON', 'name': 'stone', 'val': 1},
                             {'abr': 'MITH', 'name': 'mithril', 'val': 1},
                             {'abr': 'ROOT', 'name': 'rootstone', 'val': 1}]})
            
            # Armor
            item = 'chain armor [CARM], weight 1, costs 150 silver to ' \
                   'withdraw. This is a type of armor. This armor will ' \
                   'protect its wearer 33% of the time versus slashing ' \
                   'attacks, 33% of the time versus piercing attacks, 33% ' \
                   'of the time versus crushing attacks, 33% of the time ' \
                   'versus cleaving attacks, 0% of the time versus ' \
                   'armor-piercing attacks, 0% of the time versus energy ' \
                   'attacks, 0% of the time versus spirit attacks, and 0% of ' \
                   'the time versus weather attacks.'
            consumer_mock.reset_mock()
            parser.parse_item(item)
            consumer_mock().item.assert_called_with(
                    name='chain armor', abr='CARM', weight=1, withdraw=150,
                    descr=mock.ANY,
                    armor={'saves': [{'weapClass': 'slashing', 'percent': 33},
                                     {'weapClass': 'piercing', 'percent': 33},
                                     {'weapClass': 'crushing', 'percent': 33},
                                     {'weapClass': 'cleaving', 'percent': 33},
                                     {'weapClass': 'armor-piercing',
                                      'percent': 0},
                                     {'weapClass': 'energy', 'percent': 0},
                                     {'weapClass': 'spirit', 'percent': 0},
                                     {'weapClass': 'weather', 'percent': 0}]})
            
            item = 'leather armor [LARM], weight 1, costs 112 silver to ' \
                   'withdraw. This is a type of armor. This armor will ' \
                   'protect its wearer 25% of the time versus slashing ' \
                   'attacks, 25% of the time versus piercing attacks, 25% ' \
                   'of the time versus crushing attacks, 25% of the time ' \
                   'versus cleaving attacks, 0% of the time versus ' \
                   'armor-piercing attacks, 0% of the time versus energy ' \
                   'attacks, 0% of the time versus spirit attacks, and 0% of ' \
                   'the time versus weather attacks. This armor may be worn ' \
                   'during assassination attempts.'
            consumer_mock.reset_mock()
            parser.parse_item(item)
            consumer_mock().item.assert_called_with(
                    name='leather armor', abr='LARM', weight=1, withdraw=112,
                    descr=mock.ANY,
                    armor={'useinassassinate': True,
                           'saves': [{'weapClass': 'slashing', 'percent': 25},
                                     {'weapClass': 'piercing', 'percent': 25},
                                     {'weapClass': 'crushing', 'percent': 25},
                                     {'weapClass': 'cleaving', 'percent': 25},
                                     {'weapClass': 'armor-piercing',
                                      'percent': 0},
                                     {'weapClass': 'energy', 'percent': 0},
                                     {'weapClass': 'spirit', 'percent': 0},
                                     {'weapClass': 'weather', 'percent': 0}]})
            
            # Weapon
            item = 'crossbow [XBOW], weight 1, costs 150 silver to withdraw. ' \
                   'This is a ranged armor-piercing weapon. Knowledge of ' \
                   'crossbow [XBOW] is needed to wield this weapon. ' \
                   'Attackers do not get skill bonus on defense. There is a ' \
                   '50% chance that the wielder of this weapon gets a chance ' \
                   'to attack in any given round. This weapon attacks versus ' \
                   'the target\'s defense against ranged attacks. This ' \
                   'weapon allows 1 attack every 2 rounds.'
            consumer_mock.reset_mock()
            parser.parse_item(item)
            consumer_mock().item.assert_called_with(
                    name='crossbow', abr='XBOW', weight=1, withdraw=150,
                    descr=mock.ANY,
                    weapon={'class': 'armor-piercing', 'range': 'ranged',
                            'attackType': 'ranged',
                            'attackBonus': 0, 'defenseBonus': 0,
                            'noattackerskill': True,
                            'numAttacks': {'atts': -2},
                            'skill': {'abbr': 'XBOW', 'name': 'crossbow'}})
            
            item = 'sword [SWOR], weight 1, costs 150 silver to withdraw. ' \
                   'This is a slashing weapon. No skill is needed to wield ' \
                   'this weapon. This weapon grants a bonus of 2 on attack ' \
                   'and defense. This weapon also grants a bonus of 1 '\
                   'against mounted opponents. Wielders of this weapon, if ' \
                   'mounted, get their riding skill bonus on combat ' \
                   'defense. There is a 50% chance that the wielder of ' \
                   'this weapon gets a chance to attack in any given round. ' \
                   'This weapon attacks versus the target\'s defense against ' \
                   'melee attacks. This weapon allows 1 attack per round.'
            consumer_mock.reset_mock()
            parser.parse_item(item)
            consumer_mock().item.assert_called_with(
                    name='sword', abr='SWOR', weight=1, withdraw=150,
                    descr=mock.ANY,
                    weapon={'class': 'slashing', 'mountBonus': 1,
                            'attackType': 'melee',
                            'attackBonus': 2, 'defenseBonus': 2,
                            'ridingbonusdefense': True,
                            'numAttacks': {'atts': 1}})
            
            # Men
            item = 'leader [LEAD], weight 10, walking capacity 5, moves 2 ' \
                   'hexes per month. This race may study all skills to level 5'
            consumer_mock.reset_mock()
            parser.parse_item(item)
            consumer_mock().item.assert_called_with(
                    name='leader', abr='LEAD', weight=10, walking=5, speed=2,
                    descr=mock.ANY,
                    man={'defaultLevel': 5})
            
            item = 'viking [VIKI], weight 10, walking capacity 5, moves 2 ' \
                   'hexes per month. This race may study shipbuilding ' \
                   '[SHIP], sailing [SAIL], lumberjack [LUMB] and combat ' \
                   '[COMB] to level 3 and all other skills to level 2'
            consumer_mock.reset_mock()
            parser.parse_item(item)
            consumer_mock().item.assert_called_with(
                    name='viking', abr='VIKI', weight=10, walking=5, speed=2,
                    descr=mock.ANY,
                    man={'defaultLevel': 2, 'specialLevel': 3,
                         'skills': [{'abbr': 'SHIP', 'name': 'shipbuilding'},
                                    {'abbr': 'SAIL', 'name': 'sailing'},
                                    {'abbr': 'LUMB', 'name': 'lumberjack'},
                                    {'abbr': 'COMB', 'name': 'combat'}]})
            
            item = 'high elf [HELF], weight 10, walking capacity 5, moves 2 ' \
                   'hexes per month. This race may study all magical skills, ' \
                   'farming [FARM], entertainment [ENTE] and longbow [LBOW] ' \
                   'to level 3 and all other skills to level 2'
            consumer_mock.reset_mock()
            parser.parse_item(item)
            consumer_mock().item.assert_called_with(
                    name='high elf', abr='HELF', weight=10, walking=5, speed=2,
                    descr=mock.ANY,
                    man={'defaultLevel': 2, 'specialLevel': 3,
                         'skills': [{'abbr': 'MANI', 'name': 'manipulation'},
                                    {'abbr': 'FARM', 'name': 'farming'},
                                    {'abbr': 'ENTE', 'name': 'entertainment'},
                                    {'abbr': 'LBOW', 'name': 'longbow'}]})
            
            # Ships
            item = 'Raft [RAFT]. This is a ship with a capacity of 300 and a ' \
                   'speed of 2 hexes per month. This ship requires a total ' \
                   'of 2 levels of sailing skill to sail.'
            consumer_mock.reset_mock()
            parser.parse_item(item)
            consumer_mock().item.assert_called_with(
                    name='Raft', abr='RAFT', swimming=300, speed=2,
                    ship={'sailors': 2})
            
            item = 'Galleon [GALL]. This is a ship with a capacity of 1800 ' \
                   'and a speed of 4 hexes per month. This ship requires a ' \
                   'total of 15 levels of sailing skill to sail. This ship ' \
                   'will allow up to 2 mages to study above level 2.'
            consumer_mock.reset_mock()
            parser.parse_item(item)
            consumer_mock().item.assert_called_with(
                    name='Galleon', abr='GALL', swimming=1800, speed=4,
                    ship={'sailors': 15, 'maxMages': 2})
                   
            item = 'Galley [GLLY]. This is a ship with a capacity of 800 and ' \
                   'a speed of 4 hexes per month. This ship requires a total ' \
                   'of 12 levels of sailing skill to sail. This ship ' \
                   'provides defense to the first 75 men inside it, giving a ' \
                   'defensive bonus of 2 against melee attacks, 2 against ' \
                   'energy attacks, 2 against spirit attacks, 2 against ' \
                   'weather attacks, 2 against riding attacks and 2 against ' \
                   'ranged attacks. This ship will allow one mage to study ' \
                   'above level 2.'
            consumer_mock.reset_mock()
            parser.parse_item(item)
            consumer_mock().item.assert_called_with(
                    name='Galley', abr='GLLY', swimming=800, speed=4,
                    ship={'sailors': 12, 'protect': 75, 'maxMages': 1,
                          'defense': {'melee': 2, 'energy': 2, 'spirit': 2,
                                      'weather': 2, 'riding': 2, 'ranged': 2}})
  
            item = 'Airship [AIRS]. This is a flying \'ship\' with a ' \
                   'capacity of 800 and a speed of 6 hexes per month. This ' \
                   'ship requires a total of 10 levels of sailing skill to ' \
                   'sail. This ship will allow one mage to study above level 2.'
            consumer_mock.reset_mock()
            parser.parse_item(item)
            consumer_mock().item.assert_called_with(
                    name='Airship', abr='AIRS', flying=800, speed=6,
                    ship={'sailors': 10, 'maxMages': 1})
       
    def test_parse_structure(self):
        """Test parse structure method"""
        with patch(__name__ + '.reportparser.ReportConsumer') as consumer_mock:
            parser = ReportParser(consumer_mock())
            
            # Group of ships
            ob = 'Fleet: This is a group of ships. Units may enter this ' \
                 'structure.'
            parser.parse_structure(ob)
            consumer_mock().structure.assert_called_with(
                    name='Fleet', structuretype='group of ships',
                    canenter=True)
                 
            # Lair
            ob = 'Ruin: This is a building. Monsters can potentially lair in ' \
                 'this structure. This structure cannot be built by players.'
            consumer_mock.reset_mock()
            parser.parse_structure(ob)
            consumer_mock().structure.assert_called_with(
                    name='Ruin', structuretype='building', monster=True,
                    nobuildable=True)
            
            # Unbuildable
            ob = 'Shaft: This is a building. Units may enter this structure. ' \
                 'This structure cannot be built by players.'
            consumer_mock.reset_mock()
            parser.parse_structure(ob)
            consumer_mock().structure.assert_called_with(
                    name='Shaft', structuretype='building', canenter=True,
                    nobuildable=True)
            
            # Building
            ob = 'Fort: This is a building. Units may enter this structure. ' \
                 'This structure provides defense to the first 50 men inside ' \
                 'it. This structure gives a defensive bonus of 2 against ' \
                 'melee attacks, 2 against energy attacks, 2 against spirit ' \
                 'attacks, 2 against weather attacks, 2 against riding ' \
                 'attacks and 2 against ranged attacks. This structure will ' \
                 'allow one mage to study above level 2.'
            consumer_mock.reset_mock()
            parser.parse_structure(ob)
            consumer_mock().structure.assert_called_with(
                    name='Fort', structuretype='building', canenter=True,
                    protect=50, maxMages=1,
                    defense={'melee': 2, 'energy': 2, 'spirit': 2,
                             'weather': 2, 'riding': 2, 'ranged': 2})
            
            # Not affected
            ob = 'Magical Fortress: This is a building. Units may enter this ' \
                 'structure. This structure provides defense to the first 50 ' \
                 'men inside it. This structure gives a defensive bonus of 2 ' \
                 'against melee attacks, 2 against energy attacks, 2 against ' \
                 'spirit attacks, 2 against weather attacks, 2 against ' \
                 'riding attacks and 2 against ranged attacks. Units in this ' \
                 'structure are not affected by an earthquake. This ' \
                 'structure will allow up to 20 mages to study above level 2.'
            consumer_mock.reset_mock()
            parser.parse_structure(ob)
            consumer_mock().structure.assert_called_with(
                    name='Magical Fortress', structuretype='building',
                    canenter=True, protect=50, maxMages=20,
                    defense={'melee': 2, 'energy': 2, 'spirit': 2,
                             'weather': 2, 'riding': 2, 'ranged': 2},
                    specials=[{'specialname': 'an earthquake',
                               'affected': False}])
                 
            # Production
            ob = 'Mine: This is a building. Units may enter this structure. ' \
                 'This trade structure increases the amount of iron ' \
                 'available in the region.'
            consumer_mock.reset_mock()
            parser.parse_structure(ob)
            consumer_mock().structure.assert_called_with(
                    name='Mine', structuretype='building', canenter=True,
                    productionAided='iron')
        
    
    def test_parse_region(self):
        """Tests parse_region method"""
        with patch(__name__ + '.reportparser.ReportConsumer') as consumer_mock:
            parser = ReportParser(consumer_mock())
            
            # Region line, ocean
            region = 'ocean (28,0) in Havilah Ocean.'
            parser.parse_region(region)
            consumer_mock().region.assert_called_with(
                    xloc=28, yloc=0, terrain='ocean', name='Havilah Ocean')
            
            # Ocean in the underworld
            region = 'ocean (6,30,underworld) in The Undersea.'
            consumer_mock.reset_mock()
            parser.parse_region(region)
            consumer_mock().region.assert_called_with(
                    xloc=6, yloc=30, zloc='underworld', terrain='ocean',
                    name='The Undersea')
            
            # Land
            region = 'mountain (23,3) in Dinvore, 1167 peasants ' \
                     '(sea elves), $560.'
            consumer_mock.reset_mock()
            parser.parse_region(region)
            consumer_mock().region.assert_called_with(
                    xloc=23, yloc=3, terrain='mountain', name='Dinvore',
                    population=1167, racenames='sea elves', wealth=560)
            
            # Town
            region = 'plain (36,4) in Banthesban, contains Ca\'a [village], ' \
                     '6812 peasants (vikings), $5722.'
            consumer_mock.reset_mock()
            parser.parse_region(region)
            consumer_mock().region.assert_called_with(
                    xloc=36, yloc=4, terrain='plain', name='Banthesban',
                    population=6812, racenames='vikings', wealth=5722,
                    town={'name': 'Ca\'a', 'type': 'village'})
            
            # Weather
            weather = '  It was monsoon season last month; it will be clear ' \
                      'next month.'
            consumer_mock.reset_mock()
            parser.parse_region(weather)
            consumer_mock().region_weather.assert_called_with(
                    weather='monsoon season', nxtweather='clear')
            
            weather = '  The weather was clear last month; it will be clear ' \
                      'next month.'
            consumer_mock.reset_mock()
            parser.parse_region(weather)
            consumer_mock().region_weather.assert_called_with(
                    weather='clear', nxtweather='clear')
            
            # Economy, wages
            wages = '  Wages: $12.4 (Max: $234).'
            consumer_mock.reset_mock()
            parser.parse_region(wages)
            consumer_mock().region_wages.assert_called_with(
                    productivity=12.4, amount=234)
            
            # Economy, no wages
            wages = '  Wages: $0.'
            consumer_mock.reset_mock()
            parser.parse_region(wages)
            consumer_mock().region_wages.assert_called_with(
                    productivity=0, amount=0)
            
            # Market, sell. No products
            market = '  Wanted: none.'
            consumer_mock.reset_mock()
            parser.parse_region(market)
            self.assertFalse(consumer_mock().region_market.called)
            
            # Market, sell.
            market = '  Wanted: 116 grain [GRAI] at $18, 113 livestock ' \
                     '[LIVE] at $18, 104 fish [FISH] at $24.'
            consumer_mock.reset_mock()
            parser.parse_region(market)
            consumer_mock().region_market.assert_called_with(
                    market='sell',
                    items=[ItemMarket(abr='GRAI', names='grain',
                                      amt=116, price=18),
                           ItemMarket(abr='LIVE', names='livestock',
                                      amt=113, price=18),
                           ItemMarket(abr='FISH', names='fish',
                                      amt=104, price=24)])
            
            # Market, buy
            market = '  For Sale: 240 plainsmen [PLAI] at $59, 48 leaders ' \
                     '[LEAD] at $118.'
            consumer_mock.reset_mock()
            parser.parse_region(market)
            consumer_mock().region_market.assert_called_with(
                    market='buy',
                    items=[ItemMarket(abr='PLAI', names='plainsmen',
                                      amt=240, price=59),
                           ItemMarket(abr='LEAD', names='leaders',
                                      amt=48, price=118)])
            
            # Entertainment
            entertainment = '  Entertainment available: $348.'
            consumer_mock.reset_mock()
            parser.parse_region(entertainment)
            consumer_mock().region_entertainment.assert_called_with(amount=348)
            
            # Products, none
            products = '  Products: none.'
            consumer_mock.reset_mock()
            parser.parse_region(products)
            self.assertFalse(consumer_mock().region_products.called)
            
            # Products
            products = '  Products: 56 livestock [LIVE], 37 horses [HORS].'
            consumer_mock.reset_mock()
            parser.parse_region(products)
            consumer_mock().region_products.assert_called_with(
                    products=[ItemAmount(abr='LIVE', names='livestock', amt=56),
                              ItemAmount(abr='HORS', names='horses', amt=37)])
            
            # Exits
            exits = '  Southeast : swamp (19,93) in Slamer.'
            consumer_mock.reset_mock()
            parser.parse_region(exits)
            consumer_mock().region_exits.assert_called_with(
                    direction='Southeast', name='Slamer', terrain='swamp',
                    xloc=19, yloc=93)
            
            exits = '  South : plain (21,93) in Isshire, contains Durshire ' \
                   '[town].'
            consumer_mock.reset_mock()
            parser.parse_region(exits)
            consumer_mock().region_exits.assert_called_with(
                    direction='South', name='Isshire', terrain='plain',
                    xloc=21, yloc=93, town={'name': 'Durshire', 'type': 'town'})
            
            # Gate
            gate = 'There is a Gate here (Gate 112).'
            consumer_mock.reset_mock()
            parser.parse_region(gate)
            consumer_mock().region_gate.assert_called_with(
                    gate=112, gateopen=True)
            
            gate = 'There is a closed Gate here.'
            consumer_mock.reset_mock()
            parser.parse_region(gate)
            consumer_mock().region_gate.assert_called_with(
                    gate=0, gateopen=False)
            
            # Object
            objects = '+ Pinta [102] : Galleon'
            consumer_mock.reset_mock()
            parser.parse_region(objects)
            consumer_mock().region_structure.assert_called_with(
                    name='Pinta', num=102, structure_type='Galleon')
            
            objects = '+ Fleet [104] : Fleet, 1 Galleon, 3 Longships'
            consumer_mock.reset_mock()
            parser.parse_region(objects)
            consumer_mock().region_structure.assert_called_with(
                    name='Fleet', num=104, structure_type='Fleet',
                    items=[ItemAmount(amt=1, name='Galleon'),
                           ItemAmount(amt=3, names='Longships')])
            
            objects = '+ Galleon [102] : Fleet, 2 Galleons'
            consumer_mock.reset_mock()
            parser.parse_region(objects)
            consumer_mock().region_structure.assert_called_with(
                    name='Galleon', num=102, structure_type='Fleet',
                    items=[ItemAmount(amt=2, names='Galleons')])
            
            objects = '+ Explendorosa [3] : Timber Yard, needs 3.'
            consumer_mock.reset_mock()
            parser.parse_region(objects)
            consumer_mock().region_structure.assert_called_with(
                    name='Explendorosa', num=3, structure_type='Timber Yard',
                    incomplete=3)
            
            objects = '+ Shaft [1] : Shaft, contains an inner location.'
            consumer_mock.reset_mock()
            parser.parse_region(objects)
            consumer_mock().region_structure.assert_called_with(
                    name='Shaft', num=1, structure_type='Shaft',
                    inner_location=True)
            
            objects = '+ Ruin [1] : Ruin, closed to player units.'
            consumer_mock.reset_mock()
            parser.parse_region(objects)
            consumer_mock().region_structure.assert_called_with(
                    name='Ruin', num=1, structure_type='Ruin', can_enter=False)
            
            # Units
            unit = '* Scout (1710), Mathoyoh (13), avoiding, behind, ' \
                   'receiving no aid, won\'t cross water, tribal elf [TELF], ' \
                   '51 silver [SILV]. Weight: 10. Capacity: 0/0/15/0. ' \
                   'Skills: combat [COMB] 1 (30).'
            consumer_mock.reset_mock()
            parser.parse_region(unit)
            consumer_mock().region_unit.assert_called_with(
                    name='Scout', num=1710, attitude='me',
                    faction={'name': 'Mathoyoh', 'num': 13},
                    guard='avoid', behind=True, noaid=True, nocross=True,
                    items=[ItemUnit(abr='TELF', name='tribal elf', amt=1),
                           ItemUnit(abr='SILV', names='silver', amt=51)],
                    skills=[SkillDays('COMB', 'combat', 1, 30)],
                    capacity={'riding': 0, 'flying': 0, 'walking': 15,
                              'swimming': 0}, weight=10)
            
            unit = '* Ship (468), Mathoyoh (3), avoiding, behind, won\'t ' \
                   'cross water, 10 vikings [VIKI], unfinished Galleon ' \
                   '[GALL] (needs 15). Weight: 100. Capacity: 0/0/150/0. ' \
                   'Skills: shipbuilding [SHIP] 3 (180).'
            consumer_mock.reset_mock()
            parser.parse_region(unit)
            consumer_mock().region_unit.assert_called_with(
                    name='Ship', num=468, attitude='me',
                    faction={'name': 'Mathoyoh', 'num': 3},
                    guard='avoid', behind=True, nocross=True,
                    items=[ItemUnit(abr='VIKI', names='vikings', amt=10),
                           ItemUnit(abr='GALL', name='Galleon', amt=1,
                                    unfinished=15)],
                    skills=[SkillDays('SHIP', 'shipbuilding', 3, 180)],
                    capacity={'riding': 0, 'flying': 0, 'walking': 150,
                              'swimming': 0}, weight=100)
            
            unit = '- City Guard (188), on guard, The Guardsmen (1), 80 ' \
                   'leaders [LEAD], 80 swords [SWOR].'
            consumer_mock.reset_mock()
            parser.parse_region(unit)
            consumer_mock().region_unit.assert_called_with(
                    name='City Guard', num=188, attitude='neutral',
                    items=[ItemUnit(abr='LEAD', names='leaders', amt=80),
                           ItemUnit(abr='SWOR', names='swords', amt=80)],
                    faction={'name': 'The Guardsmen', 'num': 1},
                    guard='guard')
            
            unit = '* ShArcashmo (397), Mathoyoh (13), behind, won\'t cross ' \
                   'water, leader [LEAD], 4 wolves [WOLF], 4 swords [SWOR], ' \
                   '24 horses [HORS]. Weight: 1254. Capacity: 0/1740/1755/0. ' \
                   'Skills: pattern [PATT] 2 (120), force [FORC] 1 (70), ' \
                   'weather lore [WEAT] 1 (30), clear skies [CLEA] 1 (30), ' \
                   'earth lore [EART] 2 (105), bird lore [BIRD] 2 (90), fire ' \
                   '[FIRE] 1 (30), earthquake [EQUA] 1 (30), wolf lore ' \
                   '[WOLF] 2 (100), observation [OBSE] 1 (60), stealth ' \
                   '[STEA] 1 (60), summon wind [SWIN] 1 (30), magical ' \
                   'healing [MHEA] 1 (60). Combat spell: fire [FIRE]. Can ' \
                   'Study: force shield [FSHI], energy shield [ESHI], ' \
                   'magical healing [MHEA], mind reading [MIND], summon ' \
                   'storm [SSTO], illusion [ILLU].'
            consumer_mock.reset_mock()
            parser.parse_region(unit)
            consumer_mock().region_unit.assert_called_with(
                    name='ShArcashmo', num=397, attitude='me',
                    faction={'name': 'Mathoyoh', 'num': 13},
                    behind=True, nocross=True,
                    items=[ItemUnit(abr='LEAD', name='leader', amt=1),
                           ItemUnit(abr='WOLF', names='wolves', amt=4),
                           ItemUnit(abr='SWOR', names='swords', amt=4),
                           ItemUnit(abr='HORS', names='horses', amt=24)],
                    capacity={'riding': 1740, 'flying': 0, 'walking': 1755,
                              'swimming': 0}, weight=1254,
                    combat=Skill(abr='FIRE', name='fire'),
                    skills=[SkillDays('PATT', 'pattern', 2, 120),
                            SkillDays('FORC', 'force', 1, 70),
                            SkillDays('WEAT', 'weather lore', 1, 30),
                            SkillDays('CLEA', 'clear skies', 1, 30),
                            SkillDays('EART', 'earth lore', 2, 105),
                            SkillDays('BIRD', 'bird lore', 2, 90),
                            SkillDays('FIRE', 'fire', 1, 30),
                            SkillDays('EQUA', 'earthquake', 1, 30),
                            SkillDays('WOLF', 'wolf lore', 2, 100),
                            SkillDays('OBSE', 'observation', 1, 60),
                            SkillDays('STEA', 'stealth', 1, 60),
                            SkillDays('SWIN', 'summon wind', 1, 30),
                            SkillDays('MHEA', 'magical healing', 1, 60)],
                    canstudy=[Skill(abr='FSHI', name='force shield'),
                              Skill(abr='ESHI', name='energy shield'),
                              Skill(abr='MHEA', name='magical healing'),
                              Skill(abr='MIND', name='mind reading'),
                              Skill(abr='SSTO', name='summon storm'),
                              Skill(abr='ILLU', name='illusion')])
            
            # Unit. Ready
            unit = '* Garrison (3286), on guard, Fhetoky (21), tribal elf ' \
                   '[TELF], sword [SWOR], leather armor [LARM], censer of ' \
                   'protection [CNSR]. Weight: 12. Capacity: 0/0/15/0. ' \
                   'Skills: combat [COMB] 2 (90). Ready weapon: sword ' \
                   '[SWOR]. Ready armor: leather armor [LARM]. Ready item: ' \
                   'censer of protection [CNSR].'
            consumer_mock.reset_mock()
            parser.parse_region(unit)
            consumer_mock().region_unit.assert_called_with(
                    name='Garrison', num=3286, attitude='me',
                    faction={'name': 'Fhetoky', 'num': 21}, guard='guard',
                    items=[ItemUnit(abr='TELF', name='tribal elf', amt=1),
                           ItemUnit(abr='SWOR', name='sword', amt=1),
                           ItemUnit(abr='LARM', name='leather armor', amt=1),
                           ItemUnit(abr='CNSR', name='censer of protection',
                                    amt=1)],
                    capacity={'riding': 0, 'flying': 0, 'walking': 15,
                              'swimming': 0}, weight=12,
                    skills=[SkillDays('COMB', 'combat', 2, 90)],
                    readyweapon=[Item(abr='SWOR', name='sword')],
                    readyarmor=[Item(abr='LARM', name='leather armor')],
                    readyitem=[Item(abr='CNSR', name='censer of protection')])

if __name__ == '__main__':
    unittest.main()
