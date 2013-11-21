"""Unit tests for atlantis.gamedata.region module."""

from atlantis.gamedata.region import Region
from atlantis.gamedata.item import ItemAmount, ItemMarket

from io import StringIO

import json
import unittest

class TestRegion(unittest.TestCase):
    """Test Region class."""
    
    def test_constructor(self):
        """Test Region constructor."""
        region = Region((21, 93, None), 'plain', 'Isshire',
                        2392, 'vikings', 11016,
                        {'name': 'Durshire', 'type': 'town'})
        self.assertEqual(region.location, (21, 93, None))
        self.assertEqual(region.terrain, 'plain')
        self.assertEqual(region.name, 'Isshire')
        self.assertEqual(region.population, 2392)
        self.assertEqual(region.racenames, 'vikings')
        self.assertEqual(region.wealth, 11016)
        self.assertEqual(region.town, {'name': 'Durshire', 'type': 'town'})
        
        region = Region((21,93, None), 'plain', 'Isshire',
                        town={'name': 'Durshire', 'type': 'town'})
        self.assertEqual(region.location, (21, 93, None))
        self.assertEqual(region.terrain, 'plain')
        self.assertEqual(region.name, 'Isshire')
        self.assertEqual(region.population, 0)
        self.assertIsNone(region.racenames)
        self.assertEqual(region.wealth, 0)
        self.assertEqual(region.town, {'name': 'Durshire', 'type': 'town'})
    
    def test_append_report_description(self):
        """Test Region.append_report_description method."""
        region = Region((21, 93, None), 'plain', 'Isshire',
                        2392, 'vikings', 11016,
                        {'name': 'Durshire', 'type': 'town'})
        
        lines = ['plain (21,93) in Isshire, contains Durshire [town], 9836 '
                 'peasants (vikings), $11016.',
                 '------------------------------------------------------------',
                 '  The weather was clear last month; it will be clear next '
                 'month.',
                 '  Wages: $15.6 (Max: $3672).',
                 '  Wanted: 171 grain [GRAI] at $24, 109 livestock [LIVE] at '
                 '$24, 139 fish [FISH] at $23, 4 leather armor [LARM] at $90, '
                 'sword [SWOR] at $101.',
                 '  For Sale: 393 vikings [VIKI] at $62, 78 leaders [LEAD] at '
                 '$124.',
                 '  Entertainment available: $649.']
        
        for l in lines:
            region.append_report_description(l)
        
        self.assertEqual(region.report, lines)
    
    def test_set_weather(self):
        """Test Region.set_weather method."""
        region = Region((21, 93, None), 'plain', 'Isshire',
                        2392, 'vikings', 11016,
                        {'name': 'Durshire', 'type': 'town'})
        region.set_weather('clear', 'winter', True, False)
        
        self.assertEqual(region.weather,
                         {'last': 'clear', 'next': 'winter',
                          'clearskies': True, 'blizzard': False})
    
    def test_set_wages(self):
        """Test Region.set_wages method."""
        region = Region((21, 93, None), 'plain', 'Isshire',
                        2392, 'vikings', 11016,
                        {'name': 'Durshire', 'type': 'town'})
        region.set_wages(15.6, 3672)
        
        self.assertEqual(region.wages, {'productivity': 15.6, 'amount': 3672})
    
    def test_set_market(self):
        """Test Region.set_market method."""
        region = Region((21, 93, None), 'plain', 'Isshire',
                        2392, 'vikings', 11016,
                        {'name': 'Durshire', 'type': 'town'})
        region.set_market('sell',
                          [ItemMarket('GRAI', 171, 24, names='grain'),
                           ItemMarket('LIVE', 109, 24, names='livestock'),
                           ItemMarket('FISH', 139, 23, names='fish'),
                           ItemMarket('LARM', 4, 90, names='leather armor'),
                           ItemMarket('SWOR', 1, 101, name='sword')])
        
        self.assertEqual(region.market,
                         {'sell': [
                             ItemMarket('GRAI', 171, 24, names='grain'),
                             ItemMarket('LIVE', 109, 24, names='livestock'),
                             ItemMarket('FISH', 139, 23, names='fish'),
                             ItemMarket('LARM', 4, 90, names='leather armor'),
                             ItemMarket('SWOR', 1, 101, name='sword')]})
    
    def test_set_entertainment(self):
        """Test Region.set_entertainment method."""
        region = Region((21, 93, None), 'plain', 'Isshire',
                        2392, 'vikings', 11016,
                        {'name': 'Durshire', 'type': 'town'})
        region.set_entertainment(649)
        
        self.assertEqual(region.entertainment, 649)
    
    def test_set_products(self):
        """Test Region.set_products method."""
        region = Region((21, 93, None), 'plain', 'Isshire',
                        2392, 'vikings', 11016,
                        {'name': 'Durshire', 'type': 'town'})
        region.set_products([ItemAmount('LIVE', 66, names='livestock')])
        
        self.assertEqual(region.products,
                         [ItemAmount('LIVE', 66, names='livestock')])
    
    def test_set_exit(self):
        """Test Region.set_exit method."""
        region = Region((21, 93, None), 'plain', 'Isshire',
                        2392, 'vikings', 11016,
                        {'name': 'Durshire', 'type': 'town'})
        region.set_exit('north', (21,91, None))
        
        self.assertEqual(region.exits, {'north': (21, 91, None)})
    
    def test_set_gate(self):
        """Test Region.set_gate method."""
        region = Region((21, 93, None), 'plain', 'Isshire',
                        2392, 'vikings', 11016,
                        {'name': 'Durshire', 'type': 'town'})
        region.set_gate(12, True)
        
        self.assertEqual(region.gate, {'number': 12, 'is_open': True})

    def test_json_methods(self):
        """Test implementation of JsonSerializable interface."""
        io = StringIO()
        
        region = Region((21, 93, None), 'plain', 'Isshire',
                        2392, 'vikings', 11016,
                        {'name': 'Durshire', 'type': 'town'})
        json.dump(region, io, default=Region.json_serialize)
        io.seek(0)
        region_new = Region.json_deserialize(json.load(io))
        self.assertEqual(region, region_new)
        
        region.append_report_description('plain (21,93) in Isshire, contains '
                                         'Durshire [town], 9836 peasants '
                                         '(vikings), $11016.')
        region.append_report_description('------------------------------'
                                         '------------------------------')
        region.append_report_description('  The weather was clear last month; '
                                         'it will be clear next month.')
        region.set_weather('clear', 'clear')
        region.append_report_description('  Wages: $15.6 (Max: $3672).')
        region.set_wages(15.6, 3672)
        region.append_report_description('  Wanted: 171 grain [GRAI] at $24, '
                                         '109 livestock [LIVE] at $24, 139 '
                                         'fish [FISH] at $23, 4 leather armor '
                                         '[LARM] at $90, sword [SWOR] at $101.')
        region.set_market('sell',
                          [ItemMarket('GRAI', 171, 24, names='grain'),
                           ItemMarket('LIVE', 109, 24, names='livestock'),
                           ItemMarket('FISH', 139, 23, names='fish'),
                           ItemMarket('LARM', 4, 90, names='leather armor'),
                           ItemMarket('SWOR', 1, 101, name='sword')])
        region.append_report_description('  For Sale: 393 vikings [VIKI] at $62,'
                                         ' 78 leaders [LEAD] at $124.')
        region.set_market('buy',
                          [ItemMarket('VIKI', 393, 62, 'vikings'),
                           ItemMarket('LEAD', 78, 124, 'leaders')])
        region.append_report_description('  Entertainment available: $649.')
        region.set_entertainment(649)
        region.append_report_description('  Products: 66 livestock [LIVE].')
        region.set_products([ItemAmount('LIVE', 66, names='livestock')])
        region.append_report_description('')
        region.append_report_description('Exits:')
        region.append_report_description("  North : forest (19,91) in Ny'intu.")
        region.set_exit('north', (19, 91, None))
        
        io.seek(0)
        io.truncate()
        json.dump(region, io, default=Region.json_serialize)
        io.seek(0)
        region_new = Region.json_deserialize(json.load(io))
        self.assertEqual(region, region_new)

if __name__ == '__main__':
    unittest.main()
