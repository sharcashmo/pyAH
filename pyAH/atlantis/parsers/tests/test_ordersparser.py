"""Unit tests for atlantis.reportparser module"""

from atlantis.parsers.ordersparser import OrdersParser
from atlantis.parsers import ordersparser  # @UnusedImport

try:
    from unittest.mock import patch  # @UnresolvedImport @UnusedImport
except:
    from mock import patch  # @UnresolvedImport @Reimport

import unittest
from collections import deque

class TestOrdersParser(unittest.TestCase):
    """Test OrdersParser class
    
    Tests run by this class are:
    test_tokenize  Test tokenize method
    
    """
    
    def test_tokenize(self):
        """Test OrdersParser.tokenize method
        
        OrdersParser.tokenize method works in the same way Atlantis
        tokenizer works.
        
        If the first character is an at sign (@) then permanent mark
        is set. Double quotes do surround a text token and special
        characters inside double quotes are ignored. Unmatched quotes
        raise a SyntaxError exception. Spaces and tabs are the token
        delimiters and semicolon signals a comment.
        
        """
        
        orders = 'move north 127 a'
        self.assertEqual(OrdersParser.tokenize(orders),
                         (deque(['move', 'north', '127', 'a']), False, None))
        
        orders = 'cast "Earth Lore" 27; Casting'
        self.assertEqual(OrdersParser.tokenize(orders),
                         (deque(['cast', 'Earth Lore', '27']),
                          False, ' Casting'))
        
        orders = '@produce wood ;Producing wood'
        self.assertEqual(OrdersParser.tokenize(orders),
                         (deque(['produce', 'wood']), True, 'Producing wood'))
        
        orders = 'cast p@#" ;Special characters inside a token'
        self.assertEqual(OrdersParser.tokenize(orders),
                         (deque(['cast', 'p@#"']), False,
                          'Special characters inside a token'))
        
        orders = '#atlantis "Bart ;Unmatched quotes'
        self.assertRaises(SyntaxError, OrdersParser.tokenize, orders)
    
    def test_parse_line(self):
        """Test OrdersParser.parse_line method
        
        Several tests are performed for each possible order
        
        """
        with patch(__name__ + '.ordersparser.OrdersConsumer') as consumer_mock:
            parser = OrdersParser(consumer_mock())
            
            # atlantis statement
            order = '#atLAntis 127 "pergamino"'
            parser.parse_line(order)    
            consumer_mock().atlantis.assert_called_with(
                    faction=127, password='pergamino')
            
            order = '#aTlantis 13' 
            consumer_mock.reset_mock()
            parser.parse_line(order)    
            consumer_mock().atlantis.assert_called_with(
                    faction=13)
            
            order = '#atlaNTIs' 
            consumer_mock.reset_mock()
            self.assertRaises(SyntaxError, parser.parse_line, order)
            
            order = '#eND'
            consumer_mock.reset_mock()
            parser.parse_line(order)    
            consumer_mock().atlantis_end.assert_called_with()
            
            order = 'Unit 123'
            consumer_mock.reset_mock()
            parser.parse_line(order)    
            consumer_mock().unit.assert_called_with(
                    unit=123)
            
            order = 'uniT' 
            consumer_mock.reset_mock()
            self.assertRaises(SyntaxError, parser.parse_line, order)
            
            order = 'unit 0' 
            consumer_mock.reset_mock()
            self.assertRaises(SyntaxError, parser.parse_line, order)
            
            order = '@foRm 1 ;Form messenger'
            consumer_mock.reset_mock()
            parser.parse_line(order)    
            consumer_mock().order_form.assert_called_with(
                    alias=1, permanent=True, comment='Form messenger')
            
            order = 'form ;Form messenger'
            consumer_mock.reset_mock()
            self.assertRaises(SyntaxError, parser.parse_line, order)
            
            order = 'eND'
            consumer_mock.reset_mock()
            parser.parse_line(order)    
            consumer_mock().order_end.assert_called_with()
            
            order = '@TURN'
            consumer_mock.reset_mock()
            parser.parse_line(order)    
            consumer_mock().order_turn.assert_called_with(
                    permanent=True, comment=None)
            
            order = 'ENDTURN'
            consumer_mock.reset_mock()
            parser.parse_line(order)    
            consumer_mock().order_endturn.assert_called_with()
            
            order = 'Address "shar1@arrakis.es"'
            consumer_mock.reset_mock()
            parser.parse_line(order)    
            consumer_mock().order_address.assert_called_with(
                    address='shar1@arrakis.es', permanent=False, comment=None)
            
            order = '@ADvance N norTheast IN out 2'
            consumer_mock.reset_mock()
            parser.parse_line(order)    
            consumer_mock().order_advance.assert_called_with(
                    dirs=['n', 'ne', 'in', 'out', 2],
                    permanent=True, comment=None)
            
            order = 'ASSASSINATE 101'
            consumer_mock.reset_mock()
            parser.parse_line(order)    
            consumer_mock().order_assassinate.assert_called_with(
                    unit={'unitnum': 101}, permanent=False, comment=None)
            
            order = 'attacK 21 453 12 FACTION 12 NEW 1'
            consumer_mock.reset_mock()
            parser.parse_line(order)    
            consumer_mock().order_attack.assert_called_with(
                    targets=[{'unitnum': 21}, {'unitnum': 453},
                             {'unitnum': 12}, {'faction': 12, 'alias': 1}],
                    permanent=False, comment=None)
            
            order = 'AUTOTAX ON'
            consumer_mock.reset_mock()
            parser.parse_line(order)    
            consumer_mock().order_autotax.assert_called_with(
                    flag=True, permanent=False, comment=None)
            
            order = 'AVOID F'
            consumer_mock.reset_mock()
            parser.parse_line(order)    
            consumer_mock().order_avoid.assert_called_with(
                    flag=False, permanent=False, comment=None)
            
            order = 'IDLE'
            consumer_mock.reset_mock()
            parser.parse_line(order)    
            consumer_mock().order_idle.assert_called_with(permanent=False,
                                                          comment=None)
            
            order = 'Behind Yes'
            consumer_mock.reset_mock()
            parser.parse_line(order)    
            consumer_mock().order_behind.assert_called_with(
                    flag=True, permanent=False, comment=None)
            
            order = 'BUILD'
            consumer_mock.reset_mock()
            parser.parse_line(order)    
            consumer_mock().order_build.assert_called_with(permanent=False,
                                                           comment=None)
            
            order = 'BUILD HELP FACTION 12 NEW 15'
            consumer_mock.reset_mock()
            parser.parse_line(order)    
            consumer_mock().order_build.assert_called_with(
                    target={'faction': 12, 'alias': 15},
                    permanent=False, comment=None)
            
            order = 'BUILD "tIMBeR YaRd"'
            consumer_mock.reset_mock()
            parser.parse_line(order)    
            consumer_mock().order_build.assert_called_with(
                    structure='timber yard',
                    permanent=False, comment=None)
            
            order = 'BUY all peas'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_buy.assert_called_with(
                    num=OrdersParser.AMT_ALL, item='peas',
                    permanent=False, comment=None)
            
            order = 'CAST Bird_Lore N'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_cast.assert_called_with(
                    skill='bird_lore', params=['n'],
                    permanent=False, comment=None)
            
            order = 'Claim 10'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_claim.assert_called_with(
                    num=10, permanent=False, comment=None)
            
            order = 'COMBAT Earth_Lore'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_combat.assert_called_with(
                    skill='earth_lore', permanent=False, comment=None)
            
            order = 'CONSUME'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_consume.assert_called_with(
                    consuming='none', permanent=False, comment=None)
            
            order = 'Declare 15'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_declare.assert_called_with(
                    faction=15, permanent=False, comment=None)
            
            order = 'DECLARE DEFAULT friendly'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_declare.assert_called_with(
                    faction='default', attitude='friendly',
                    permanent=False, comment=None)
            
            order = 'DECLARE 26 HOSTILE'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_declare.assert_called_with(
                    faction=26, attitude='hostile',
                    permanent=False, comment=None)
            
            order = 'DESCRIBE UNIT'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_describe.assert_called_with(
                    unit=None, permanent=False, comment=None)
            
            order = 'DESCRIBE STRUCTURE "Mi casa"'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_describe.assert_called_with(
                    structure='Mi casa', permanent=False, comment=None)
            
            order = 'DESTROY'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_destroy.assert_called_with(
                    permanent=False, comment=None)
            
            order = 'ENTER 12'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_enter.assert_called_with(
                    structure=12, permanent=False, comment=None)
            
            order = '@Entertain'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_entertain.assert_called_with(
                    permanent=True, comment=None)
            
            order = 'evict 21 453 12 FACTION 12 NEW 1 0 bad-number'
            consumer_mock.reset_mock()
            self.assertRaises(SyntaxError, parser.parse_line, order)
            consumer_mock().order_evict.assert_called_with(
                    targets=[{'unitnum': 21}, {'unitnum': 453},
                             {'unitnum': 12}, {'faction': 12, 'alias': 1}],
                    permanent=False, comment=None)
            
            order = '@exchange 123 200 silv 50 swor ; Buying swords'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_exchange.assert_called_with(
                    target={'unitnum': 123}, give={'amt': 200, 'item': 'silv'},
                    expected={'amt': 50, 'item': 'swor'},
                    permanent=True, comment=' Buying swords')
            
            order = 'faction war 2 trade 1 magic 2'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_faction.assert_called_with(
                    war=2, trade=1, magic=2, permanent=False, comment=None)
            
            order = 'find all'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_find.assert_called_with(
                    faction='all', permanent=False, comment=None)
            
            order = 'find 13'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_find.assert_called_with(
                    faction=13, permanent=False, comment=None)
            
            order = 'forget comb'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_forget.assert_called_with(
                    skill='comb', permanent=False, comment=None)
            
            order = 'withdraw hors'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_withdraw.assert_called_with(
                    item='hors', amt=1, permanent=False, comment=None)
            
            order = 'withdraw 10 iron'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_withdraw.assert_called_with(
                    item='iron', amt=10, permanent=False, comment=None)
            
            order = 'give 101 unit'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_give.assert_called_with(
                    target={'unitnum': 101}, give='unit',
                    permanent=False, comment=None)
            
            order = 'give 23 13 iron'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_give.assert_called_with(
                    target={'unitnum': 23},
                    give={'amt': 13, 'item': 'iron', 'unfinished': False},
                    permanent=False, comment=None)
            
            order = 'give faction 13 new 2 all men'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_give.assert_called_with(
                    target={'faction': 13, 'alias': 2},
                    give={'amt': 'all', 'item': 'men', 'unfinished': False},
                    permanent=False, comment=None)
            
            order = 'give new 1 all unfinished wood except 13'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_give.assert_called_with(
                    target={'alias': 1},
                    give={'amt': 'all', 'item': 'wood',
                          'unfinished': True, 'excpt': 13},
                    permanent=False, comment=None)
            
            order = 'give 114 14 wood except 13'
            consumer_mock.reset_mock()
            self.assertRaises(SyntaxError, parser.parse_line, order)
            
            order = 'guard 0'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_guard.assert_called_with(
                    flag=False, permanent=False, comment=None)
            
            order = 'hold 1'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_hold.assert_called_with(
                    flag=True, permanent=False, comment=None)
            
            order = 'join new 3 nooverload'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_join.assert_called_with(
                    target={'alias': 3}, nooverload=True,
                    permanent=False, comment=None)
            
            order = 'join 103'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_join.assert_called_with(
                    target={'unitnum': 103}, permanent=False, comment=None)
            
            order = 'leave'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_leave.assert_called_with(
                    permanent=False, comment=None)
            
            order = 'Move N norTheast IN out 2'
            consumer_mock.reset_mock()
            parser.parse_line(order)    
            consumer_mock().order_move.assert_called_with(
                    dirs=['n', 'ne', 'in', 'out', 2],
                    permanent=False, comment=None)
            
            order = 'name unit "Pedro el Grande"'
            consumer_mock.reset_mock()
            parser.parse_line(order)    
            consumer_mock().order_name.assert_called_with(
                    unit='Pedro el Grande', permanent=False, comment=None)
            
            order = 'NAME BUILDING "Mi casa"'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_name.assert_called_with(
                    structure='Mi casa', permanent=False, comment=None)
            
            order = 'name village "¡Año Mariano!"'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_name.assert_called_with(
                    city='Ao Mariano!', permanent=False, comment=None)
            
            order = 'noaid 1'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_noaid.assert_called_with(
                    flag=True, permanent=False, comment=None)
            
            order = 'nocross 1'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_nocross.assert_called_with(
                    flag=True, permanent=False, comment=None)
            
            order = 'nospoils 0'
            consumer_mock.reset_mock()
            self.assertRaises(DeprecationWarning, parser.parse_line, order)
            consumer_mock().order_spoils.assert_called_with(
                    spoils='all', permanent=False, comment=None)
            
            order = 'option notimes'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_option.assert_called_with(
                    times=False, permanent=False, comment=None)
            
            order = 'option showattitudes'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_option.assert_called_with(
                    showunitattitudes=True, permanent=False, comment=None)
            
            order = 'option template map'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_option.assert_called_with(
                    temformat='map', permanent=False, comment=None)
            
            order = 'password'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_password.assert_called_with(
                    password='none', permanent=False, comment=None)
            
            order = 'pillage'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_pillage.assert_called_with(
                    permanent=False, comment=None)
            
            order = 'prepare'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_prepare.assert_called_with(
                    item=None, permanent=False, comment=None)
            
            order = 'prepare staf'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_prepare.assert_called_with(
                    item='staf', permanent=False, comment=None)
            
            order = 'weapon'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_weapon.assert_called_with(
                    items=[], permanent=False, comment=None)
            
            order = 'weapon baxe swor axe'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_weapon.assert_called_with(
                    items=['baxe', 'swor', 'axe'],
                    permanent=False, comment=None)
            
            order = 'armor'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_armor.assert_called_with(
                    items=[], permanent=False, comment=None)
            
            order = 'armor parm carm larm'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_armor.assert_called_with(
                    items=['parm', 'carm', 'larm'],
                    permanent=False, comment=None)
            
            order = 'produce 10 axe'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_produce.assert_called_with(
                    target=10, item='axe', permanent=False, comment=None)
            
            order = '@produce wood'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_produce.assert_called_with(
                    item='wood', permanent=True, comment=None)
            
            order = 'promote new 1'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_promote.assert_called_with(
                    unit={'alias': 1}, permanent=False, comment=None)
            
            order = 'quit "mipassword"'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_quit.assert_called_with(
                    password='mipassword', permanent=False, comment=None)
            
            order = 'restart "mipassword"'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_restart.assert_called_with(
                    password='mipassword', permanent=False, comment=None)
            
            order = 'reveal'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_reveal.assert_called_with(
                    reveal=None, permanent=False, comment=None)
            
            order = 'reveal unit'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_reveal.assert_called_with(
                    reveal='unit', permanent=False, comment=None)
            
            order = 'sail N norTheast pause'
            consumer_mock.reset_mock()
            parser.parse_line(order)    
            consumer_mock().order_sail.assert_called_with(
                    dirs=['n', 'ne', 'p'],
                    permanent=False, comment=None)
            
            order = 'sail N 2 norTheast pause'
            consumer_mock.reset_mock()
            self.assertRaises(SyntaxError, parser.parse_line, order)
            
            order = 'sell 10 axe'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_sell.assert_called_with(
                    num=10, item='axe', permanent=False, comment=None)
            
            order = 'share 1'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_share.assert_called_with(
                    flag=True, permanent=False, comment=None)
            
            order = 'show item swor'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_show.assert_called_with(
                    item='swor', permanent=False, comment=None)
            
            order = 'show skill forc'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_show.assert_called_with(
                    skill='forc', permanent=False, comment=None)
            
            order = 'show object Castle'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_show.assert_called_with(
                    structure='castle', permanent=False, comment=None)
            
            order = 'spoils fly'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_spoils.assert_called_with(
                    spoils='fly', permanent=False, comment=None)
            
            order = 'steal 2017 silv'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_steal.assert_called_with(
                    target={'unitnum': 2017}, item='silv',
                    permanent=False, comment=None)
            
            order = 'study comb'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_study.assert_called_with(
                    skill='comb', permanent=False, comment=None)
            
            order = 'study ship 3'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_study.assert_called_with(
                    skill='ship', level=3, permanent=False, comment=None)
            
            order = 'take from 23 13 iron'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_takefrom.assert_called_with(
                    target={'unitnum': 23},
                    give={'amt': 13, 'item': 'iron', 'unfinished': False},
                    permanent=False, comment=None)
            
            order = 'take from faction 13 new 2 all men'
            consumer_mock.reset_mock()
            self.assertRaises(SyntaxError, parser.parse_line, order)
            
            order = 'take from 103 all unfinished wood except 13'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_takefrom.assert_called_with(
                    target={'unitnum': 103},
                    give={'amt': 'all', 'item': 'wood',
                          'unfinished': True, 'excpt': 13},
                    permanent=False, comment=None)
            
            order = 'take from 114 14 wood except 13'
            consumer_mock.reset_mock()
            self.assertRaises(SyntaxError, parser.parse_line, order)
            
            order = 'tax'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_tax.assert_called_with(
                    permanent=False, comment=None)
            
            order = 'teach 21 453 12 FACTION 12 NEW 1'
            consumer_mock.reset_mock()
            parser.parse_line(order)    
            consumer_mock().order_teach.assert_called_with(
                    targets=[{'unitnum': 21}, {'unitnum': 453},
                             {'unitnum': 12}, {'faction': 12, 'alias': 1}],
                    permanent=False, comment=None)
            
            order = 'work'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_work.assert_called_with(
                    permanent=False, comment=None)
            
            order = 'transport 101 unit'
            consumer_mock.reset_mock()
            self.assertRaises(SyntaxError, parser.parse_line, order)
            
            order = 'transport 23 13 iron'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_transport.assert_called_with(
                    target={'unitnum': 23},
                    give={'amt': 13, 'item': 'iron', 'unfinished': False},
                    permanent=False, comment=None)
            
            order = 'transport faction 13 new 2 all men'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_transport.assert_called_with(
                    target={'faction': 13, 'alias': 2},
                    give={'amt': 'all', 'item': 'men', 'unfinished': False},
                    permanent=False, comment=None)
            
            order = 'transport new 1 all unfinished wood except 13'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_transport.assert_called_with(
                    target={'alias': 1},
                    give={'amt': 'all', 'item': 'wood',
                          'unfinished': True, 'excpt': 13},
                    permanent=False, comment=None)
            
            order = 'transport 114 14 wood except 13'
            consumer_mock.reset_mock()
            self.assertRaises(SyntaxError, parser.parse_line, order)
            
            order = 'distribute 101 unit'
            consumer_mock.reset_mock()
            self.assertRaises(SyntaxError, parser.parse_line, order)
            
            order = 'distribute 23 13 iron'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_distribute.assert_called_with(
                    target={'unitnum': 23},
                    give={'amt': 13, 'item': 'iron', 'unfinished': False},
                    permanent=False, comment=None)
            
            order = 'distribute faction 13 new 2 all men'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_distribute.assert_called_with(
                    target={'faction': 13, 'alias': 2},
                    give={'amt': 'all', 'item': 'men', 'unfinished': False},
                    permanent=False, comment=None)
            
            order = 'distribute new 1 all unfinished wood except 13'
            consumer_mock.reset_mock()
            parser.parse_line(order)
            consumer_mock().order_distribute.assert_called_with(
                    target={'alias': 1},
                    give={'amt': 'all', 'item': 'wood',
                          'unfinished': True, 'excpt': 13},
                    permanent=False, comment=None)
            
            order = 'distribute 114 14 wood except 13'
            consumer_mock.reset_mock()
            self.assertRaises(SyntaxError, parser.parse_line, order)

if __name__ == '__main__':
    unittest.main()
