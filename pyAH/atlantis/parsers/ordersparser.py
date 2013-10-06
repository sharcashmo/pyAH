"""This module implements all classes needed to parse order files.

It defines a :class:`OrdersParser` which will parse report lines and
will call a :class:`OrdersConsumer` with parser data. Classes willing
to consume data parser by :class:`OrdersParser` will have to implement
:class:`OrdersConsumer` interface.

"""

import re
from collections import deque

# Directions
directions = {'n': 'north', 'ne': 'northeast', 'se': 'southeast',
              's': 'south', 'sw': 'southweast', 'nw': 'northweast',
              'in': 'in', 'out': 'out', 'p': 'pause'}

class OrdersConsumer:
    """Virtual class for :class:`OrdersParser` consumer.
    
    This is an interface for classes willing to receive data from the
    :class:`OrdersParser`. Classes implementing this interface should
    overwrite their public methods.
    
    """
    pass

class OrdersParser:
    """Atlantis orders parser.
    
    :class:`!OrdersParser` is in charge of parsing an orders file, or
    the orders template part of an Atlantis PBEM report, and sends
    parsing result to its registered :class:`OrdersConsumer` together
    with the original line, in case the :class:`OrdersConsumer` needs
    it for description, as it happens with comments.
    
    """
    
    # Class constants
    UNIT_ANY, AMT_ALL, IT_NONE = -1, -1, -1
    
    # Member attributes
    _consumer = None
    
    def __init__(self, consumer):
        """Parser initializer.
        
        Its only parameter is the consumer (must implmement
        OrdersConsumer interface) of the parsed report.
        
        Parameter:
        consumer  OrdersConsumer instance to which parsed elements will
                  be sent
        
        """
        self._consumer = consumer
        
    def parse(self, f):
        """Read orders from an open file and parse them
        
        This method read lines from an open file. lines all passed
        to parse_line until the file ends.
        
        Parameters:
        f  Open file instance to be read
        
        """
        
        for line in f:
            self.parse_line(line)
            
    def parse_line(self, line):
        """Parse an orders line.
        
        Read line is always sent to the consumer before stripping
        them from its comments. The order line is parsed and its
        contents sent to the consumer.
        
        Parameters:
        line  Line being parsed
        
        """
        tokens, permanent, comment = OrdersParser.tokenize(line)
        
        if not tokens:
            if comment:
                self._consumer.comment(permanent=permanent, comment=comment)
            return
                
        order = tokens.popleft().lower()
            
        if order == '#atlantis':
            if not tokens:
                raise SyntaxError('{}: missing faction'.format(line))
            faction = OrdersParser._value(tokens.popleft())
            try:
                password = tokens.popleft()
            except IndexError:
                self._consumer.atlantis(faction=faction)
            else:
                self._consumer.atlantis(faction=faction,
                                        password=password)
                
        elif order == '#end':
            self._consumer.atlantis_end()
            
        elif order == 'unit':
            if not tokens:
                raise SyntaxError('{}: missing unit'.format(line))
            else:
                unit = OrdersParser._value(tokens.popleft())
                if not unit:
                    raise SyntaxError('{}: invalid unit'.format(line))
                self._consumer.unit(unit=unit)
                
        elif order == 'form':
            if not tokens:
                raise SyntaxError('{}: missing alias'.format(line))
            else:
                alias = OrdersParser._value(tokens.popleft())
                if not alias:
                    raise SyntaxError('{}: invalid alias'.format(line))
                self._consumer.order_form(alias=alias, permanent=permanent,
                                          comment=comment)
        elif order == 'end':
            self._consumer.order_end()
            
        elif order == 'turn':
            self._consumer.order_turn(permanent=permanent, comment=comment)
        
        elif order == 'endturn':
            self._consumer.order_endturn()
        
        elif order == 'address':
            if not tokens:
                raise SyntaxError('{}: missing address'.format(line))
            else:
                self._consumer.order_address(address=tokens.popleft(),
                                             permanent=permanent,
                                             comment=comment)
        
        elif order == 'advance':
            try:
                dirs = [OrdersParser._parse_dir(d.lower()) for d in tokens]
            except SyntaxError as e:
                raise SyntaxError('{}: {}'.format(line, e))
            else:
                self._consumer.order_advance(dirs=dirs, permanent=permanent,
                                             comment=comment)
        
        elif order == 'assassinate':
            try:
                unit = OrdersParser._parse_unit(tokens)
            except SyntaxError as e:
                raise SyntaxError('{}: {}'.format(line, e))
            else:
                self._consumer.order_assassinate(unit=unit,
                                                 permanent=permanent,
                                                 comment=comment)
        
        elif order == 'attack':
            targets = []
            try:
                while tokens:
                    targets.append(OrdersParser._parse_unit(tokens))
            except SyntaxError as e:
                self._consumer.order_attack(targets=targets,
                                            permanent=permanent,
                                            comment=comment)
                raise SyntaxError('{}: {}'.format(line, e))
            else:
                self._consumer.order_attack(targets=targets,
                                            permanent=permanent,
                                            comment=comment)
        
        elif order == 'autotax':
            if not tokens:
                raise SyntaxError('{}: missing value'.format(line))
            try:
                self._consumer.order_autotax(
                        flag=OrdersParser._parse_TF(tokens.popleft()),
                        permanent=permanent, comment=comment)
            except SyntaxError as e:
                raise SyntaxError('{}: {}'.format(line, e))
        
        elif order == 'avoid':
            if not tokens:
                raise SyntaxError('{}: missing value'.format(line))
            try:
                self._consumer.order_avoid(
                        flag=OrdersParser._parse_TF(tokens.popleft()),
                        permanent=permanent, comment=comment)
            except SyntaxError as e:
                raise SyntaxError('{}: {}'.format(line, e))
        
        elif order == 'idle':
            self._consumer.order_idle(permanent=permanent, comment=comment)
        
        elif order == 'behind':
            if not tokens:
                raise SyntaxError('{}: missing value'.format(line))
            try:
                self._consumer.order_behind(
                        flag=OrdersParser._parse_TF(tokens.popleft()),
                        permanent=permanent, comment=comment)
            except SyntaxError as e:
                raise SyntaxError('{}: {}'.format(line, e))
        
        elif order == 'build':
            if not tokens:
                self._consumer.order_build(permanent=permanent, comment=comment)
            else:
                tok = tokens.popleft().lower()
                if tok == 'help':
                    try:
                        target = OrdersParser._parse_unit(tokens)
                    except SyntaxError as e:
                        raise SyntaxError('{}: {}'.format(line, e))
                    else:
                        self._consumer.order_build(target=target,
                                                   permanent=permanent,
                                                   comment=comment)
                else:
                    self._consumer.order_build(structure=tok,
                                               permanent=permanent,
                                               comment=comment)
                    
        elif order == 'buy':
            if not tokens:
                raise SyntaxError('{}: missing amount'.format(line))
            num = tokens.popleft().lower()
            if num == 'all':
                num = OrdersParser.AMT_ALL
            else:
                num = OrdersParser._value(num)
            if not num:
                raise SyntaxError('{}: missing amount'.format(line))
            if not tokens:
                raise SyntaxError('{}: missing item'.format(line))
            self._consumer.order_buy(num=num, item=tokens.popleft().lower(),
                                     permanent=permanent, comment=comment)
            
        elif order == 'cast':
            if not tokens:
                raise SyntaxError('{}: missing skill'.format(line))
            skill = tokens.popleft().lower()
            params = [p.lower() for p in tokens]
            self._consumer.order_cast(skill=skill, params=params,
                                      permanent=permanent, comment=comment)
        
        elif order == 'claim':
            if not tokens:
                raise SyntaxError('{}: missing amount'.format(line))
            value = OrdersParser._value(tokens.popleft())
            if not value:
                raise SyntaxError('{}: missing amount'.format(line))
            self._consumer.order_claim(num=value, permanent=permanent,
                                       comment=comment)
        
        elif order == 'combat':
            if not tokens:
                combat = OrdersParser.IT_NONE
            else:
                combat = tokens.popleft().lower()
            self._consumer.order_combat(skill=combat, permanent=permanent,
                                        comment=comment)
        
        elif order == 'consume':
            if not tokens:
                consuming = 'none'
            else:
                consuming = tokens.popleft().lower()
                if consuming not in ('unit', 'faction', 'none'):
                    raise SyntaxError('{}: invalid value'.format(line))
            self._consumer.order_consume(consuming=consuming,
                                         permanent=permanent, comment=comment)
        
        elif order == 'declare':
            if not tokens:
                raise SyntaxError('{}: missing faction'.format(line))
            fac = tokens.popleft().lower()
            if fac != 'default':
                fac = OrdersParser._value(fac)
            if not fac:
                raise SyntaxError('{}: missing faction'.format(line))
            if not tokens:
                self._consumer.order_declare(faction=fac, permanent=permanent,
                                             comment=comment)
            else:
                attitude = tokens.popleft().lower()
                if attitude in ('hostile', 'unfriendly', 'neutral',
                                'friendly', 'ally'):
                    self._consumer.order_declare(faction=fac,
                                                 attitude=attitude,
                                                 permanent=permanent,
                                                 comment=comment)
                else:
                    raise SyntaxError('{}: invalid attitude'.format(line))
        
        elif order == 'describe':
            if tokens:
                target = tokens.popleft().lower()
            else:
                raise SyntaxError('{}: missing target'.format(line))
            if tokens:
                description = tokens.popleft()
            else:
                description = None
            if target == 'unit':
                self._consumer.order_describe(unit=description,
                                              permanent=permanent,
                                              comment=comment)
            elif target in ('ship', 'building', 'object', 'structure'):
                self._consumer.order_describe(structure=description,
                                              permanent=permanent,
                                              comment=comment)
            else:
                raise SyntaxError('{}: invalid target'.format(line))
        
        elif order == 'destroy':
            self._consumer.order_destroy(permanent=permanent, comment=comment)
        
        elif order == 'enter':
            if tokens:
                structure = OrdersParser._value(tokens.popleft())
                if dir:
                    self._consumer.order_enter(structure=structure,
                                               permanent=permanent,
                                               comment=comment)
                else:
                    raise SyntaxError('{}: invalid structure'.format(line))
            else:
                raise SyntaxError('{}: missing structure'.format(line))
            
        elif order == 'entertain':
            self._consumer.order_entertain(permanent=permanent, comment=comment)
        
        elif order == 'evict':
            targets = []
            try:
                while tokens:
                    targets.append(OrdersParser._parse_unit(tokens))
            except SyntaxError as e:
                self._consumer.order_evict(targets=targets,
                                           permanent=permanent,
                                           comment=comment)
                raise SyntaxError('{}: {}'.format(line, e))
            else:
                self._consumer.order_evict(targets=targets,
                                           permanent=permanent,
                                           comment=comment)
        
        elif order == 'exchange':
            try:
                target = OrdersParser._parse_unit(tokens, allow_any=True)
            except SyntaxError as e:
                raise SyntaxError('{}: {}'.format(line, e))
            if not tokens:
                raise SyntaxError('{}: missing given amount'.format(line))
            amtGive = OrdersParser._value(tokens.popleft())
            if not tokens:
                raise SyntaxError('{}: missing given item'.format(line))
            itemGive = tokens.popleft().lower()
            if not tokens:
                raise SyntaxError('{}: missing expected amount'.format(line))
            amtExpected = OrdersParser._value(tokens.popleft())
            if not tokens:
                raise SyntaxError('{}: missing expected item'.format(line))
            itemExpected = tokens.popleft().lower()
            self._consumer.order_exchange(
                    target=target, give={'amt': amtGive, 'item': itemGive},
                    expected={'amt': amtExpected, 'item': itemExpected},
                    permanent=permanent, comment=comment)
        
        elif order == 'faction':
            if not tokens:
                raise SyntaxError('{}: missing faction type'.format(line))
            ftype = {}
            while tokens:
                t = tokens.popleft().lower()
                if not tokens:
                    raise SyntaxError('{}: invalid value'.format(line))
                ftype[t] = OrdersParser._value(tokens.popleft())
            self._consumer.order_faction(permanent=permanent, comment=comment,
                                         **ftype)
        
        elif order == 'find':
            if not tokens:
                raise SyntaxError('{}: missing faction'.format(line))
            fac = tokens.popleft().lower()
            if fac != 'all':
                fac = OrdersParser._value(fac)
            if not fac:
                raise SyntaxError('{}: invalid faction'.format(line))
            self._consumer.order_find(permanent=permanent, comment=comment,
                                      faction=fac)
        
        elif order == 'forget':
            if not tokens:
                raise SyntaxError('{}: missing skill'.format(line))
            self._consumer.order_forget(permanent=permanent, comment=comment,
                                        skill=tokens.popleft().lower())
        
        elif order == 'withdraw':
            if not tokens:
                raise SyntaxError('{}: missing amount'.format(line))
            tok = tokens.popleft().lower()
            amt = OrdersParser._value(tok)
            if amt < 1:
                amt = 1
                item = tok
            elif tokens:
                item = tokens.popleft().lower()
            else:
                raise SyntaxError('{}: missing item'.format(line))
            self._consumer.order_withdraw(permanent=permanent, comment=comment,
                                          amt=amt, item=item)
        
        elif order == 'give':
            try:
                target = OrdersParser._parse_unit(tokens)
            except SyntaxError as e:
                raise SyntaxError('{}: {}'.format(line, e))
            if not tokens:
                raise SyntaxError('{}: missing amount'.format(line))
            amt = tokens.popleft().lower()
            if amt == 'unit':
                self._consumer.order_give(permanent=permanent, comment=comment,
                                          target=target, give=amt)
            else:
                if amt != 'all':
                    amt = OrdersParser._value(amt)
                    if not amt:
                        raise SyntaxError('{}: invalid amount'.format(line))
                try:
                    item = tokens.popleft().lower()
                    if item == 'unfinished':
                        unfinished = True
                        item = tokens.popleft().lower()
                    else:
                        unfinished = False
                except:
                    raise SyntaxError('{}: missing item'.format(line))
                
                if tokens and tokens[0].lower() == 'except':
                    tok = tokens.popleft().lower()
                    if amt != 'all':
                        raise SyntaxError(
                                '{}: except only valid with all'. format(line))
                    if not tokens:
                        raise SyntaxError(
                                '{}: missing except value'.format(line))
                    excpt = OrdersParser._value(tokens.popleft())
                    if not excpt:
                        raise SyntaxError(
                                '{}: invalid except value'.format(line))
                    self._consumer.order_give(permanent=permanent,
                                              comment=comment,
                                              target=target,
                                              give={'amt': amt, 'item': item,
                                                    'unfinished': unfinished,
                                                    'excpt': excpt})
                else:
                    self._consumer.order_give(permanent=permanent,
                                              comment=comment,
                                              target=target,
                                              give={'amt': amt, 'item': item,
                                                    'unfinished': unfinished})
        
        elif order == 'guard':
            if not tokens:
                raise SyntaxError('{}: invalid value'.format(line))
            try:
                guard = OrdersParser._parse_TF(tokens.popleft())
            except SyntaxError as e:
                raise SyntaxError('{}: {}'.format(line, e))
            self._consumer.order_guard(flag=guard, permanent=permanent,
                                       comment=comment)
        
        elif order == 'hold':
            if not tokens:
                raise SyntaxError('{}: invalid value'.format(line))
            try:
                hold = OrdersParser._parse_TF(tokens.popleft())
            except SyntaxError as e:
                raise SyntaxError('{}: {}'.format(line, e))
            self._consumer.order_hold(flag=hold, permanent=permanent,
                                      comment=comment)
        
        elif order == 'join':
            try:
                target = OrdersParser._parse_unit(tokens)
            except SyntaxError as e:
                raise SyntaxError('{}: {}'.format(line, e))
            if tokens:
                tok = tokens.popleft().lower()
                if tok == 'nooverload':
                    self._consumer.order_join(target=target, nooverload=True,
                                              permanent=permanent,
                                              comment=comment)
                elif tok == 'merge':
                    self._consumer.order_join(target=target, merge=True,
                                              permanent=permanent,
                                              comment=comment)
                else:
                    self._consumer.order_join(target=target,
                                              permanent=permanent,
                                              comment=comment)
            else:
                self._consumer.order_join(target=target,
                                          permanent=permanent,
                                          comment=comment)
        
        elif order == 'leave':
            self._consumer.order_leave(permanent=permanent, comment=comment)
        
        elif order == 'move':
            try:
                dirs = [OrdersParser._parse_dir(d.lower()) for d in tokens]
            except SyntaxError as e:
                raise SyntaxError('{}: {}'.format(line, e))
            else:
                self._consumer.order_move(dirs=dirs, permanent=permanent,
                                          comment=comment)
        
        elif order == 'name':
            if len(tokens) < 2:
                raise SyntaxError('{}: missing name'.format(line))
            what, name = tokens.popleft().lower(), tokens.popleft()
            if what == 'faction':
                self._consumer.order_name(permanent=permanent, comment=comment,
                                          faction=name)
            elif what == 'unit':
                self._consumer.order_name(permanent=permanent, comment=comment,
                                          unit=name)
            elif what in ('building', 'ship', 'object', 'structure'):
                self._consumer.order_name(permanent=permanent, comment=comment,
                                          structure=name)
            elif what in ('village', 'town', 'city') and \
                 OrdersParser._get_legal(name):
                self._consumer.order_name(permanent=permanent, comment=comment,
                                          city=OrdersParser._get_legal(name))
            else:
                raise SyntaxError('{}: invalid argument'.format(line))
        
        elif order == 'noaid':
            if not tokens:
                raise SyntaxError('{}: invalid value'.format(line))
            try:
                noaid = OrdersParser._parse_TF(tokens.popleft())
            except SyntaxError as e:
                raise SyntaxError('{}: {}'.format(line, e))
            self._consumer.order_noaid(flag=noaid, permanent=permanent,
                                       comment=comment)
        
        elif order == 'nocross':
            if not tokens:
                raise SyntaxError('{}: invalid value'.format(line))
            try:
                nocross = OrdersParser._parse_TF(tokens.popleft())
            except SyntaxError as e:
                raise SyntaxError('{}: {}'.format(line, e))
            self._consumer.order_nocross(flag=nocross, permanent=permanent,
                                         comment=comment)
        
        elif order == 'nospoils':
            if not tokens:
                raise SyntaxError('{}: invalid value'.format(line))
            try:
                spoils_none = OrdersParser._parse_TF(tokens.popleft())
            except SyntaxError as e:
                raise SyntaxError('{}: {}'.format(line, e))
            if spoils_none:
                self._consumer.order_spoils(spoils='none', permanent=permanent,
                                            comment=comment)
            else:
                self._consumer.order_spoils(spoils='all', permanent=permanent,
                                            comment=comment)
            raise DeprecationWarning(
                    '{}: deprecated. Use SPOILS instead'.format(line))
        
        elif order == 'option':
            if not tokens:
                raise SyntaxError('{}: missing option'.format(line))
            option = tokens.popleft().lower()
            if option == 'times':
                self._consumer.order_option(times=True, permanent=permanent,
                                            comment=comment)
            elif option == 'notimes':
                self._consumer.order_option(times=False, permanent=permanent,
                                            comment=comment)
            elif option == 'showattitudes':
                self._consumer.order_option(showunitattitudes=True,
                                            permanent=permanent,
                                            comment=comment)
            elif option == 'dontshowattitudes':
                self._consumer.order_option(showunitattitudes=False,
                                            permanent=permanent,
                                            comment=comment)
            elif option == 'template':
                if not tokens:
                    raise SyntaxError('{}: missing template type'.format(line))
                temformat = tokens.popleft().lower()
                if temformat in ('off', 'short', 'long', 'map'):
                    self._consumer.order_option(temformat=temformat,
                                                permanent=permanent,
                                                comment=comment)
                else:
                    raise SyntaxError('{}: invalid template type'.format(line))
            else:
                raise SyntaxError('{}: invalid option'.format(line))
        
        elif order == 'password':
            if not tokens:
                self._consumer.order_password(password='none',
                                              permanent=permanent,
                                              comment=comment)
            else:
                self._consumer.order_password(password=tokens.popleft(),
                                              permanent=permanent,
                                              comment=comment)
        
        elif order == 'pillage':
            self._consumer.order_pillage(permanent=permanent, comment=comment)
        
        elif order == 'prepare':
            if not tokens:
                self._consumer.order_prepare(item=None,
                                             permanent=permanent,
                                             comment=comment)
            else:
                self._consumer.order_prepare(item=tokens.popleft().lower(),
                                             permanent=permanent,
                                             comment=comment)
        
        elif order == 'weapon':
            self._consumer.order_weapon(permanent=permanent, comment=comment,
                                        items=[w.lower() for w in tokens])
        
        elif order == 'armor':
            self._consumer.order_armor(permanent=permanent, comment=comment,
                                       items=[w.lower() for w in tokens])
        
        elif order == 'produce':
            if not tokens:
                raise SyntaxError('{}: missing item'.format(line))
            item = tokens.popleft().lower()
            if OrdersParser._value(item):
                if not tokens:
                    raise SyntaxError('{}: missing item'.format(line))
                self._consumer.order_produce(target=OrdersParser._value(item),
                                             item=tokens.popleft().lower(),
                                             permanent=permanent,
                                             comment=comment)
            else:
                self._consumer.order_produce(item=item,
                                             permanent=permanent,
                                             comment=comment)
        
        elif order == 'promote':
            try:
                unit = OrdersParser._parse_unit(tokens)
            except SyntaxError as e:
                raise SyntaxError('{}: {}'.format(line, e))
            else:
                self._consumer.order_promote(unit=unit, permanent=permanent,
                                             comment=comment)
        
        elif order == 'quit':
            if not tokens:
                self._consumer.order_quit(permanent=permanent, comment=comment)
            else:
                self._consumer.order_quit(password=tokens.popleft(),
                                          permanent=permanent, comment=comment)
        
        elif order == 'restart':
            if not tokens:
                self._consumer.order_restart(permanent=permanent,
                                             comment=comment)
            else:
                self._consumer.order_restart(password=tokens.popleft(),
                                             permanent=permanent,
                                             comment=comment)
        
        elif order == 'reveal':
            if not tokens:
                self._consumer.order_reveal(reveal=None, permanent=permanent,
                                            comment=comment)
            else:
                tok = tokens.popleft().lower()
                if tok == 'none':
                    self._consumer.order_reveal(reveal=None, comment=comment,
                                                permanent=permanent)
                elif tok in ('unit', 'faction'):
                    self._consumer.order_reveal(reveal=tok, comment=comment,
                                                permanent=permanent)
                else:
                    raise SyntaxError('{}: invalid value'.format(line))
        
        elif order == 'sail':
            try:
                dirs = [OrdersParser._parse_dir(d.lower(), allow_enter=False) \
                        for d in tokens]
            except SyntaxError as e:
                raise SyntaxError('{}: {}'.format(line, e))
            else:
                self._consumer.order_sail(dirs=dirs, permanent=permanent,
                                          comment=comment)
                    
        elif order == 'sell':
            if not tokens:
                raise SyntaxError('{}: missing amount'.format(line))
            num = tokens.popleft().lower()
            if num == 'all':
                num = OrdersParser.AMT_ALL
            else:
                num = OrdersParser._value(num)
            if not num:
                raise SyntaxError('{}: missing amount'.format(line))
            if not tokens:
                raise SyntaxError('{}: missing item'.format(line))
            self._consumer.order_sell(num=num, item=tokens.popleft().lower(),
                                      permanent=permanent, comment=comment)
        
        elif order == 'share':
            if not tokens:
                raise SyntaxError('{}: invalid value'.format(line))
            try:
                share = OrdersParser._parse_TF(tokens.popleft())
            except SyntaxError as e:
                raise SyntaxError('{}: {}'.format(line, e))
            self._consumer.order_share(flag=share, permanent=permanent,
                                       comment=comment)
        
        elif order == 'show':
            try:
                what, item = tokens.popleft().lower(), tokens.popleft().lower()
            except IndexError:
                raise SyntaxError('{}: missing target'.format(line))
            if what == 'skill':
                self._consumer.order_show(permanent=permanent, comment=comment,
                                          skill=item)
            elif what == 'item':
                self._consumer.order_show(permanent=permanent, comment=comment,
                                          item=item)
            elif what == 'object':
                self._consumer.order_show(permanent=permanent, comment=comment,
                                          structure=item)
            else:
                raise SyntaxError('{}: invalid target'.format(line))
        
        elif order == 'spoils':
            if not tokens:
                tok = 'all'
            else:
                tok = tokens.popleft().lower()
            if tok in ('none', 'walk', 'fly', 'swim', 'sail', 'all'):
                self._consumer.order_spoils(spoils=tok, permanent=permanent,
                                            comment=comment)
            else:
                raise SyntaxError('{}: invalid option'.format(line))
        
        elif order == 'steal':
            try:
                unit = OrdersParser._parse_unit(tokens)
            except SyntaxError as e:
                raise SyntaxError('{}: {}'.format(line, e))
            if not tokens:
                raise SyntaxError('{}: missing item'.format(line))
            else:
                item = tokens.popleft().lower()
                self._consumer.order_steal(target=unit, item=item,
                                           permanent=permanent, comment=comment)
        
        elif order == 'study':
            if not tokens:
                raise SyntaxError('{}: missing skill'.format(line))
            sk = tokens.popleft().lower()
            if tokens:
                self._consumer.order_study(
                        skill=sk, level=OrdersParser._value(tokens.popleft()),
                        permanent=permanent, comment=comment)
            else:
                self._consumer.order_study(skill=sk, permanent=permanent,
                                           comment=comment)
        
        elif order == 'take':
            if not tokens or tokens.popleft().lower() != 'from':
                raise SyntaxError('{}: missing from'.format(line))
            if not tokens:
                raise SyntaxError('{}: missing unit'.format(line))
            unit = OrdersParser._value(tokens.popleft())
            if not unit:
                raise SyntaxError('{}: invalid unit'.format(line))
            target = {'unitnum': unit}
            if not tokens:
                raise SyntaxError('{}: missing amount'.format(line))
            amt = tokens.popleft().lower()
            if amt != 'all':
                amt = OrdersParser._value(amt)
                if not amt:
                    raise SyntaxError('{}: invalid amount'.format(line))
            try:
                item = tokens.popleft().lower()
                if item == 'unfinished':
                    unfinished = True
                    item = tokens.popleft().lower()
                else:
                    unfinished = False
            except:
                raise SyntaxError('{}: missing item'.format(line))
            
            if tokens and tokens[0].lower() == 'except':
                tok = tokens.popleft().lower()
                if amt != 'all':
                    raise SyntaxError(
                            '{}: except only valid with all'. format(line))
                if not tokens:
                    raise SyntaxError(
                            '{}: missing except value'.format(line))
                excpt = OrdersParser._value(tokens.popleft())
                if not excpt:
                    raise SyntaxError(
                            '{}: invalid except value'.format(line))
                self._consumer.order_takefrom(permanent=permanent,
                                              comment=comment,
                                              target=target,
                                              give={'amt': amt, 'item': item,
                                                    'unfinished': unfinished,
                                                    'excpt': excpt})
            else:
                self._consumer.order_takefrom(permanent=permanent,
                                              comment=comment,
                                              target=target,
                                              give={'amt': amt, 'item': item,
                                                    'unfinished': unfinished})
        
        elif order == 'tax':
            self._consumer.order_tax(permanent=permanent, comment=comment)
        
        elif order == 'teach':
            if not tokens:
                raise SyntaxError('{}: missing target'.format(line))
            targets = []
            try:
                while tokens:
                    targets.append(OrdersParser._parse_unit(tokens))
            except SyntaxError as e:
                self._consumer.order_teach(targets=targets,
                                           permanent=permanent,
                                           comment=comment)
                raise SyntaxError('{}: {}'.format(line, e))
            else:
                self._consumer.order_teach(targets=targets,
                                           permanent=permanent,
                                           comment=comment)
        
        elif order == 'work':
            self._consumer.order_work(permanent=permanent, comment=comment)
        
        elif order == 'transport':
            try:
                target = OrdersParser._parse_unit(tokens)
            except SyntaxError as e:
                raise SyntaxError('{}: {}'.format(line, e))
            if not tokens:
                raise SyntaxError('{}: missing amount'.format(line))
            amt = tokens.popleft().lower()
            if amt != 'all':
                amt = OrdersParser._value(amt)
                if not amt:
                    raise SyntaxError('{}: invalid amount'.format(line))
            try:
                item = tokens.popleft().lower()
                if item == 'unfinished':
                    unfinished = True
                    item = tokens.popleft().lower()
                else:
                    unfinished = False
            except:
                raise SyntaxError('{}: missing item'.format(line))

            if tokens and tokens[0].lower() == 'except':
                tok = tokens.popleft().lower()
                if amt != 'all':
                    raise SyntaxError(
                            '{}: except only valid with all'. format(line))
                if not tokens:
                    raise SyntaxError(
                            '{}: missing except value'.format(line))
                excpt = OrdersParser._value(tokens.popleft())
                if not excpt:
                    raise SyntaxError(
                            '{}: invalid except value'.format(line))
                self._consumer.order_transport(permanent=permanent,
                                               comment=comment,
                                               target=target,
                                               give={'amt': amt, 'item': item,
                                                     'unfinished': unfinished,
                                                     'excpt': excpt})
            else:
                self._consumer.order_transport(permanent=permanent,
                                               comment=comment,
                                               target=target,
                                               give={'amt': amt, 'item': item,
                                                     'unfinished': unfinished})
        
        elif order == 'distribute':
            try:
                target = OrdersParser._parse_unit(tokens)
            except SyntaxError as e:
                raise SyntaxError('{}: {}'.format(line, e))
            if not tokens:
                raise SyntaxError('{}: missing amount'.format(line))
            amt = tokens.popleft().lower()
            if amt != 'all':
                amt = OrdersParser._value(amt)
                if not amt:
                    raise SyntaxError('{}: invalid amount'.format(line))
            try:
                item = tokens.popleft().lower()
                if item == 'unfinished':
                    unfinished = True
                    item = tokens.popleft().lower()
                else:
                    unfinished = False
            except:
                raise SyntaxError('{}: missing item'.format(line))
            
            if tokens and tokens[0].lower() == 'except':
                tok = tokens.popleft().lower()
                if amt != 'all':
                    raise SyntaxError(
                            '{}: except only valid with all'. format(line))
                if not tokens:
                    raise SyntaxError(
                            '{}: missing except value'.format(line))
                excpt = OrdersParser._value(tokens.popleft())
                if not excpt:
                    raise SyntaxError(
                            '{}: invalid except value'.format(line))
                self._consumer.order_distribute(permanent=permanent,
                                                comment=comment,
                                                target=target,
                                                give={'amt': amt, 'item': item,
                                                      'unfinished': unfinished,
                                                      'excpt': excpt})
            else:
                self._consumer.order_distribute(permanent=permanent,
                                                comment=comment,
                                                target=target,
                                                give={'amt': amt, 'item': item,
                                                      'unfinished': unfinished})

    @staticmethod
    def tokenize(line):
        """Tokenize a line
        
        Splits a line into its tokens. In Atlantis tokens are defined
        by:
        - Double quotes: everything included between a pair of double
        quotes is a token, no matter which characters are in it.
        - Comments: comments is anything after a semi-colon ;. Comments
        suffer no longer tokenization, they're a single token
        - Permanent mark: the at sign @ as the first not blank
        is interpreted as a permanent mark, and anything following
        it will be included in next turn orders template.
        - Spaces: tokens are separated by spaces.
        
        Tokenize returns a tuple with the following elements: list of
        tokens, permanent flag (True or False), comment string.
        
        Parameters:
        line  The line to be tokenized
        
        Returns:
        A three elements tuple with the list of tokens, the permanent
        flag and the commend string
        
        Raises:
        SyntaxError  If an error is found (like unmatched quotes)
        
        """
        line = line.strip()
        tokens = deque()
        permanent = line.startswith('@')
        if permanent:
            line = line[1:]
        while line:
            token, line, comment = OrdersParser._get_token(line)
            if comment:
                return (tokens, permanent, token)
            else:
                tokens.append(token)
            
        return (tokens, permanent, None)
    
    @staticmethod
    def _get_token(line):
        """Get next token of a line
        
        Reads line and get its next token and its remaining part as a
        tuple.
        
        Parameter:
        line  Line string where the token is to be read
        
        Returns:
        A three elements tuple with next token, remaining part of the
        line and True if the token it's a comment, False otherwise
        
        Raises:
        SyntaxError  If an error is found (like unmatched quotes)
        
        """
        line = line.strip()
        if line.startswith('"'):
            result = re.match(r'"(?P<token>.+?)"(?P<remaining>.*)', line)
            if result:
                return (result.group('token'), result.group('remaining'), False)
            else:
                raise SyntaxError('Unmatched quotes')
        elif line.startswith(';'):
            return (line[1:], None, True)
        else:
            result = re.match(r'(?P<token>[^\s;]+)(:?(?P<remaining>[\s;].*))?',
                              line)
            return (result.group('token'), result.group('remaining'), False)
        
    @staticmethod
    def _value(token):
        """Returns the positive integer value from the token
        
        This function works as value function in Atlantis code. Chars
        others than 0-9 are simply ignored.
        
        Parameter:
        token  String which needs to be converted into number
        
        Return:
        Integer value of the token string
        
        """
        result = re.match(r'\d*', '0' + token)
        return int(result.group(0))
    
    @staticmethod
    def _parse_dir(token, allow_enter=True):
        """Parse a direction string
        
        This function parse a direction string, returning its short
        value (ie, N, S, SE, instead of north, south, southeast).
        
        It raises SyntaxError if direction is not valid.
        
        Parameter:
        token        String which need be parsed as a string
        allow_enter  If True (default) entering and leaving structures
                     are valid movements
        
        Return:
        A string with the direction, or the number of object to enter
        
        Raises:
        SyntaxError if direction is not valid
        
        """
        for k, v in directions.items():
            if not allow_enter and k in ('in', 'out'):
                continue
            if token.lower() in (k, v):
                return k
        else:
            if not allow_enter:
                raise SyntaxError('invalid direction')
            result = OrdersParser._value(token)
            if result:
                return result
            else:
                raise SyntaxError('invalid direction')
    
    @staticmethod
    def _parse_unit(tokens, allow_any=False):
        """Parse a target unit string
        
        This method parses a unit string as Atlantis parser does. It
        returns a dictionary for the unit id with the following keys:
        unitnum  Number of the unit (in case the unit exists we'll use
                 its number)
        alias    Alias of the unit (in case the unit is just created)
        faction  Number of the faction, to be used together with the
                 alias when we're referring to a just created unit
                 from another faction
        
        There's a special case when the string used for the unit is
        '0'. In this case unitnumber is set to _ANY.
        
        So unit can be referred by:
        <number>
            As in give 127 100 silv. Return unitnumber set to number
            of the unit
        faction <facnum> new <alias>
            As in give faction 12 new 3 100 silv. Return faction and
            alias numbers
        new <alias>
            As in give new 3 100 silv. Return alias number
        0
            The special case mentioned above. unitnum is returned as
            ANY
            
        If there's a parser error a SyntaxError exception is raised.
        
        Parameters:
        tokens     A list of string tokens
        allow_any  If True ANY value is allowed, otherwise it raises
                   a SyntaxError exception
        
        Return:
        A dictionary with unitnum, alias and faction keys
        
        Raises:
        SyntaxError if unit specification is not correctly built
        
        """
        if not tokens:
            raise SyntaxError('missing unit')
        tok = tokens.popleft().lower()
        if tok == '0':
            if allow_any:
                return {'unitnum': OrdersParser.UNIT_ANY}
            else:
                raise SyntaxError('malformed unit')
        elif tok == 'faction':
            try:
                faction, newstr, alias = \
                        OrdersParser._value(tokens.popleft()), \
                        tokens.popleft().lower(), \
                        OrdersParser._value(tokens.popleft())
            except IndexError:
                raise SyntaxError('malformed unit')
            if not faction or not alias or newstr != 'new':
                raise SyntaxError('malformed unit')
            return {'alias': alias, 'faction': faction}
        elif tok == 'new':
            try:
                alias = OrdersParser._value(tokens.popleft())
            except IndexError:
                raise SyntaxError('malformed unit')
            if not alias:
                raise SyntaxError('malformed unit')
            return {'alias': alias}
        else:
            unitnum = OrdersParser._value(tok)
            if not unitnum:
                raise SyntaxError('malformed unit')
            return {'unitnum': unitnum}
    
    @staticmethod
    def _parse_TF(token):
        """Parse a true or false flag
        
        Translate the true or false string to a Boolean value. True
        values are true, t, on, yes and 1. False values are false, f,
        off, no and 0.
        
        Raises a SyntaxError exception if none of this strings are
        found.
        
        Parameter:
        token  String to be translated
        
        Return:
        True or False depending on the string
        
        Raises:
        SyntaxError if the string is not a true/false string
        
        """
        if token and token.lower() in ('true', 't', 'on', 'yes', '1'):
            return True
        elif token and token.lower() in ('false', 'f', 'off', 'no', '0'):
            return False
        else:
            raise SyntaxError('invalid value')
    
    @staticmethod
    def _get_legal(token):
        """Get rid of invalid characters in the token
        
        Valid characters are
        a-z A-Z 0-9 ! [ ] , . <space> { } @ # $ % ^ & * - _ + = ; : <
        > ? / ~ ' \ `
        
        Parameter:
        token  String to be cleaned up from invalid characters
        
        Return:
        Cleaned up string 
        
        """
        valid = re.split(r'[^]a-zA-Z0-0![,. {}@#$%^&*-_+=;:<>?/~\'\\`]', token)
        return ''.join(valid).strip()
    