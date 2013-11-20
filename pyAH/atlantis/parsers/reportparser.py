"""This module implements all classes needed to parse report files.

Main class defined by this module is :class:`ReportParser`, which will
parse report lines and will call a :class:`ReportConsumer` with parser
data.

Also the above mentioned :class:`ReportConsumer` interface is declared.
Classes willing to consume data parser by :class:`ReportParser`
will have to implement :class:`ReportConsumer` interface.

In addition a helper :class:`ReportReader` is defined. As report lines
are wrapped at 70 chars length this class is in charge of reading the
report file and unwrapping the lines.

Public attributes in :mod:`atlantis.parsers.reportparser` module:

.. attribute:: TAB_SPACES

   Number of spaces used for tabbing report lines.

.. attribute:: TAB

   Tab string. It's made of :obj:`!TAB_SPACES` spaces.

"""

from atlantis.gamedata.item import ItemRef, ItemAmount, ItemMarket

import re

# Wrapping definitions
TAB_SPACES = 2

TAB = ' ' * TAB_SPACES

class ReportReader:
    """Class used to read report lines, unwrapping them.
    
    This class is used as a wrapper to read lines from a report file.
    These report files have their lines wrapped at 70 chars length,
    and what this class does is unwrapping them so its user will get
    complete logical lines, not the physical ones saved in the file.
    
    ReportReader implements a :meth:`readline` public method, that
    returns the next unwrapped line from the file being read. It also
    implements the :meth:`__iter__` magic method, so the complete file
    can be read iterating the object as::
    
        with open('hello.txt') as f:
            reader = ReportReader(f)
            for line in reader:
                print(line)
            
    """
    _file = None
    _tab = ''
    _buffered_line = None
    _re_line = re.compile('(?P<tab> *)(?P<line>.*)$')
    _re_exits = re.compile('^Exits:$')
    _re_separator = re.compile('^-+$')
    _re_unit = re.compile('(?P<attitude>[-*=%!]) (?P<unit>.*)$')
    _re_object = re.compile(r'\+ (?P<object>.*)$')
    _re_orders = re.compile(r'^Orders Template \((?:Short|Long|Map) Format\):$')
    _in_report = True

    def __init__(self, f):
        """Creates a :class:`ReportReader` on a file object.
        
        :param f: file object to be read.
        
        """
        self._file = f
        self._tab = ''
        self._buffered_line = None
        self._in_report = True

    def __iter__(self):
        """Return an iterator on :class:`ReportReader` instance.
        
        This iterator returns all lines in the file, unwrapped,
        allowing the use of :class:`ReportReader` class as::
    
            with open('hello.txt') as f:
                reader = ReportReader(f)
                for line in reader:
                    print(line)
        
        :return: an iterator on wrapped file lines.
        
        """ 
        self._in_report = True
        l = self.readline()
        while l:
            yield l
            l = self.readline()
        else:
            yield l

    def readline(self):
        """Read next line from the file.

        When reading next line from the file :meth:`!readline` unwraps
        it, joining all wrapped parts back to the original one.
        
        :return: next line, unwrapped.
    
        """
        # Uses previous read line if it was not joined
        if self._buffered_line:
            line = self._buffered_line
        else:
            line = self._file.readline()
      
        self._buffered_line = None
    
        if self._in_report and ReportReader._re_orders.match(line):
            self._in_report = False
            
        if not self._in_report or not line:
            return line

        res = ReportReader._re_line.match(line)
        self._tab = res.group('tab')
        inline = res.group('line')

        # Separator
        #   ---------------------
        # and exits lines
        #   Exits:
        # cause tabbing of next lines, but no wrap exists
        if ReportReader._re_separator.match(line) or \
                ReportReader._re_exits.match(line):
            return line

        # Look for wrapped lines and glue them together
        self._buffered_line = self._file.readline()
        res = ReportReader._re_line.match(self._buffered_line)
        while self._buffered_line and res.group('tab') == self._tab + TAB:
            # Units inside objects are also tabbed, but not joined
            if ReportReader._re_object.match(inline) and \
                    ReportReader._re_unit.match(res.group('line')):
                break

            # Join wrapped line...
            line = line.rstrip() + ' ' + res.group('line') + '\n'
            # ... and read a new one
            self._buffered_line = self._file.readline()
            res = ReportReader._re_line.match(self._buffered_line)

        # Return line
        return line


class ReportConsumer:
    """Virtual class for :class:`ReportParser` consumer.
    
    This is an interface for classes willing to receive data from the
    :class:`ReportParser`. Classes implementing this interface should
    overwrite their public methods.
        
    """
    
    def line(self, line):
        """Handle a new line.
        
        Whenever a line is read, it is sent to the consumer in case
        it wants to use it for the read entity description.
        
        The line is send just before the parsed object is sent to
        the consumer, so it should store it in a temporary buffer,
        and when the parsed entity is received attach the line(s)
        to it as a description.
        
        :param line: read line.
        
        :raise: :class:`NotImplementedError` if not overriden.
            
        """
        raise NotImplementedError('ReportConsumer method must be overriden')
    
    def battle(self, att, tar, reg, ass=False):
        """Handle a battle starting line.
        
        This method signals the starting of a new battle. Previous
        open battle (if any) should be closed, and next battle lines
        assigned to this one.
        
        When a new battle is reported it is given its attacking unit,
        defending unit, location and a flag telling if it's due to
        an failed assassination attempt. Attacking and defending units
        will be the *leading* units of each side and further side
        reports (as healing, loses, etc) will use this unit as target
        although they refer to the entire side.
        
        :param att: The attacking unit, as a dictionary with unit *num*
                    and *name*.
        :param tar: The target (defending) unit, also as a dictionary
                    with unit *num* and *name*.
        :param reg: Location of the battle, as a region dictionary with
                    region *type*, *name*, *xloc*, *yloc* and, if not
                    in surface, *zloc*.
        :param ass: *True* if it was an assassination attempt, *False*
                    otherwise.
        
        """
        print('battle', att, tar, reg, ass)
    
    def battle_side(self, side):
        """Handle a battle side marker
        
        This marker is set just before the units in the given side
        are listed. So the consumer should initialize side data and
        attach following battle units entities to the side.
        
        :meth:`ReportConsumer.battle`
        
        Parameter:
            side
                **attacker** or **defender**.
        
        """
        print('battle_side', side)
        
    def battle_side_unit(self, num, name, faction=None, behind=False,
                           items=None, skills=None):
        """Handle a battle side units
        
        For each side its list of units is given. This unit report is
        not a complete one. Only items, skills and flags relevant for
        battle are reported.
        
        Parameters:
            num
                Num of the unit.
            name
                Name of the unit.
            faction
                Optional. If faction is visible, a dictionary with
                faction *num* and *name*.
            behind
                *True* if unit is behind in battle, *False* otherwise.
            items
                A list of items. For each item a dictionary is given
                with *num*, *abr* and *name* or *names* of the item.
                
                If the item is a monster also *monster* key is
                included, which value is another dictionary with
                *attackLevel*, *defense*, *numAttacks*, *hits* and
                *tactics* stats.
            skills
                A list of skills. For each skill a dictionary is given
                with its *level* and *name*.
        
        """
        print('battle_side_unit', num, name, faction, behind, items,
              skills)

    def battle_round(self, num, unit=None):
        """Handle a battle round marker
        
        This method signals the starting of a round. Every new round
        in the battle it is called.
        
        There're two types of rounds: normal rounds (both sides attack)
        and free rounds (only one side attack). There're two possible
        free rounds: at the beginning of the battle it is granted to
        the side with highest TACT skill, and at the end of the battle
        it is granted to the winner when the loser side breaks and
        routes.
        
        For normal rounds the only parameter is num, which takes the
        value of the round number (from 1 to the end of the battle).
        For free rounds, num takes the value **free**, and an
        additional unit parameter is given.
        
        Parameters:
            num
                **free** for free rounds (either first or last round),
                and round number for normal rounds.
            unit
                when in a free round, leader unit of the side granted
                the free round as a dictionary with *num* and *name*
                values.
        
        """
        print('battle_round', num, unit)
    
    def battle_round_shield(self, unit, shielddesc):
        """Handle a cast shield in battle.
        
        Parameters:
            unit
                Unit casting the shield, as a dictionary with unit
                *num* and *name*.
            shielddesc
                Description of the shield being cast.
        
        """
        print('battle_round_shield', unit, shielddesc)
    
    def battle_round_special(
            self, soldier, spelldesc, spelldesc2=None, tot=0,
            spelltarget=None, deflected=False):
        """Handle a special effect in battle.
        
        When an effect takes place in a battle, its description is
        parsed in several pieces. For example::
        
            Mage (314) strikes fear into enemy mounts, causing 8 mounts
            to panic.
          
        What we get is:
            - ``Mage (314)`` is the *soldier* casting the effect.
            - ``strikes fear into enemy mounts`` is the description of
              the spell (*spelldesc*).
            - ``causing`` is the effect of the spell on the target
              (*spelldesc2*).
            - ``8`` is the number of affected targets (*tot*).
            - ``mounts to panic`` is the string describing the target
              (*spelltarget*).
              
        In addition the spell can be deflected by a shield, and
        *deflected* flag is set to *True*.
        
        Parameters:
            soldier
                Soldier casting the special effect as a dictionary
                with unit *num* and *name*.
            spelldesc
                Description of the spell.
            spelldesc2
                String of the effect of the spell (ie killing).
            tot
                Number of targets affected.
            spelltarget
                String describing the target of the spell.
            deflected
                True if the effect has been deflected by a shield.
        
        """
        print('battle_round_special', soldier, spelldesc, spelldesc2, tot,
              spelltarget, deflected)
    
    def battle_round_regenerate(self, soldier, regenerate, damage,
                                   hits, maxhits):
        """Handle regeneration/damage in battle.
        
        While normal men die in battle with just a hit, larger monsters
        can take more hits before dying. Some of them even regenerate
        from their wounds and can even end a round with higher hit
        points than they started it.
        
        When this happens this method is called.
        
        Parameters:
            soldier
                Soldier regenerating or taking damage, as a dictionary
                with unit *num* and *name*.
            regenerate
                **regenerate** if unit is regenerating, or **take** if
                unit is taking damage.
            damage
                Amount of hit points the unit is being regenerated
                or damaged
            hits
                Hit points of the unit after regeneration/damage.
            maxhits
                Maximum number of hit points of the unit.
        
        """
        print('battle_round_regenerate', soldier, regenerate, damage,
              hits, maxhits)
    
    def battle_loses(self, unit, loses):
        """Handle rount/battle loses.
        
        This function is called at the end of each round with side
        loses of the round, and again at the end of the battle with
        total side casualties of the battle after healing has taken
        place.
        
        Parameters:
            unit
                A dictionary with *num* and *name* of the leading unit.
                of the side
            loses
                Num of casualties of the round/battle.
        
        """
        print('battle_loses', unit, loses)
    
    def battle_end(self, result, unit=None):
        """Handle battle end result.
        
        When one or both units are broken battle ends, and this
        method is called with the result in result parameter:
        
        - **destroyed**, losing side has completely been destroyed
          and battle has ended.
        - **routed**, losing side has been broken and winner side is
          granted a free round of attacks, that follows.
        - **tie**, both sides have been broken at once and no more
          rounds will take place.
        
        When there's a loser side a unit parameter is also provided
        with the loser side leader unit as a dictionary.
        
        Parameters:
            result
                What happened to the loser side. Can be **destroyed**,
                **routed**, or **tie** (no loser, no winner).
            unit
                Only when there's a loser side. Loser side leader
                unit as a dictionary with *num* and *name* of the unit.
        
        """
        print('battle_end', result, unit)
    
    def battle_casualties(self):
        """Handle battle casualties marker.
        
        When battle ends, even the free round after loser side are
        broken, it's time to report casualties and spoils.
        
        This method just signals this point.
        
        """
        print('battle_casualties')
    
    def battle_casualties_heal(self, unit, heal):
        """Handle healing after battle.
        
        This function is called at the end of the battle when the
        winner side does heal. Total casualties are listed after
        healing, so healed units are not counted as battle loses.
        
        Parameters:
            unit
                A dictionary with *num* and *name* of the leading unit
                of the side.
            heal
                Num of casualties healed.
        
        """
        print('battle_casualties_heal', unit, heal)
    
    def battle_casualties_units(self, units):
        """Handle the list of damaged units.
        
        This function is called with a list of damaged units. While
        this function does have no information about which side damaged
        units belong, it's called immediately after battle loses
        handler for their side, so the consumer can easily track it.
        
        Parameters:
            units
                A list of units, being each unit a dictionary with
                *num* of the damaged unit.
        
        """
        print('battle_casualties_units', units)
    
    def battle_spoils(self, items):
        """Handle battle spoils.
        
        Winner side gets spoils from battle.
        
        Parameters:
            items
                List of spoiled items, each item being a dictionary
                with *abr*, *name*/*names* and *amt*.
               
        """
        print('battle_spoils', items)
    
    def battle_raise(self, undead, unit=None):
        """Handle battle raised undead.
        
        This function is called at the very end of the battle. Part
        of the casualties raises again as skeletons and undead, joining
        a wandering undead unit or creating a new one if none exists.
        
        Parameters:
            undead
                List of undead items. Each undead item is a dictionary
                with *abr*, *amt* and *name*/*names*.
            unit
                If the undead join an existing wandering unit this
                parameter will be set with a dictionary with *num* and
                *name* of the unit.
        
        """
        print('battle_raise', undead, unit)
    
    def skill(self, name, abbr, level, descr=None, cost=None, skilldescr=None,
               noexp=False, noteach=False, nostudy=False, slowstudy=False,
               builds=None, production=None, mProduction=None,
               depends=None, discovers=None,
               foundation=False, combat=False, cast=False, apprentice=False,
               specialstr=None, special=None):
        """Handle a skill definition.
        
        This method is called when a skill description is read. Skill
        are very complex entities in Atlantis, with lots of flags and
        specially complex special effects.
        
        Basically a skill is always defined by name, abbr and level.
        As::
        
            combat [COMB] 2: No skill report
        
        There're some basic properties of the skills that are not given
        in every report, but only are reported at the first level, and
        are supposed to be generic data for all levels of the skill. So
        happens with description, study cost, and several flags. This
        will be noted in the description of the parameters.
        
        Basic parameters:
            name
                Skill name.
            abbr
                Skill abbreviature.
            level
                Skill level.
            descr
                Complete skill description. Everything after the colon.
            cost
                *Level 1*. Cost of skill study.
            skilldescr
                *Optional*. A generic skill description. It's
                usually given only for level 1 skill report, but
                sometimes additional descriptions are given at
                further levels when additional abilities are
                granted by the skill.
        
        Flags:
            noexp
                *True* if skill cannot be increased by experience.
            noteach
                *True* if skill cannot be teached.
            nostudy
                *True* if skill cannot be studied.
            slowstudy
                *Level 1*. *True* if skill study is slow.
        
        Production parameters:
            builds
                *Optional*. List of structures that current skill
                level allows to build. Each structure is a dictionary
                with *name*, *cost* and *item*.
                
                *item* value is a list of items that can be used to
                build the structure. Each item in *item* list is a
                dictionary with *abr* and *name* (singular) of the
                item.
                
                **Note that the structure won't need both items,
                but it can use any of them to be built.**
            production
                *Optional*. Normal production granted by the skill
                level. This parameter is a dictionary with *command*,
                that can take the values of **build** for ships and
                **produce** for items; and *items*, that it's a list of
                items that can be produced.
                
                When producing items each element in *items* list is a
                dictionary with its *abr*, *names*, *pOut* (items
                produced per *pMonths* man months) and *pMonths*
                (months needed to produce *pOut* items).
                
                Other optional elements in item dictionary are
                *skillout* (default *False*) that if *True* means that
                production is multiplied per skill level, *orinputs*
                (default *False*) that if *True* means that input items
                can be used alternatively instead of having to use them
                all, and *pInput*, which is a list of input items
                needed for production.
                
                Each item in *pInput* list is a dictionary with *abr*,
                *amt* and *name*/*names* of input item.
                
                When building ships, each element in *items* list is a
                dictionary with *abr*, *names* and *pMonths* (*pOut* is
                not given). *pMonths* is both for time needed to build
                the ship and the amount of items needed.
                
                Optionals elements in item dictionary are, as with
                items, *skillout*, *orinputs* and *pInput*.
            mProduction
                *Optional*. Magical production granted by the skill
                level. This parameter is a dictionary with *command*,
                that it's **cast**, and *items*, that it's a list of
                items that can be produced.

                Each element of *items* list is a dictionary with *abr*
                of the item being produced, its *name* or *names*,
                *mOut* (number of items produced per level multiplied
                by 100, so 20 means 20% chance, 200 means 2 times the
                skill level items), and optionally *mInput*, as a list
                of items needed for production.
                
                Each element of *mInput* is a dictionary with *amt*,
                *abr* and *name*/*names* of needed items.
        
        Advanced items and skills parameters:
            depends
                *Level 1*. *Optional*. List of skills current skills
                depends on. Each skill in the list is given as a
                dictionary with *name*, *abbr* and *level* of the
                prerequisite skill.
            discovers
                *Optional*. List of advanced products than can be
                discovered by this skill. Each item in the list is a
                dictionary with item *names* value.
        
        Magic parameters:
            foundation
                *Level 1*. *True* if skill is a foundational one.
            combat
                *Level 1*. *True* if skill can be used as combat spell.
            cast
                *True* if skill can be cast.
            apprentice
                *Level 1*. *True* if the skill allows the unit to use
                magical items (manipulation skill).
            specialstr
                *Optional*. If special effect is caused, the special
                effect description string.
            special
                *Optional*. Special effect caused by the spell.
                
                This is a complex object passed as a dictionary, with
                the following keys and values, all of them optionals
                but the name:
                    *name*
                        only mandatory key, name of the effect.
                    *level*
                        level of the effect. This is given for items
                        with special effects. For skills, the skill
                        level will be used.
                    *damage*
                        if it's a damage spell, *damage* is set as a
                        list of damages. Each element in *damage* list
                        is a dictionary with
                            *minnum*
                                minimum affected targets.
                            *maxnum*
                                maximum affected targets.
                            *expandLevel*
                                *optional*, if *True*, multiply nums by
                                skill level of the mage.
                            *type*
                                type of attack.
                            *effectstr*
                                *optional*, effect description.
                            *effect*
                                *optional*, parsed effect as a
                                dictionary:
                                    *name*
                                        name of the effect.
                                    *cancelEffect*
                                        *optional*, name of effect
                                        cancelled by this one.
                                If the effect affects target attack and
                                defense stats the following keys are
                                also included in effect:
                                    *oneshot*
                                        *True* if effect is only for
                                        next round, *False* if its for
                                        the entire battle.
                                    *attackVal*
                                        mod on target attack stat.
                                    *defMods*
                                        a list of mods on target
                                        defensive stats. Each element
                                        in the list is a dictionary
                                        with *type*, type of attack and
                                        *val*, defense modifier.
                    *defs*
                        a list of defensive bonuses. Each element in
                        *defs* list is a dictionary with
                            *type*
                                attack type affected.
                            *val*
                                value of defensive bonus.
                            *expandLevel*
                                *optional*, if *True*, multiply *val*
                                by skill level of the mage.
                    *shield*
                        list of attack types shielded as dictionaries
                        with *type* key and value.
                    *nobuilding*
                        if *True* target soldiers don't get
                        benefit of being in a building.
                    *nomonster*
                        if *True* cannot target monsters.
                    *illusion*
                        if *True* can target only illusions.
                    *effectexcept*
                        if *True*, won't affect soldiers affected by
                        effects in *effects* list.
                    *effectif*
                        if *True*, will only affect soldiers affected by
                        effects in *effects* list.
                    *effects*
                        list of effects. Each effect is a dictionary
                        with *name* key and value.
                    *mountexcept*
                        if *True*, won't affect soldiers mounted on
                        *target* mounts.
                    *mountif*
                        if *True*, will only affect soldiers mounted on
                        *target* mounts.
                    *soldierexcept*
                        if *True*, won't affect soldiers of *target*
                        races.
                    *soldierif*
                        if *True*, will only affect soldiers of
                        *target* races.
                    *targets*
                        list of items. Each item is a dictionary with
                        *abr* and *names* of the item.
                    *buildingexcept*
                        if *True*, won't affect soldiers inside
                        *buildings* buildings.
                    *buildingif*
                        if *True*, will only affect soldiers inside
                        *buildings* buildings.
                    *buildings*
                        list of structures. Each structure is a
                        dictionary with *name* key and value.
         
        """
        print('skill', name, abbr, level, descr, cost, skilldescr,
              noexp, noteach, nostudy, slowstudy, builds, production,
              mProduction, depends, discovers, foundation, combat, cast,
              apprentice, specialstr, special)
    
    def item(self, abr, name, descr=None, illusion=False,
              weight=None, hitch=None, walking=None, riding=None,
              swimming=None, flying=None, speed=None,
              max_inventory=None, food=None, withdraw=None,
              cantgive=False, mageonly=False, money=False, resource=False,
              grantSkill=None, wind=None, stealth=None, observation=None,
              mount=None, battle=None, trade=None,
              tool=None, armor=None, weapon=None, monster=None,
              man=None, ship=None):
        """Handle an item definition.
        
        This handler is called when an item description is read. Items
        are very complex objects in Atlantis, and they can be divided
        into two main categories: ships and normal items.
        
        Ships have a diffent behaviour because they are items while
        unfinished, but become structures when finished. In addition
        they're build using the build command, as structures, instead
        of produce.
        
        There're several types of normal items: men and leaders,
        monsters, weapons and armors, tools, raw materials. Items can
        be referred to by using its name (singular, like *horse*),
        names (plural, like *horses*) and abr (four letters
        abbreviature, like *hors*).
        
        Common parameters:
            name
                Name of the item.
            abr
                Abbreviature of the item.
            descr
                Complete description of the item. It's everything after
                name and abbreviature.
            illusion
                *True* if the item is an illusion. Defaults to *False*.
            weight
                Weight of the item.
            hitch
                If the item can be hitched to a mount this parameter
                will be present, as a dictionary with:
                    *item*
                        Mount to be hitched, as a dictionary with *abr*
                        and *name*.
                    *walk*
                        Waling capacity of the item when it is hitched.
            walking
                Walking capacity of the item. Defaults to *None*.
            riding
                Riding capacity of the item. Defaults to *None*.
            swimming
                Swimming capacity of the item. Defaults to *None*.
                Normal ships only define this capacity parameter.
            flying
                Flying capacity of the item. Defaults to *None*. Flying
                ships only define this capacity parameter.
            speed
                Number of movement points available per month. Defaults
                to *None*.
            max_inventory
                If present, maximum number of this item that a unit can
                have.
            food
                If present, the item can be used for maintenance, as
                parameter value in gold.
            withdraw
                If present, the item can be withdrawed using unclaimed
                at the cost of this parameter value.
            cantgive
                If *True* the item cannot be give. Defaults to *False*.
            mageonly
                If *True*, only mages and apprentices can use the item.
                Defaults to *False*.
            money
                If *True*, the item is used as money in the game.
                Defaults to *False*.
            resource
                If *True*, the item is a trade resource. Ie, it's
                produced from the region and not from input items.
                Defaults to *False*.
            grantSkill
                If present the item grants a skill to its user.
                *grantSkill* is defined as a dictionary with the
                following values:
                    *name*
                        Name of the skill being granted by the item.
                    *minGrant*
                        Minimum level of skill granted by the item.
                    *maxGrant*
                        Maximum level of skill granted by the item.
                    *fromSkills*
                        If *minGrant* < *maxGrant*, the actual skill
                        level granted will be the highest of the unit
                        levels on a serie of skills, always between
                        *minGrant* and *maxGrant*.
                        
                        *fromSkills* is then a list of skills, being
                        each skill in the list is a dictionary with a
                        unique key, *name* of the skill.
            wind
                If present the item gives a wind boost to ships as
                defined in a dictionary with the following values:
                    *windBoost*
                        Movement points boosted to the ship.
                    *val*
                        Maximum number of sailors of the boosted ship
                        to get the movement bonus.
            stealth
                If present the item gives a bonus on unit's stealth as
                defined in a dictionary with the following values:
                    *val*
                        Stealth bonus.
                    *perman*
                        If *True*, at least one item per man in the
                        unit is needed to get the bonus. Defaults to
                        *False*.
            observation
                If present the item gives a bonus on unit's observation
                as defined in a dictionary with the following values:
                    *val*
                        Stealth bonus.
                    *perman*
                        An item granting observation grants it even if
                        there aren't an item per man in the unit, but
                        not always repels assassination attemps from
                        units using an stealth item.
                        
                        If this parameter is *True*, at least one item
                        per man in the unit is needed to repel these
                        assassination attempts. Defaults to *False*.
            mount
                If present the item is a mount, with the stats given in
                a dictionary with the following values:
                    *minBonus*
                        Minimum bonus granted by the mount in combat.
                    *maxBonus*
                        Maximum bonus granted by the mount in combat.
                    *skill*
                        Name of the skill used to ride the mount.
                        Defaults to *None*.
                    *unridable*
                        If *True* the mount cannot be riden in combat.
                        Defaults to *False*.
                    *specialstr*
                        If present, description of the special effect
                        caused by the mount.
                    *special*
                        Special effect caused by the mount. Special
                        effect are very complex entities. A detailed
                        description can be found at
                        :meth:`ReportConsumer.skill` documentation.
            battle
                If present the item is a miscellaneous battle item with
                the stats given in a dictionary with the values:
                    *mageonly*
                        If *True*, only mages and apprentices can use
                        the item. Defaults to *False*.
                    *shield*
                        If *True*, the item provides with a shield its
                        wearer. Defaults to *False*.
                    *specialstr*
                        If present, description of the special effect
                        caused by the item.
                    *special*
                        Special effect caused by the item. Special
                        effect are very complex entities. A detailed
                        description can be found at
                        :meth:`ReportConsumer.skill` documentation.
            trade
                If present the item is a trade good. It cannot be
                produced in any way, just bought and sold in markets.
                It is a dictionary with the following stats:
                    *baseprice*
                        Usual price, if there're not better selling
                        than buying prices in the game.
                Or
                    *minbuy*
                        Minimum buy price.
                    *maxbuy*
                        Maximum buy price.
                    *minsell*
                        Minimum sell price.
                    *maxsell*
                        Maximum sell price.
            tool
                If present the item is a tool, boosting production of
                one or more items. Tool parameter is a dictionary with
                an unique key, *items*, which value is a list of items.
                For each element of *items* list a dictionary is given
                with the following values:
                    *abr*
                        Abbreviature of the item which production is
                        boosted.
                    *name*
                        Name of the item wich production is boosted.
                    *val*
                        Boost applied to the item production.
                If production aided is entertainment, no *abr* is given
                and *name* is **entertainment**.
            armor
                If present the item is an armor, protecting its wearer
                from death in a percentage depending of the weapon type
                of the attacker. Armor parameter is a dictionary with
                two values:
                    *useinassassinate*
                        If *True* the armor can be used in
                        assassination attempts. Defaults to *False*.
                    *saves*
                        A list of save percentages depending on weapon
                        type. Each element of this list is a dictionary
                        with *weapClass* and *percent* values.
            weapon
                If present the item is an armor, boosting combat stats
                of its wearer and allowing it to tax a region. Weapon
                parameter is a dictionary with the following values:
                    *attackBonus*
                        Bonus granted on attack. Can be negative.
                    *defenseBonus*
                        Bonus granted on defense. Can be negative.
                    *mountBonus*
                        Bonus granted against mounted oponents. Can be
                        negative. Defaults to *None*.
                    *attackType*
                        Attack type of the weapon.
                    *class*
                        Weapon class of the weapon.
                    *range*
                        Rage of the weapon. Can be *short*, *long* and
                        *ranged*. Defaults to *None*.
                    *skill*
                        If present, a skill is needed to handle this
                        weapon. It's a dictionary with the skill *abbr*
                        and *name*.
                    *nofoot*
                        If *True*, only mounted troops can use this
                        weapon. Defaults to *False*.
                    *nomount*
                        If *True*, only on foot troops can use this
                        weapon. Defaults to *False*.
                    *ridingbonus*
                        If *True*, riding troops will add its riding
                        skill on attack and defense. Defaults to
                        *False*.
                    *ridingbonusdefense*
                        If *True*, riding troops will add its riding
                        skill on defense. Defaults to *False*.
                    *nodefense*
                        If *True*, defenders are treated as if they
                        have an effective combat skill of 0. Defaults
                        to *False*.
                    *noattackerskill*
                        If *True*, attackers do not get skill bonus on
                        defense. Defaults to *False*.
                    *alwaysready*
                        If *True*, attacker will have a chance to
                        attack each round, instead of the usual 50%.
                        Defaults to *False*.
                    *numAttacks*
                        Number of attacks per round granted by the
                        weapon. It is a dictionary with the following
                        values:
                            *attacksSkill*
                                If *True* the weapon grants a number of
                                attacks equal to the skill level of the
                                attacker. Defaults to *False*.
                            *attacksHalfSkill*
                                If *True* the weapon grants a number of
                                attacks equal to half the skill level
                                of the attacker. Defaults to *False*.
                            *atts*
                                If *attacksSkill* or *attacksHalfSkill*
                                are *True*, this parameter is added to
                                the number of attacks granted by the
                                skill. Else, if *atts* > 0 user is
                                granted this number of attacks per
                                round, and if *atts* < 0 user is
                                granted one attack each number of
                                rounds.
            monster
                If present, the item is a monster. It is defined by a
                dictionary with the following parameters:
                    *attackLevel*
                        Attack level of the monster.
                    *defense*
                        Defense of the monster against the attack
                        types. It is a dictionary where keys are attack
                        types and values are resistence against them.
                    *stealth*
                        Stealth score of the monster.
                    *observation*
                        Observation score of the monster.
                    *tactics*
                        Tactics score of the monster.
                    *spoils*
                        Type of items found as spoils in addition to
                        silver. It can be **normal**, **advanced** or
                        **magic**.
                    *specialstr*
                        If present, description of the special effect
                        caused by the monster.
                    *special*
                        Special effect caused by the monster. Special
                        effect are very complex entities. A detailed
                        description can be found at
                        :meth:`ReportConsumer.skill` documentation.
            man
                If present, the item is a man. It is defined by a
                dictionary with the following parameters:
                    *defaultLevel*
                        Maximum level allowed to the man to any skill.
                    *specialLevel*
                        If present, maximum level allowed to the man to
                        skills he can specialize.
                    *skills*
                        List of skills where the man can specialize.
                        Each list element is a dictionary with *name*
                        and *abbr* of the skill.
            ship
                If present, the item is a ship. It is defined by a
                dictionary with the following parameters:
                    *sailors*
                        Number of sailors to sail the ship.
                    *protect*
                        Number of soldiers protected by the ship.
                        Defaults to *None*.
                    *defense*
                        A dictionary where keys are attack types and
                        values are bonuses applied against these attack
                        types. Defaults to *None*.
                    *maxMages*
                        Number of mages allowed to study in the ship
                        beyond 2th level. Defaults to *None*.
                
            
        """
        print('item', abr, name, descr, illusion, weight, hitch, walking,
              riding, swimming, flying, speed, max_inventory, food, withdraw,
              cantgive, mageonly, money, resource, grantSkill, wind,
              stealth, observation, mount, battle, trade, tool, armor,
              weapon, monster, man, ship)
    
    def structure(self, name, structuretype,
                   monster=False, nomonstergrowth=False, canenter=False,
                   nobuildable=False,
                   protect=None, defense=None, maxMages=None,
                   specials=None, sailors=None, productionAided=None,
                   neverdecay=False, maxMaintenance=None, maxMonthlyDecay=None,
                   maintFactor=None, maintItem=None):
        """Handle a structure definition.
        
        Structures are places were units can enter into. Main types of
        structures are buildings and ships. Some of them have inner
        locations, like passages into underworld, some are monster
        lairs, forts and castles, production buildings like mines, etc.
        
        Structures are defined by the following parameters:
            name
                Name of the structure type.
            structuretype
                Type of the structure. Can be **building**, **ship** or
                **group of ships**.
            monster
                If *True* it's a monster lair. Defaults to *False*.
            nomonstergrowth
                It *True* monster in this structure won't regenerate.
                Defaults to *False*
            canenter
                If *True* player units can enter the structure.
                Defaults to *False*.
            nobuildable
                If *True* the structure cannot be build by players.
                Defaults to *False*.
            protect
                Number of soldiers the structure can protect. Defaults
                to *None*.
            defense
                Defense bonus granted to the units protected by the
                structure. It is a dicionary where keys are the attack
                types and values the bonus granted.
            maxMages
                Number of mages that can study inside the structure
                magic skills beyond 2nd level.
            specials
                List of special effects affected by the structure. Each
                element in the list is a dictionary with two keys:
                    *specialname*
                        Name of the special effect affected by the
                        structure.
                    *affected*
                        If *True*, units inside this building are
                        affected by the special. If *False*, units
                        inside the building are not affected by it.
            sailors
                For ships, number of sailors needed to sail the ship.
                Defaults to *None*.
            productionAided
                names of the item the structure aids to produce.
                *entertainment* is an allowed special value.
            neverdecay
                If *True* the structure never decay. Defaults to
                *False*.
            maxMaintenance
                Maximum points of damage taken by the structure before
                it begins to decaul. Defauls to *None*.
            maxMonthlyDecay
                Maximum damage the structure will take per month as
                decay. Defaults to *None*.
            maintFactor
                Damage repaired per unit of material used. Defaults to
                *None*.
            maintItem
                Name of the item used to repair the structure.
                *wood or stone* is a valid special value. Defaults to
                *None*.
                
        """
        print('object', name, structuretype, monster, nomonstergrowth,
              canenter, nobuildable, protect, defense, maxMages,
              specials, sailors, productionAided, neverdecay,
              maxMaintenance, maxMonthlyDecay, maintFactor, maintItem)
    
    def faction(self, name, num, factype=None):
        """Handle faction name and type.
        
        First line with data about a faction is the one reporting
        faction name and its time. This method handles this info.
        
        Parameters:
            name
                Faction name.
            num
                Faction number.
            factype
                Faction type. It's a dictionary where keys are possible
                faction types and values are faction points spent on
                the type. Usually allowed types are **war**, **trade**
                and **magic**, but different types can exists in some
                games.
                
        """
        print('faction', name, num, factype)
    
    def faction_date(self, month, year):
        """Handle report turn date.
        
        Report turn date is defined by its month and is year.
        
        Parameters:
            month
                Month name of the report. Month names are usually
                english month names, but different month names can be
                set up in some games.
            year
                Year number of the report. First year is year 1.
        
        """
        print('faction_date', month, year)
    
    def atlantis_version(self, version):
        """Handle atlantis version.
        
        Parameter:
            version
                Atlantis version string.
        
        """
        print('atlantis_version', version)
    
    def atlantis_rules(self, name, version):
        """Handle atlantis ruleset.
        
        Parameters:
            name
                Name of the ruleset.
            version
                Version of the ruleset.
        
        """
        print('atlantis_rules', name, version)
    
    def faction_warn(self, notimes=False, nopassword=False,
                      inactive=None, quitgame=None):
        """Handle a warn message for the faction.
        
        Parameters:
            notimes
                If *True* times are not being sent to the player.
                Defaults to *False*.
            nopassword
                If *True* the faction has no password set. Defaults to
                *False*.
            inactive
                If set, number of turns until the faction is removed
                due to inactivity. Defaults to *None*.
            quitgame
                If set, the faction has quitted the game. Allowed
                values are **restart** if the faction player has
                decided to restart the game, **gameover** if the
                game has finished and the player is not the winner,
                **won** if the player is the winner, and **eliminated**
                if the player has been eliminated from the game.
        
        """
        print('faction_warn', notimes, nopassword, inactive, quitgame)
        
    def faction_status(self, what, num, allowed):
        """Handle a faction status report.
        
        Atlantis reports faction status as one status type per line, so
        this method will be called several times per report, once per
        each faction status report received.
        
        Each time it is called this parameters are provided:
            what
                The status reported. Possible values are
                **Tax Regions**, **Trade Regions**, **Quartermasters**
                **Tacticians**, **Mages** and **Apprentices** (or
                **Acolytes** or whatever the apprentice name is set
                in the game).
            num
                Number of elements that faction currently has.
            allowed
                Max Number of elements allowed to the faction.
        
        """
        print('faction_status', what, num, allowed)
    
    def faction_attitudes(self, defaultattitude=None, hostile=None,
                            unfriendly=None, neutral=None, friendly=None,
                            ally=None):
        """Handle faction attitudes.
        
        Atlantis reports faction attitudes in several lines. First, it
        reports default faction attitude, that's the attitude towards
        unlisted factions in the following lines, or towards seen units
        of unknown faction. Then declared faction attitudes follow,
        having a list of factions per attitude type.
        
        Parameters:
            defaultattitude
                Default faction attitude. Allowed values are
                **hostile**, **unfriendly**, **neutral**, **friendly**
                and **ally**.
            hostile
                List of factions declared as **hostile**. Each faction
                is a dictionary with its *num* and *name*.
            unfriendly
                List of factions declared as **unfriendly**. Each
                faction is a dictionary with its *num* and *name*.
            neutral
                List of factions declared as **neutral**. Each faction
                is a dictionary with its *num* and *name*.
            friendly
                List of factions declared as **friendly**. Each faction
                is a dictionary with its *num* and *name*.
            ally
                List of factions declared as **ally**. Each faction is
                a dictionary with its *num* and *name*.
        
        """
        print('faction_attitudes', defaultattitude, hostile, unfriendly,
              neutral, friendly, ally)
    
    def faction_unclaimed(self, unclaimed):
        """Handle faction unclaimed.
        
        Parameter:
            unclaimed
                Amount of faction unclaimed money.
        
        """
        print('faction_unclaimed', unclaimed)

    def faction_event(self, message_type, message, unit=None):
        """Handle a read event or error.
        
        Faction are reported a number of events and errors. Most of
        them are attached to a unit, and in this case the *unit*
        parameter will be set. A few of them are general faction
        events and errors.
        
        Parameters:
            message_type
                **event** or **error**
            message
                Text of the event.
            unit
                If set the event is attached to the unit. Unit is given
                as a dictionary with its *num* and *name*.
        
        """
        print('event', message_type, message, unit)
    
    def region(self, terrain, name, xloc, yloc, zloc=None,
                population=0, racenames=None, wealth=0, town=None):
        """Handle line of region report.
        
        This is the very first handler called when a new region hexagon
        is found. This call signals the start of an hexagon information
        and also basic information about it: coordinates, terrain type,
        region name, peasants race and present town (if any).
        
        :class:`ReportConsumer` implementations should initialize hex
        information when this method is called.
        
        :param xloc: X coordinates of the hexagon.
        :param yloc: Y coordinates of the hexagon.
        :param zloc: Z coordinates of the hexagon. If *None* is given
            the hexagon is on surface.
        :param terrain: Terrain type.
        :param name: Region name the hexagon belongs to.
        :param population: Population of the hexagon, if any. Some
            terrain types as oceans have no population.
        :param racenames: Name of the race (plural form) of region
            inhabitants.
        :param wealth: Maximum amount available for taxing.
        :param town: If present, a dictionary with *name* and *type* of
            the town there. Allowed *type* values are ``village``,
            ``town`` and ``city``.
        
        :raise: :class:`NotImplementedError` if not overriden.
            
        """
        raise NotImplementedError('ReportConsumer method must be overriden')
    
    def region_weather(self, weather, nxtweather,
                         clearskies=False, blizzard=False):
        """Handle region weather report.
        
        Reports last and next month weather. Next month weather will be
        the one affecting movement orders given this turn. Weather can
        be ``clear``, ``winter``, ``monsoon season`` or ``blizzard``.
        
        Also, if weather was affected by magic it is also reported.
        
        :param weather: last month weather. Valid values are ``clear``,
            ``winter``, ``monsoon season`` and ``blizzard``.
        :param nxtweather: next month weather. Valid values are
            ``clear``, ``winter`` and ``monsoon season``. Unnatural
            values are not reported here.
        :param clearskies: if *True*, last month weather was caused by
            a Clear Skies spell. Defaults to *False*.
        :param blizzard: if *True*, last month weather was caused by a
            Blizzard spell. Defaults to *False*.
        
        :raise: :class:`NotImplementedError` if not overriden.
                
        """
        raise NotImplementedError('ReportConsumer method must be overriden')
    
    def region_wages(self, productivity, amount):
        """Handle region wages report.
        
        This method report wages per month, and total available amount.
        Wages are a float value with one decimal value (ex. $14.3), but
        the total amount are truncated per unit.
        
        :param productivity: wages obtained per man and month.
        :param amount: total amount of wages available in the region.
        
        :raise: :class:`NotImplementedError` if not overriden.
        
        """
        raise NotImplementedError('ReportConsumer method must be overriden')
    
    def region_market(self, market, items):
        """Handle region market report.
        
        This method is called up to twice per region. One for the sell
        market (products that players can *sell* to the market) and one
        for the buy market (products that players can *buy* from the
        market). Each market is a list of items with their sell/buy
        prices.
        
        :param market: market type. Allowed values are ``sell`` and
            ``buy``.
        :param items: list of
            :class:`~atlantis.gamedata.item.ItemMarket` objects.
        
        :raise: :class:`NotImplementedError` if not overriden.
        
        """
        raise NotImplementedError('ReportConsumer method must be overriden')
    
    def region_entertainment(self, amount):
        """Handle region entertainment report.
        
        The only parameter of this method is the total amount of
        entertainment available.
        
        :param amount: Entertainment available in the region.
        
        :raise: :class:`NotImplementedError` if not overriden.
        
        """
        raise NotImplementedError('ReportConsumer method must be overriden')
    
    def region_products(self, products):
        """Handle region products report.
        
        The only parameter of this method is a list of available
        products in the region.
        
        New products can be discovered in the region when units get
        the appropiate skill.
        
        :param products: list of
            :class:`~atlantis.gamedata.item.ItemAmount` objects.
        
        :raise: :class:`NotImplementedError` if not overriden.
        
        """
        raise NotImplementedError('ReportConsumer method must be overriden')
    
    def region_exits(self, direction, terrain, name, xloc, yloc,
                       zloc='surface', town=None):
        """Handle a region exit direction.
        
        Each region has a number of linked hexagons. Each of them
        are reported by calling this method. When an exit is found some
        basic information of the linked hexagon is attached.
        
        :param direction: direction of the exit. Allowed values are
            ``North``, ``Northeast``, ``Southeast``, ``South``,
            ``Southwest``, ``Northwest``. 
        :param xloc: X coordinates of the hexagon.
        :param yloc: Y coordinates of the hexagon.
        :param zloc: Z coordinates of the hexagon. If *None* is given
            the hexagon is on surface.
        :param terrain: terrain type.
        :param name: region name the hexagon belongs to.
        :param town: if present, a dictionary with *name* and *type* of
            the town there. Allowed *type* values are ``village``,
            ``town`` and ``city``.
            
        :raise: :class:`NotImplementedError` if not overriden.
        
        """
        raise NotImplementedError('ReportConsumer method must be overriden')
    
    def region_gate(self, gate, gateopen):
        """Handle a gate report.
        
        If a gate is found in the region it is reported.
        
        Parameters:
            gate
                Gate number, or 0 if it's closed.
            gateopen
                *True* if the gate is open, *False* otherwise.
        
        """
        print('region_gate', gate, gateopen)
    
    def region_structure(self, num, name, ob, items=None,
                           incomplete=False, decay=False, maintenance=False,
                           inner=False, runes=False, canenter=True):
        """Handle a structure in a region report.
        
        A structure is a complex entity in Atlantis. Structures can
        hold player or monster units inside, open paths to other map
        levels, improve resource production, provide protection to
        soldiers inside or, in case of ships, provide sailing or even
        flying transportation.
        
        When a region report is finished with their products listing
        it's time for units and structures. First all units outside
        structures are listed, then each object, followed by their
        stacked units.
        
        Structure is defined by the following parameters:
            num
                Unique number for the structure in the hex. Structures
                will be listed ordered by its number, and it's the
                direction unit must issue in order to enter inside it.
            name
                Name of the structure. Note that this is the name given
                by the owner player to the structure, not the name of
                the structure type.
            ob
                Structure type. This parameter is a dictionary with
                only the *name* value of the structure type. This
                *name* is the generic structure type (like **Mine** or
                **Castle**).
            items
                List of items, only given in case the structure is a
                fleet of ships. In this case each element in the list
                is a dictionary with *num* and *name*, *names* of the
                ship items building the fleet. Defaults to *None*.
            incomplete
                Amount of work needed to complete the structure.
                Defaults to zero.
            decay
                When decay is activated it is *about to decay* when it
                could be completely ruined next month if it's not
                repaired. When this happens this flag is *True*.
                Defaults to *False*.
            maintenance
                When decay is activated it *needs maintenance* when the
                structure is damaged and needs to be repaired but it's
                not *about to decay* next month. Defaults to *False*.
            inner
                Some structures have inner locations, a shafts. Units
                can move *in* such structures. This structures have
                their inner flag set to *True*. Defaults to *False*.
            runes
                *True* if the structure has engraved runes of guard,
                *False* otherwise. Defaults to *False*.
            canenter
                *True* if player units can enter the structure, *False*
                otherwise. Defaults to *True*.
                
        """
        print('region_structure', num, name, ob, items, incomplete, decay,
              maintenance, inner, runes, canenter)
    
    def region_unit(self, num, name, items, tab=False, guard=None,
                      faction=None, attitude='neutral', behind=False,
                      holding=False, autotax=False, noaid=False,
                      sharing=False, nocross=False,
                      reveal=None, consuming=None, spoils=None,
                      visited=None, canstudy=None,
                      readyitem=None, readyarmor=None, readyweapon=None,
                      combat=None, skills=None,
                      weight=None, capacity=None
                      ):
        """Handle a unit report in a region.
        
        Units are the main entities in Atlantis: every action a player
        does is by issuing orders to their units.
        
        Units are mainly a group of items, of which at least one must
        be a man or a monster, plus a group of learned skills. In
        addition units will have some identifiers (num and name),
        a reference to its owner faction and a good bunch of flags.
        
        Unit reports are not complete. While a complete report is
        received from own units, units stats are hidden to other
        players. Some of them can be revealed depending on unit's
        reveal flag or relative *OBSE* and *STEA* skills.
        
        There're three levels of unit visibility:
        
        - Own units. Always visible and complete report.
        
        - Extended report. Unit is revealing faction or our *OBSE* is
        greater than unit *STEA*. Faction is revealed, as well as some
        flags like *avoiding* and *behind*.
        
        - Basic report. Unit is revealing unit, on guard, or our *OBSE*
        is equal than unit *STEA*. Unit is visible, but less stats are
        reported.
        
        These parameters are reported every time a unit is visible:
            num
                Unique identifier of the unit.
            name
                Name of the unit.
            items
                List of items in the unit (including men). All items
                are reported *except* weightless items, that are only
                reported for own units.
                
                Each element in the list is a dictionary with the
                following keys:
                    *amt*
                        Amount of items of this type.
                    *abr*
                        Abbreviature of the item type.
                    *name*/*names*
                        Name or names of the item.
                    *illusion*
                        *True* if it's an illusion. Defaults to
                        *False*.
                    *unfinished*
                        *True* if the item is unfinished. Defaults to
                        *False*.
                    *num*
                        Amount of work needed to finish the item if
                        it's unfinished. Defaults to 0.
            tab
                If *True* the unit is tabbed. That is, the unit is
                inside a structure. Defaults to *False*.
            guard
                Flags if the unit is on guard (**guard**), avoiding
                (**avoid**) or *None*. Note that while **guard** is
                always reported, **avoid** only in the *extended*
                report. Defaults to *None*.
                
        In addition these parameters are reported with superior *OBSE*
        or if the unit is revealing faction:
            faction
                If visible, faction will be a dictionary with *num* and
                *name* of unit's faction. Defaults to *None*.
            attitude
                If the option *showattitudes* is chosen for the report
                this parameter will show our attitude towards unit's
                faction. Possible values are **me**, **ally**,
                **friendly**, **neutral**, **unfriendly** and
                **hostile**.
                
                If *showattitudes* is not active or unit's faction is
                unknown *attitude* will take **neutral** value.
            behind
                If *True* the unit is *behind* in combat. Defaults to
                *False*.
            
        Parameters only give for own units:
            holding
                If *True* the unit is *holding* its position. Defaults
                to *False*.
            autotax
                If *True* the unit will always tax without having to
                issue the *tax* order. Defaults to *False*.
            noaid
                If *True* the unit won't call for help if attacked.
                Defaults to *False*.
            sharing
                If *True* the unit will share its posessions with any
                other unit of your faction that needs them. Defaults to
                *False*.
            nocross
                If *True* the unit won't cross a body of water even if
                it can do it. Defaults to *False*.
            reveal
                Reveal flag of the unit. Can be **faction**, **unit**
                or *None*. Defaults to *None*.
            consuming
                If set the unit will consume food in preference to
                silver. Possible values are **unit** and **faction**
                to consume own's unit food or faction food. Defaults to
                *None*.
            spoils
                If set the unit has limited which spoils can take from
                battle. Possible values are **weightless**, **flying**,
                **walking**, **riding** and **sailing**. Defaults to
                *None*.
            visited
                List of places (strings) the unit has visited, for
                quests. Defaults to *None*.
            canstudy
                List of advanced skills that need prerequisites that
                the unit has fulfilled so it can now study them. Each
                element in the list is a dicionary with skill *abbr*
                and *name*. Defaults to *None*.
            readyitem
                List of ready miscellaneous combat items for the unit.
                Each element in the list is a dictionary with item
                *abr* and *name*. Defaults to *None*.
            readyarmor
                List of ready armor items for the unit. Each element in
                the list is a dictionary with item *abr* and *name*.
                Defaults to *None*.
            readyweapon
                List of ready weapon items for the unit. Each element
                in the list is a dictionary with item *abr* and *name*.
                Defaults to *None*.
            combat
                Unit combat spell. It's a dictionary with skill *abbr*
                and *name*. Defaults to *None*.
            skills
                List of unit skills. Each element in the list is a
                dictionary with *abbr*, *name*, *level* and *days* of
                the studied skill. In addition, if skills require
                experience is activated a *rate* is added to the
                dictionary.
                
                Defaults to *None*.
            weight
                Unit weight. Defaults to *None*.
            capacity
                Unit capacity. It's a dictionary where keys are the
                movement types and values are capacities for them. Note
                that capacity include own weight, so a man will have
                a capacity of 15 and a weight of 10, being able to
                carry up to 5 weight of items with him.
                
                Movement types are: *flying*, *riding*, *walking* and
                *swimming*.
        
        """
        print('region_unit', num, name, items, tab, guard, faction, attitude,
              behind, holding, autotax, noaid, sharing, nocross, reveal,
              consuming, spoils, visited, canstudy, readyitem, readyarmor,
              readyweapon, combat, skills, weight, capacity)


class ReportParser:
    """Report parser state machine.

    :class:`ReportParser` parses whole report. It is implemented as
    state machine, with different handler functions depending of which
    is being parsed. Parsing result is sent to its registered consumer
    together with the original line, in case the consumer needs it
    for entity description.
    
    Although the common use of :class:`ReportParser` should be
    instantiate the class and calling its public parse method all
    methods completely parsing a single report line are public too, so
    this class can be used to parse any single line in the report.
    Helper methods parsing portions of a line are not public, however.
    
    :class:`ReportParser` has the following public methods.

    """
    
    # Class constants
    _START, _GM_REPORT_SKILLS, _GM_REPORT_ITEMS, _GM_REPORT_OBJECTS, \
        _GM_REPORT_REGIONS, _REPORT_FACTION, _REPORT_ERRORS, _REPORT_BATTLES, \
        _REPORT_EVENTS, _REPORT_SKILLS, _REPORT_ITEMS, _REPORT_OBJECTS, \
        _REPORT_ATTITUDES, _REPORT_REGIONS, _ORDERS_TEMPLATE = range(15)
    
    # Constants: regex strings    
    # Basic strings
    _re_str_direction = r'(?P<direction>Northeast|Northwest|Southeast|' \
            r'Southwest|South|North)'
                    
    # Skills
    _re_str_skill_str = r'(?P<name>[^[]+) \[(?P<abbr>\w+)\]'
    _re_str_skill_str_level = _re_str_skill_str + r' (?P<level>\d+)'
    _re_str_skill_line = _re_str_skill_str_level + r': (?P<descr>.*)'
    _re_str_skill_no_report = r'No skill report'
    _re_str_skill_no_exp = r'This skill cannot be increased through experience'
    _re_str_skill_no_teach = r'This skill cannot be taught to other units'
    _re_str_skill_no_study = r'This skill cannot be studied via normal means'
    _re_str_skill_slow_study = \
            r'This skill is studied at one half the normal speed'
    _re_str_skill_cost = \
            r'This skill costs (?P<cost>\d+) silver per month of study'
    _re_str_skill_depends = \
            r'This skill requires (?P<depends>.*) to begin to study'
    _re_str_skill_builds = \
            r'A unit with this skill may BUILD (?=an?)(?P<builds>.*)'
    _re_str_skill_magic_production = \
            r'A mage with this skill (?=' \
            r'has a \d+ percent times their level chance to create a|' \
            r'may create (\d+ times )?their level in)'
    _re_str_skill_magic_production_end = \
            r'\[(?P<abr>\w+)\] via magic(?: at a cost of (?P<mInput>.+))?\. ' \
            r'To use this spell, the mage should CAST'
    _re_str_skill_magic_production_100 = \
            r'has a (?P<mOut>\d+) percent times their level chance to create ' \
            r'an? (?:illusory )?(?P<name>[^[]+) ' + \
            _re_str_skill_magic_production_end
    _re_str_skill_magic_production_1 = \
            r'may create (?:(?P<mOut>\d+) times )?their level ' \
            r'in (?:illusory )?(?P<names>[^[]+) ' + \
            _re_str_skill_magic_production_end
    _re_str_skill_production_discover = r'A unit with this skill is able to ' \
            r'determine if a region contains (?P<items>.*)\.'
    _re_str_skill_production = \
            r'A unit with this skill may (?P<command>BUILD|PRODUCE) ' \
            r'(?P<production>.*)\.'
    _re_str_skill_production_produce = \
            r'(?P<skillout>a number of )?(?P<names>[^[]+) \[(?P<abr>\w+)\]' \
            r'(?: equal to their skill level)?' \
            r'(?: from (?P<orinputs>any of )?(?P<pInput>.+))? at a rate ' \
            r'of (?P<pOut>\d+) per (?:(?P<pMonths>\d+) )?man\-months?'
    _re_str_skill_production_build = \
            r'(?P<skillout>a number of )?(?P<names>[^[]+) \[(?P<abr>\w+)\]' \
            r'(?: equal to their skill level)?' \
            r' from (?P<orinputs>any of )?(?P<pInput>.+)'
    _re_str_skill_combat_spell = \
            r'A mage with this skill can cast (?P<special>.+) ' \
            r'In order to use this spell in combat, the mage should use ' \
            r'the COMBAT order to set it as his combat spell\.'
    _re_str_skill_fundation = \
            r'The (?:\w+) skill is not directly useful to a mage, but is ' \
            r'rather one of the Foundation skills'
    _re_str_skill_apprentice = \
            r'A unit with this skill becomes an (?P<apprentice>\w+)\. While ' \
            r'(?P=apprentice)s cannot cast spells directly, '
    
    # Items
    _re_str_item_str = r'(?P<name>[^[]+) \[(?P<abr>\w+)\]'
    _re_str_item_amt_str = r'(?P<amt>\d+|unlimited) (?P<names>[^[]+) ' \
                           r'\[(?P<abr>\w+)\]'
    _re_str_item_unfinished = r'unfinished (?P<item>.+) \(needs (?P<num>\d+)\)'
    _re_str_item_illusion = r'(?P<item>.+) \(illusion\)'
    _re_str_item_line = r'(?P<illusion>illusory )?(?P<name>[^[]+) ' \
                        r'\[(?P<abr>\w+)\]'
    _re_str_item_line_item = r', weight (?P<weight>\d+)(?P<descr>.*)'
    _re_str_item_line_ship = r'\. This is a (?=ship|flying \'ship\')'
    _re_str_item_max_inventory = \
            r'A unit may have at most ' + _re_str_item_amt_str
    _re_str_item_cantgive = r'This item cannot be given to other units'
    _re_str_item_food = r'This item can be eaten to provide (?P<food>\d+) ' \
                        r'silver towards a unit\'s maintenance cost'
    _re_str_item_mageonly = r'This item may only be used by a mage'
    _re_str_item_battle = r'This item is a miscellaneous combat item\. ' \
            r'(?P<mageonly>This item may only be used by a mage.*)?' \
            r'This item (?P<shield>provides|can cast) (?P<special>.*)'
    _re_str_item_grant = r'This item allows its possessor to CAST the ' \
            r'(?P<name>.+) spell as if their skill in .+ was ' \
            r'(?:.+ of their (?P<fromSkills>.+) skills?, ' \
            r'up to a maximum of )?level (?P<maxGrant>\d+)\.' \
            r'(?: A skill level of at least (?P<minGrant>\d+) will always)?'
    # Item special
    _re_str_item_special_damage = \
            r'This ability does between (?P<minnum>\d+) and (?P<maxnum>\d+) ' \
            r'(?P<expandLevel>times the skill level of the mage )?' \
            r'(?P<type>.+) attacks\.(?: Each attack causes the target to be ' \
            r'effected by (?P<effect>.+))?'
    _re_str_item_special_damage_effect = \
            r'(?P<name>.+?)(?: \((?P<effect>.+)\) for ' \
            r'(?P<oneshot>their next attack|the rest of the battle))?\.' \
            r'(?: This effect cancels out the effects of ' \
            r'(?P<cancelEffect>.+)\.)?'
    _re_str_item_special_defbonus = \
            r'This (?:ability|spell) provides (?P<defs>.*) to the user'
    _re_str_item_special_defbonus_def = \
            r'a defensive bonus of (?P<val>\d+) ' \
            r'(?P<expandLevel>per skill level )?' \
            r'versus (?P<type>.+) attacks'
    _re_str_item_special_shield = \
            r'(?:This spell provides a shield|' \
            r'This ability provides the wielder with a defence bonus of ' \
            r'(?P<level>\d+)) against all (?P<shields>.+) attacks'
    _re_str_item_special_nobuilding = \
            r'The bonus given to units inside buildings is not effective ' \
            r'against this ability'
    _re_str_item_special_nomonster =  r'This ability cannot target monsters'
    _re_str_item_special_illusion =  r'This ability will only target illusions'
    _re_str_item_special_effectif = \
            r'This ability will (?P<effectif>not|only) target creatures ' \
            r'which are currently affected by (?P<effects>.+)\.'
    _re_str_item_special_soldierif = \
            r'This ability will (?P<soldierif>not|only) target ' \
            r'(?!units (which|inside))(?P<mount>units mounted on )?' \
            r'(?P<items>.+)\.'
    _re_str_item_special_buildingif = r'This ability will only target units ' \
            r'(?P<buildingif>which are inside|' \
            r'inside structures, with the exception of) ' \
            r'the following structures: (?P<buildings>.+)\.'
    _re_str_item_special_name = r'(?P<specialname>.+) in battle ' \
            r'(?:at a skill level of (?P<level>\d+))?'
    _re_str_item_wind = r'The possessor of this item will add ' \
            r'(?P<windBoost>\d+) movement points to ships requiring up to ' \
            r'(?P<val>\d+) sailing'
    _re_str_item_stealth = r'This item grants a (?P<val>\d+) point bonus to ' \
            r'a unit\'s stealth skill(?P<perman> \(note that a unit)?'
    _re_str_item_observation = r'This item grants a (?P<val>\d+) point bonus ' \
            r'to a unit\'s observation skill(?P<perman> \(note that a unit)?'
    _re_str_item_money = r'This is the currency of'
    _re_str_item_resource = r'This item is a trade resource'
    _re_str_item_mount = r'This is a mount\. ' \
            r'(?:No skill is required to use this mount|' \
            r'This mount is unridable|' \
            r'This mount requires (?P<skill>.+) of at least level (?:\d+) to ' \
            r'ride in combat)\. ' \
            r'This mount gives a minimum bonus of \+(?P<minBonus>\d+) when ' \
            r'ridden into combat\. ' \
            r'This mount gives a maximum bonus of \+(?P<maxBonus>\d+) when ' \
            r'ridden into combat\.' \
            r'(?: This mount gives a maximum bonus of ' \
            r'\+(?P<maxHamperedBonus>\d+) when ridden into combat in terrain ' \
            r'which allows ridden mounts but not flying mounts\.)?' \
            r'(?: When ridden, this mount causes (?P<special>.+))?'
    _re_str_item_trade = r'This is a trade good\.' \
            r'(?: This item can be ' \
            r'(?:bought and sold for (?P<baseprice>\d+) silver|' \
            r'bought for between (?P<minbuy>\d+) and (?P<maxbuy>\d+) ' \
            r'silver\. ' \
            r'This item can be sold for between (?P<minsell>\d+) and ' \
            r'(?P<maxsell>\d+) silver)\.)?'
    _re_str_item_tool = r'This is a tool\. This item increases the ' \
            r'production of (?P<items>.+)\.'
    _re_str_item_armor = r'This is a type of armor\. This armor will protect ' \
            r'its wearer (?P<saves>[^.]+)\.(?P<assassinate> This armor may ' \
            r'be worn during assassination attempts\.)?'
    _re_str_item_armor_saves = \
            r'(?P<percent>\d+)% of the time versus (?P<class>.+) attacks'
    _re_str_item_weapon = r'This is a (?:(?P<range>ranged|long|short) )?' \
            r'(?P<weapClass>.+?) weapon\.(?P<extra>.+)'
    _re_str_item_weapon_skill = \
            r'(?:No skill is needed to wield this weapon|' \
            r'Knowledge of ' + _re_str_skill_str + r' is needed to wield ' \
            r'this weapon)\.'
    _re_str_item_weapon_bonus = r'(?:This weapon grants|and) a ' \
            r'(?P<type>bonus|penalty) of (?P<bonus>\d+) on ' \
            r'(?P<when>attack|defense)(?P<both> and defense)?\.'
    _re_str_item_weapon_mount_bonus = r'This weapon (?:also )?grants a ' \
            r'(?P<type>bonus|penalty) of (?P<bonus>\d+) ' \
            r'against mounted opponents\.'
    _re_str_item_weapon_nofoot = \
            r'Only (?P<foot>mounted|foot) troops may use this weapon\.'
    _re_str_item_weapon_ridingbonus = r'Wielders of this weapon, if mounted, ' \
            r'get their riding skill bonus on combat (?:(?P<attack>attack) ' \
            r'and )?defense\.'
    _re_str_item_weapon_nodefense = r'Defenders are treated as if they have ' \
            r'an effective combat skill of 0\.'
    _re_str_item_weapon_noattackerskill = r'Attackers do not get skill bonus ' \
            r'on defense\.'
    _re_str_item_weapon_alwaysready = r'(?P<ready>Wielders of this weapon ' \
            r'never miss a round to ready their weapon|There is a 50% chance ' \
            r'that the wielder of this weapon gets a chance to attack in ' \
            r'any given round)\.'
    _re_str_item_weapon_attacktype = r'This weapon attacks versus the ' \
            r'target\'s defense against (?P<attackType>.+?) attacks\.'
    _re_str_item_weapon_numattacks = r'This weapon allows ' \
            r'(?:a number of attacks equal to (?P<attacksSkill>(?:half )?' \
            r'the skill level) (?:\(rounded up\) )?of the attacker' \
            r'(?: plus (?P<matts>\d+))?|(?P<atts>\d+) attacks?) ' \
            r'(?:per|every (?P<natts>\d+)) rounds?\.'
    _re_str_item_monster = r'This is a monster\. This monster attacks with a ' \
            r'combat skill of (?P<attackLevel>\d+)\.'
    _re_str_item_monster_resist = r'This monster ' \
            r'(?:has a resistance of (?P<val>\d+)|is (?P<valstr>.+?)) to ' \
            r'(?P<type>.+?) attacks\.'
    _re_str_item_monster_special = \
            r'Monster can cast (?P<special>.+?\.)(?= This monster )'
    _re_str_item_monster_stats = r'This monster has (?P<atts>\d+) melee ' \
            r'attacks? per round and takes (?P<hits>\d+) hits? to kill\. ' \
            r'(?:This monster regenerates (?P<regen>\d+) hits per round of ' \
            r'battle\. )?' \
            r'This monster has a tactics score of (?P<tactics>\d+), a ' \
            r'stealth score of (?P<stealth>\d+), and an observation score of ' \
            r'(?P<obs>\d+)\.'
    _re_str_item_monster_spoils = r'This monster might have (?P<type>.+) ' \
            r'items and silver as treasure\.'
    _re_str_item_man = r'This race may study (?:(?P<skills>.*?) to level ' \
            r'(?P<specialLevel>\d+) and all other skills|all skills) to ' \
            r'level (?P<defaultLevel>\d+)'
    _re_str_item_withdraw = r', costs (?P<price>\d+) silver to withdraw'
    _re_str_item_hitchItem = r', walking capacity (?P<cap>\d+) when hitched ' \
            r'to a ' + _re_str_item_str
    _re_str_item_capacity = r', (?:(?P<type>walking|riding|swimming|flying) ' \
            r'capacity (?P<cap>\d+)|can (?P<typeShort>walk|ride|swim|fly))'
    _re_str_item_speed = r', moves (?P<speed>\d+) hex(?:es)? per month'
    _re_str_item_ship = r'. This is a (?P<fly>flying \')?ship\'? with a ' \
            r'capacity of (?P<cap>\d+) and a speed of (?P<speed>\d+) ' \
            r'hex(?:es)? per month\. This ship requires a total of ' \
            r'(?P<sailors>\d+) levels of sailing skill to sail'
    _re_str_item_ship_object = r'\. This ship provides defense to the first ' \
            r'(?P<protect>\d+) men inside it, giving a defensive bonus of ' \
            r'(?P<bonus>.+?)(?=\.)'
    _re_str_item_ship_mages = r'\. This ship will allow (:?up to ' \
            r'(?P<maxMages>\d+) mages|one mage) to study above level 2'
    
    # Objects
    _re_str_object_cost = r'an? (?P<name>.*) from (?P<cost>\d+) (?P<items>.*)'
    
    # Regions
    _re_str_region_shortprint = r'(?P<type>\S[^(]+) \((?P<xloc>\d+),' \
            r'(?P<yloc>\d+)(?:,(?P<zloc>[^)]+))?\) in (?P<name>[^,.]+)'
    _re_str_region_print = _re_str_region_shortprint + \
            r'(?:, contains (?P<townname>[^[]+) \[(?P<towntype>.+)\])?'
    _re_str_region_id_line = _re_str_region_print + \
            r'(:?, (?P<population>\d+) peasants(?: \((?P<racenames>.+)\))?' \
            r', \$(?P<wealth>\d+))?\.'
    _re_str_region_weather = TAB + \
            r'.* was (?:(?P<weathereffect>unnaturally|an unnatural) )?' \
            r'(?P<weather>.+) last month; it will be (?P<nxtweather>.+) ' \
            r'next month'
    _re_str_region_wages = TAB + r'Wages: \$(?P<productivity>[0-9.]+)' \
            r'(?: \(Max: \$(?P<amount>\d+))?'
    _re_str_region_market = TAB + r'(?P<type>Wanted|For Sale): ' \
            r'(?P<items>none|.+)\.'
    _re_str_region_entertainment = TAB + r'Entertainment available: \$' \
            r'(?P<amount>\d+)\.'
    _re_str_region_products = TAB + r'Products: (?P<products>none|.+)\.'
    _re_str_region_exit = TAB + _re_str_direction + r' : ' + \
            _re_str_region_print
    _re_str_region_gate = r'There is a (?P<gateopen>closed )?Gate here' \
            r'(?: \(Gate (?P<gate>\d+))?'
    _re_str_region_object = \
            r'\+ (?P<name>[^[]+) \[(?P<num>\d+)\] : (?P<object>.+)'
    _re_str_region_object_canenter = r', closed to player units'
    _re_str_region_object_runes = r', engraved with Runes'
    _re_str_region_object_inner = r', contains an inner'
    _re_str_region_object_maintenance = r', needs maintenance'
    _re_str_region_object_decay = r', about to decay'
    _re_str_region_object_incomplete = r', needs (?P<incomplete>\d+)'
    
    # Units
    _re_str_unit = r'(?P<tab>\s*)(?P<attitude>[-*=:%!]) ' \
            r'(?P<name>[^(]+) \((?P<num>\d+)\)' \
            r'(?P<guard>, on guard)?' \
            r'(?:, (?P<factionname>[^(]+) \((?P<factionnum>\d+)\)' \
            r'(?P<avoiding>, avoiding)?(?P<behind>, behind)?)?' \
            r'(?:, revealing (?P<reveal>unit|faction))?' \
            r'(?P<holding>, holding)?(?P<autotax>, taxing)?' \
            r'(?P<noaid>, receiving no aid)?(?P<sharing>, sharing)?' \
            r'(?:, consuming (?P<consuming>unit|faction)\'s food)?' \
            r'(?P<nocross>, won\'t cross water)?' \
            r'(?:, (?P<spoils>.+) battle spoils)?' \
            r'(?P<unit>.+)'
    _re_str_unit_visited = r'\. Has visited (?P<visited>.+[^.])'
    _re_str_unit_canstudy = r'\. Can Study: (?P<canstudy>.+)'
    _re_str_unit_ready = r'\. Ready (?P<ready>weapon|armor|item)s?: ' \
            r'(?P<items>.+)'
    _re_str_unit_combat_skill = r'\. Combat spell: ' + _re_str_skill_str
    _re_str_unit_skills = r'\. Skills: (?P<skills>.+)'
    _re_str_unit_skills_skill = _re_str_skill_str + r' (?P<level>\d+) ' \
            r'\((?P<days>\d+)(?:\+(?P<rate>\d+))?\)'
    _re_str_unit_capacity = r'\. Weight: (?P<weight>\d+)\. Capacity: ' \
            r'(?P<flying>\d+)/(?P<riding>\d+)/(?P<walking>\d+)/' \
            r'(?P<swimming>\d+)'
    
    # Objects
    _re_str_object = r'(?P<name>[^:]+): This is a (?P<type>building|ship|' \
            r'group of ships)\.' \
            r'(?P<monster> Monsters can potentially lair in this structure\.' \
            r'(?P<nomonstergrowth> Monsters in this structures will never ' \
            r'regenerate\.)?)?' \
            r'(?P<canenter> Units may enter this structure\.)?' \
            r'(?: This structure provides defense to the first ' \
            r'(?P<protect>\d+) men inside it\.' \
            r'(?: This structure gives a defensive bonus of ' \
            r'(?P<bonus>[^.]+)\.)?)?'
    _re_str_object_special = r'Units in this structure are (?P<not>not )?' \
            r'affected by (?P<specialname>[^.]+)\.'
    _re_str_object_ship = r'This ship requires (?P<sailors>\d+) total levels ' \
            r'of sailing skill to sail\.'
    _re_str_object_mages = r'This structure will allow (:?up to ' \
            r'(?P<maxMages>\d+) mages|one mage) to study above level 2'
    _re_str_object_nobuildable = r'This structure cannot be built by players\.'
    _re_str_object_productionAided = r'This trade structure increases the ' \
            r'amount of (?P<names>.+?) available in the region\.'
    _re_str_object_neverdecay = r'This structure will never decay\.'
    _re_str_object_decay = r'This structure can take (?P<maxMaintenance>\d+) ' \
            r'units of damage before it begins to decay\. Decay can occur at ' \
            r'a maximum rate of (?P<maxMonthlyDecay>\d+) units per month\.' \
            r'(?: Repair of damage is accomplished at a rate of ' \
            r'(?P<maintFactor>\d+) damage units per unit of (?P<item>[^.]+)\.)?'
            
    # Faction
    _re_str_faction_str = r'(?P<name>[^(]+) \((?P<num>\d+)\) \((?P<type>.+)\)'
    _re_str_faction_date = r'(?P<month>.+), Year (?P<year>\d+)'
    _re_str_atlantis_version = r'Atlantis Engine Version: (?P<version>.+)'
    _re_str_atlantis_rules = r'(?P<name>[^,]+), Version: (?P<version>.+)'
    _re_str_faction_notimes = r'Note: The Times is not being sent to you.'
    _re_str_faction_nopassword = \
            r'REMINDER: You have not set a password for your faction!'
    _re_str_faction_inactive = \
            r'WARNING: You have (?P<turns>\d+) turns until your faction is ' \
            r'automatically removed due to inactivity!'
    _re_str_faction_quit_restart = r'You restarted your faction this turn'
    _re_str_faction_quit_gameover = r'I\'m sorry, the game has ended'
    _re_str_faction_quit_won = r'Congratulations, you have won the game!'
    _re_str_faction_quit_eliminated = \
            r'I\'m sorry, your faction has been eliminated'
    _re_str_faction_status = \
            r'(?P<what>Tax Regions|Trade Regions|Quartermasters|' \
            r'Tacticians|Mages|[^:]+): (?P<num>\d+) \((?P<allowed>\d+)\)'
    _re_str_faction_attitudes_default = r'Declared Attitudes \(default ' \
            r'(?P<defaultattitude>Hostile|Unfriendly|Neutral|Friendly|Ally)\):'
    _re_str_faction_attitudes = \
            r'(?P<attitude>Hostile|Unfriendly|Neutral|Friendly|Ally) : ' \
            r'(?P<factions>.+)\.'
    _re_str_faction_unclaimed = r'Unclaimed silver: (?P<unclaimed>\d+)\.'
    
    # Errors and events
    _re_str_unit_error = r'(?P<name>.+) \((?P<num>\d+)\): (?P<message>.+)\.'
    
    # Battle
    _re_str_battle_start = r'(?P<attname>[^(]+) \((?P<attnum>\d+)\) ' \
            r'(?P<ass>attempts to assassinate|attacks) ' \
            r'(?P<tarname>[^(]+) \((?P<tarnum>\d+)\) in ' + \
            _re_str_region_shortprint + '!'
    _re_str_battle_assassination = r'(?P<tarname>[^(]+) \((?P<tarnum>\d+)\) ' \
            r'is assassinated in ' + \
            _re_str_region_shortprint + '!'
    _re_str_battle_side = r'(?P<side>Attacker|Defender)s:'
    _re_str_battle_unit = r'(?P<name>[^[(]+) \((?P<num>\d+)\)' \
            r'(?: (?P<facname>[^(]+) \((?P<facnum>\d+)\))?' \
            r'(?P<behind>, behind)?(?:, (?P<list>[^.]+))?\.'
    _re_str_battle_unit_item = r'(?:(?P<amt>\d+) )?(?P<name>[^[]+) ' \
            r'\[(?P<abr>[^]]+)\]' \
            r'(?: \(Combat (?P<attackLevel>\d+)/(?P<defense>\d+), ' \
            r'Attacks (?P<numAttacks>\d+), Hits (?P<hits>\d+), ' \
            r'Tactics (?P<tactics>\d+)\))?'
    _re_str_battle_unit_skill = r'(?P<name>.+) (?P<level>\d+)'
    _re_str_battle_round_free = r'(?P<name>[^(]+) \((?P<num>\d+)\) ' \
            r'gets a free round of attacks\.'
    _re_str_battle_round_shield = r'(?P<name>[^(]+) \((?P<num>\d+)\) casts ' \
            r'(?P<shielddesc>.+ Shield|Clear Skies|invulnerability)\.'
    _re_str_battle_round_special_deflected = \
            r'(?P<name>[^(]+) \((?P<num>\d+)\) ' \
            r'(?P<spelldesc>.+), but it is deflected\.'
    _re_str_battle_round_special = r'(?P<name>[^(]+) \((?P<num>\d+)\) ' \
            r'(?P<spelldesc>.+), (?P<spelldesc2>\D*)(?P<tot>\d+)' \
            r'(?P<spelltarget>[^.]+)\.'
    _re_str_battle_round_regenerate = r'(?P<name>[^(]+) \((?P<num>\d+)\) ' \
            r'(?P<regenerate>take|regenerate)s (?P<damage>no|\d+) hits ' \
            r'(?:bringing it to|leaving it at) (?P<hits>\d+)/(?P<maxhits>\d+)\.'
    _re_str_battle_round_loses = r'(?P<name>[^(]+) \((?P<num>\d+)\) loses ' \
            r'(?P<loses>\d+)\.'
    _re_str_battle_round_normal = r'Round (?P<round>\d+):'
    _re_str_battle_end = r'(?P<name>[^(]+) \((?P<num>\d+)\) is ' \
            r'(?P<result>routed|destroyed)!'
    _re_str_battle_end_tie = r'The battle ends indecisively\.'
    _re_str_battle_casualties = r'Total Casualties:'
    _re_str_battle_casualties_heal = r'(?P<name>[^(]+) \((?P<num>\d+)\) ' \
            r'heals (?P<heal>\d+)\.'
    _re_str_battle_casualties_loses = r'(?P<name>[^(]+) \((?P<num>\d+)\) ' \
            r'loses (?P<loses>\d+)\.'
    _re_str_battle_casualties_units = r'Damaged units: (?P<units>.+)\.'
    _re_str_battle_spoils = r'Spoils: (?P<spoils>.+)\.'
    _re_str_battle_undead_raise = r'(?P<units>.+) rises? from the grave to ' \
            r'(?:join (?P<name>[^(]+) \((?P<num>\d+)\)|seek vengeance)\.'
    
    # Section markers
    _re_section_skill = re.compile('^Skill reports:$')
    _re_section_item = re.compile('^Item reports:$')
    _re_section_object = re.compile('^Object reports:$')
    _re_section_report = re.compile('^Atlantis Report For:$')
    _re_section_faction = re.compile('^Faction Status:$')
    _re_section_errors = re.compile('^Errors during turn:$')
    _re_section_battles = re.compile('^Battles during turn:')
    _re_section_events = re.compile('^Events during turn:$')
    _re_section_orders = re.compile('^Orders Template')
        
    # Instance attributes
    _consumer = None
    _section = _START

    def __init__(self, consumer):
        """Parser initializer.
        
        Its only parameter is the consumer (must implement
        :class:`ReportConsumer` interface) of the parsed report.
        
        Parameter:
            consumer
                :class:`ReportConsumer` instance to which parsed
                elements will be sent.
                  
        """
        self._consumer = consumer
        self._section = ReportParser._START

    def parse(self, f):
        """Read a report from an open file and parse it.
        
        This method uses a :class:`ReportReader` instance to read from
        an open file. The :class:`ReportReader` joins back wrapped
        lines, and then the rebuild lines are passed to
        :meth:`ReportParser.line` until the file ends.
        
        This method returns False if the file has been read to the end,
        and True if orders template have been found and the file has
        still to be parsed by an :class:`OrdersParser` before the end
        is reached. 
        
        Parameter:
            f
                Open file instance to be read.
        
        Returns:
            *False* if the file has been completely read (no template
            orders where found), and *True* if there're still lines for
            reading (template orders). 
        
        """
        self._section = ReportParser._START
        reader = ReportReader(f)

        for l in reader:
            if l.strip():
                self.parse_line(l.rstrip())
            if self._section == ReportParser._ORDERS_TEMPLATE:
                return True
        else:
            return False

    def parse_line(self, line):
        """Parse a report line.
        
        Read line is always sent to the consumer before stripping
        them from its comments. Then line comments are removed and
        the line parsed depending on the section of the report being
        read and the results sent to the consumer.
        
        While reading lines current read report section is stored into
        an internal variable. So parse_line method has also the side
        effect of updating section information. This is important
        because parsing depends on which section is being read, so
        if lines parsed in wrong order some entity types won't be
        matched.
        
        If you plan to do so it will be better using the
        parse_<entity_type> methods.
        
        Parameter:
            line
                Line being parsed.
        
        """
        self._consumer.line(line)
        if not re.match(ReportParser._re_str_region_weather, line):
            l = line.split(';')[0]
        else:
            l = line
        
        if self._section == ReportParser._START:
            if ReportParser._re_section_skill.match(l):
                self._section = ReportParser._GM_REPORT_SKILLS
            elif ReportParser._re_section_report.match(l):
                self._section = ReportParser._REPORT_FACTION
        elif self._section == ReportParser._GM_REPORT_SKILLS:
            if ReportParser._re_section_item.match(l):
                self._section = ReportParser._GM_REPORT_ITEMS
            else:
                self.parse_skill(l)
        elif self._section == ReportParser._GM_REPORT_ITEMS:
            if ReportParser._re_section_object.match(l):
                self._section = ReportParser._GM_REPORT_OBJECTS
            else:
                self.parse_item(l)
        elif self._section == ReportParser._GM_REPORT_OBJECTS:
            if re.match(ReportParser._re_str_region_shortprint, l):
                self._section = ReportParser._GM_REPORT_REGIONS
                self.parse_region(l)
            else:
                self.parse_structure(l)
        elif self._section == ReportParser._GM_REPORT_REGIONS:
            self.parse_region(l)
        elif self._section == ReportParser._REPORT_FACTION:
            if ReportParser._re_section_errors.match(l):
                self._section = ReportParser._REPORT_ERRORS
            elif ReportParser._re_section_battles.match(l):
                self._section = ReportParser._REPORT_BATTLES
            elif ReportParser._re_section_events.match(l):
                self._section = ReportParser._REPORT_EVENTS
            elif ReportParser._re_section_skill.match(l):
                self._section = ReportParser._REPORT_SKILLS
            elif ReportParser._re_section_item.match(l):
                self._section = ReportParser._REPORT_ITEMS
            elif ReportParser._re_section_object.match(l):
                self._section = ReportParser._REPORT_OBJECTS
            elif re.match(ReportParser._re_str_faction_attitudes, l):
                self._section = ReportParser._REPORT_ATTITUDES
                self.parse_faction(l)
            else:
                self.parse_faction(l)
        elif self._section == ReportParser._REPORT_ERRORS:
            if ReportParser._re_section_battles.match(l):
                self._section = ReportParser._REPORT_BATTLES
            elif ReportParser._re_section_events.match(l):
                self._section = ReportParser._REPORT_EVENTS
            elif ReportParser._re_section_skill.match(l):
                self._section = ReportParser._REPORT_SKILLS
            elif ReportParser._re_section_item.match(l):
                self._section = ReportParser._REPORT_ITEMS
            elif ReportParser._re_section_object.match(l):
                self._section = ReportParser._REPORT_OBJECTS
            elif re.match(ReportParser._re_str_faction_attitudes, l):
                self._section = ReportParser._REPORT_ATTITUDES
                self.parse_faction(l)
            else:
                self.parse_event('error', l)
        elif self._section == ReportParser._REPORT_BATTLES:
            if ReportParser._re_section_events.match(l):
                self._section = ReportParser._REPORT_EVENTS
            elif ReportParser._re_section_skill.match(l):
                self._section = ReportParser._REPORT_SKILLS
            elif ReportParser._re_section_item.match(l):
                self._section = ReportParser._REPORT_ITEMS
            elif ReportParser._re_section_object.match(l):
                self._section = ReportParser._REPORT_OBJECTS
            elif re.match(ReportParser._re_str_faction_attitudes, l):
                self._section = ReportParser._REPORT_ATTITUDES
                self.parse_faction(l)
            else:
                self.parse_battle(l)
        elif self._section == ReportParser._REPORT_EVENTS:
            if ReportParser._re_section_skill.match(l):
                self._section = ReportParser._REPORT_SKILLS
            elif ReportParser._re_section_item.match(l):
                self._section = ReportParser._REPORT_ITEMS
            elif ReportParser._re_section_object.match(l):
                self._section = ReportParser._REPORT_OBJECTS
            elif re.match(ReportParser._re_str_faction_attitudes, l):
                self._section = ReportParser._REPORT_ATTITUDES
                self.parse_faction(l)
            else:
                self.parse_event('event', l)
        elif self._section == ReportParser._REPORT_SKILLS:
            if ReportParser._re_section_item.match(l):
                self._section = ReportParser._REPORT_ITEMS
            elif ReportParser._re_section_object.match(l):
                self._section = ReportParser._REPORT_OBJECTS
            elif re.match(ReportParser._re_str_faction_attitudes, l):
                self._section = ReportParser._REPORT_ATTITUDES
                self.parse_faction(l)
            else:
                self.parse_skill(l)
        elif self._section == ReportParser._REPORT_ITEMS:
            if ReportParser._re_section_object.match(l):
                self._section = ReportParser._REPORT_OBJECTS
            elif re.match(ReportParser._re_str_faction_attitudes, l):
                self._section = ReportParser._REPORT_ATTITUDES
                self.parse_faction(l)
            else:
                self.parse_item(l)
        elif self._section == ReportParser._REPORT_OBJECTS:
            if re.match(ReportParser._re_str_faction_attitudes, l):
                self._section = ReportParser._REPORT_ATTITUDES
                self.parse_faction(l)
            else:
                self.parse_item(l)
        elif self._section == ReportParser._REPORT_ATTITUDES:
            self.parse_faction(l)
            if re.match(ReportParser._re_str_faction_unclaimed, l):
                self._section = ReportParser._REPORT_REGIONS
        elif self._section == ReportParser._REPORT_REGIONS:
            if ReportParser._re_section_orders.match(l):
                self._section = ReportParser._ORDERS_TEMPLATE
            else:
                self.parse_region(l)
        elif self._section == ReportParser._ORDERS_TEMPLATE:
            pass

    def parse_battle(self, l):
        """Parse battle report lines.
        
        This method parses battle report lines, begining from the
        start line::
        
            Fulano (123) attacks Mengano (321) in plain (19, 19) in
            Region.
        
        to the spoils, calling the following ReportConsumer methods:
        :meth:`battle`, :meth:`battle_side`,
        :meth:`battle_side_unit`, :meth:`battle_round`,
        :meth:`battle_round_shield`, :meth:`battle_round_special`,
        :meth:`battle_round_regenerate`, :meth:`battle_loses`,
        :meth:`battle_end`, :meth:`battle_casualties`,
        :meth:`battle_casualties_heal`,
        :meth:`battle_casualties_units`, :meth:`battle_spoils` and
        :meth:`battle_raise`.
        
        Parsing of a battle works following these phases::
        
            Fulano (123) attacks Mengano (321) in plain (19, 19) in
              Region
            
        or::
        
            Fulano (123) attempts to assassinate
            
        When such a line is found, battle method is call, signaling
        the consumer than a new battle has begun (and the previous
        one has finished).
        
        Then sides description follows::
        
            Attackers:
            Fulano (123), 2 vikings [VIKI], combat 1.
            Peasants (127), 2 plainsmen [PLAI], behind.
            ...
            
            Defenders:
            Mengano (321), 1 leader [LEAD], 1 sword [SWOR].
            ...
        
        When these lines are found two methods are called:
            battle_side
                when the **Attackers** or **Defenders** item is found,
                signaling the consumer that the list of units for that
                side follows.
            battle_side_unit
                for each unit read
        
        Then one or more battle round follows, with a starting line
        with the number of the round, and then a very short report of
        what happend this round (only shields casting, special effects,
        regeneration/damage for monsters with more than one hit and
        total loses are reported). Something like::
        
            Round 1:
            Mage eart (397) casts Force Shield.
            Other mage (314) strikes fear into enemy mounts, causing 8
              mounts to panic.
            Big monster (666) takes 8 hits bringing it to 252/300.
            City Guard (67) loses 13.
            
        The following consumer methods are called:
            battle_round
                ``Round 1:``
            battle_round_shield
                ``Mage eart (397) casts Force Shield``
            battle_round_special
                ``Other mage (314) strikes fear into ...``
            battle_round_regenerate
                ``Big monster (666) takes 8 hits ...``
            battle_loses
                ``City Guard (67) loses 13``
        
        When one of the sides is broken, it is reported that way::
        
            Mengano (321) is routed!
            Fulano (123) gets a free round of attacks
        
        And a last round is played. Called methods are:
            battle_end
                with the result of the battle.
            and all previous listed round methods.
        
        Once battle is finished, loses and healing are written for
        each side. First loses from the losing side, then heal and
        loses from the winning side::
        
            Total casualites:
            
            Mengano (321) loses 113.
            Damaged units: 321, 126, ...
            
            Fulano (123) heals 14.
            Fulano (123) loses 23.
            Damaged units: 123, 147, 193, 300, ...
        
        The following consumer methods are called:
            battle_casualties
                The starting line, signaling the consumer that
                casualties follow.
            battle_casualties_heal
                Healing line.
            battle_loses
                Loses line.
            battle_casualties_units
                Damaged unit list.
        
        Finally spoils and raised undead follows::
        
            Spoils: sword [SWOR], 12 silver [SILV]
            2 skeletons [SKEL] rise from the grave ...
        
        For these two lines the following methods are called:
            battle_spoils
                Spoils line.
            battle_raise
                Undead raise lines.
        
        """
        
        # Battle start line
        result = re.match(ReportParser._re_str_battle_start, l)
        if result:
            params = {'att': {'name': result.group('attname'),
                              'num': int(result.group('attnum'))},
                      'tar': {'name': result.group('tarname'),
                              'num': int(result.group('tarnum'))},
                      'reg': {'type': result.group('type'),
                              'name': result.group('name'),
                              'xloc': int(result.group('xloc')),
                              'yloc': int(result.group('yloc'))}}
            if result.group('zloc'):
                params['reg']['zloc'] = result.group('zloc')
            if result.group('ass').startswith('attemps'):
                params['ass'] = True
            self._consumer.battle(**params)
            return
        
        # Battle assassination
        result = re.match(ReportParser._re_str_battle_assassination, l)
        if result:
            params = {'tar': {'name': result.group('tarname'),
                              'num': int(result.group('tarnum'))},
                      'reg': {'type': result.group('type'),
                              'name': result.group('name'),
                              'xloc': int(result.group('xloc')),
                              'yloc': int(result.group('yloc'))}}
            if result.group('zloc'):
                params['reg']['zloc'] = result.group('zloc')
            params['ass'] = True
            self._consumer.battle(**params)
            return
             
        # Side marker
        result = re.match(ReportParser._re_str_battle_side, l)
        if result:
            self._consumer.battle_side(side=result.group('side').lower())
            return
        
        # Battle unit
        result = re.match(ReportParser._re_str_battle_unit, l)
        if result:
            params = {'num': int(result.group('num')),
                      'name': result.group('name')}
            if result.group('facname'):
                params['faction'] = {'num': int(result.group('facnum')),
                                     'name': result.group('facname')}
            if 'behind' in result.groupdict() and result.group('behind'):
                params['behind'] = True
            items_n_skills = result.group('list').strip()
            items_list = []
            skills_list = []
            for ins in re.split(', (?![^\(]+\))', items_n_skills):
                # If it's an item
                result = re.match(ReportParser._re_str_battle_unit_item, ins)
                if result:
                    itdict = {'abr': result.group('abr')}
                    if result.group('amt'):
                        itdict['amt'] = int(result.group('amt'))
                        itdict['names'] = result.group('name')
                    else:
                        itdict['amt'] = 1
                        itdict['name'] = result.group('name')
                    if result.group('attackLevel'):
                        mondict = {'attackLevel': \
                                   int(result.group('attackLevel')),
                                   'defense': int(result.group('defense')),
                                   'numAttacks': \
                                   int(result.group('numAttacks')),
                                   'hits': int(result.group('hits')),
                                   'tactics': int(result.group('tactics'))}
                        itdict['monster'] = mondict
                    items_list.append(itdict)
                    continue
                result = re.match(ReportParser._re_str_battle_unit_skill, ins)
                if result:
                    skills_list.append({'name': result.group('name'),
                                        'level': int(result.group('level'))})
                    continue
            else:
                if items_list:
                    params['items'] = items_list
                if skills_list:
                    params['skills'] = skills_list
            
            self._consumer.battle_side_unit(**params)
            return
        
        # Battle free round
        result = re.match(ReportParser._re_str_battle_round_free, l)
        if result:
            params = {'unit':{'num': int(result.group('num')),
                              'name': result.group('name')},
                      'num': 'free'}
            self._consumer.battle_round(**params)
            return
        
        # Battle normal round
        result = re.match(ReportParser._re_str_battle_round_normal, l)
        if result:
            self._consumer.battle_round(num=int(result.group('round')))
            return
        
        # Battle round -> 1. cast shields
        result = re.match(ReportParser._re_str_battle_round_shield, l)
        if result:
            params = {'unit': {'num': int(result.group('num')),
                               'name': result.group('name')},
                      'shielddesc': result.group('shielddesc')}
            self._consumer.battle_round_shield(**params)
            return
        
        # Battle round -> 2. special, deflected
        result = re.match(ReportParser._re_str_battle_round_special_deflected,
                          l)
        if result:
            params = {'unit': {'num': int(result.group('num')),
                               'name': result.group('name')},
                      'spelldesc': result.group('spelldesc'),
                      'deflected': True}
            self._consumer.battle_round_special(**params)
            return
        
        # Battle round -> 3. special, hit
        result = re.match(ReportParser._re_str_battle_round_special, l)
        if result:
            params = {'unit': {'num': int(result.group('num')),
                               'name': result.group('name')},
                      'spelldesc': result.group('spelldesc').strip(),
                      'spelldesc2': result.group('spelldesc2').strip(),
                      'tot': int(result.group('tot')),
                      'spelltarget': result.group('spelltarget').strip()}
            self._consumer.battle_round_special(**params)
            return
        
        # Battle round -> 4. regenerate
        result = re.match(ReportParser._re_str_battle_round_regenerate, l)
        if result:
            params = {'unit': {'num': int(result.group('num')),
                               'name': result.group('name')},
                      'regenerate': result.group('regenerate'),
                      'hits': int(result.group('hits')),
                      'maxhits': int(result.group('maxhits'))}
            if result.group('damage') == 'no':
                params['damage'] = 0
            else:
                params['damage'] = int(result.group('damage'))
            self._consumer.battle_round_regenerate(**params)
            return
        
        # Battle round -> 5. loses
        result = re.match(ReportParser._re_str_battle_round_loses, l)
        if result:
            params = {'unit': {'num': int(result.group('num')),
                               'name': result.group('name')},
                      'loses': int(result.group('loses'))}
            self._consumer.battle_loses(**params)
            return
        
        # Battle ends
        result = re.match(ReportParser._re_str_battle_end, l)
        if result:
            params = {'unit': {'num': int(result.group('num')),
                               'name': result.group('name')},
                      'result': result.group('result')}
            self._consumer.battle_end(**params)
            return
        elif re.match(ReportParser._re_str_battle_end_tie, l):
            self._consumer.battle_end(result='tie')
            return
        
        # Battle casualties
        if re.match(ReportParser._re_str_battle_casualties, l):
            self._consumer.battle_casualties()
            return
        
        # Casualties heal
        result = re.match(ReportParser._re_str_battle_casualties_heal, l)
        if result:
            params = {'unit': {'num': int(result.group('num')),
                               'name': result.group('name')},
                      'heal': int(result.group('heal'))}
            self._consumer.battle_casualties_heal(**params)
            return
        
        # Damaged units
        result = re.match(ReportParser._re_str_battle_casualties_units, l)
        if result:
            units = [{'num': int(u)} for u in result.group('units').split(', ')]
            self._consumer.battle_casualties_units(units=units)
            return
        
        # Spoils
        result = re.match(ReportParser._re_str_battle_spoils, l)
        if result:
            if result.group('spoils') != 'none':
                spoils = []
                for it in result.group('spoils').split(', '):
                    spoils.append(ReportParser._parse_item_str(it))
                else:
                    self._consumer.battle_spoils(items=spoils)
            return
        
        # Raised undead
        result = re.match(ReportParser._re_str_battle_undead_raise, l)
        if result:
            undead = []
            params = {'undead': undead}
            if result.group('name'):
                params['unit'] = {'name': result.group('name'),
                                  'num': int(result.group('num'))}
            for it in result.group('units').split(' and '):
                undead.append(ReportParser._parse_item_str(it))
            self._consumer.battle_raise(**params)


    def parse_faction(self, l):
        """Parse faction info.
        
        Parses faction level information. This faction info is at the
        very beginning of the report, before the listing of regions
        and units begins, and include data as faction type, attitudes,
        unclaimed and so on.
        
        Read :class:`ReportConsumer` documentation for further details.
        
        Parameter:
            l
                Line to be parsed.
        
        """
        result = re.match(ReportParser._re_str_faction_str, l)
        if result:
            params = {'name': result.group('name'),
                      'num': int(result.group('num'))}
            if result.group('type') not in ('Unlimited', 'Normal', 'none'):
                params['factype'] = dict()
                for tv in result.group('type').split(', '):
                    t, v = tv.split(' ')
                    params['factype'][t.lower()] = int(v)
            self._consumer.faction(**params)
            return
        
        result = re.match(ReportParser._re_str_faction_date, l)
        if result:
            params = {'month': result.group('month'),
                      'year': int(result.group('year'))}
            self._consumer.faction_date(**params)
            return
        
        result = re.match(ReportParser._re_str_atlantis_version, l)
        if result:
            self._consumer.atlantis_version(version=result.group('version'))
            return
        
        result = re.match(ReportParser._re_str_atlantis_rules, l)
        if result:
            self._consumer.atlantis_rules(**result.groupdict())
            return
        
        result = re.match(ReportParser._re_str_faction_notimes, l)
        if result:
            self._consumer.faction_warn(notimes=True)
            return
        
        result = re.match(ReportParser._re_str_faction_nopassword, l)
        if result:
            self._consumer.faction_warn(nopassword=True)
            return
        
        result = re.match(ReportParser._re_str_faction_inactive, l)
        if result:
            self._consumer.faction_warn(inactive=int(result.group('turns')))
            return
        
        result = re.match(ReportParser._re_str_faction_quit_restart, l)
        if result:
            self._consumer.faction_warn(quitgame='restart')
            return
        
        result = re.match(ReportParser._re_str_faction_quit_gameover, l)
        if result:
            self._consumer.faction_warn(quitgame='gameover')
            return
        
        result = re.match(ReportParser._re_str_faction_quit_won, l)
        if result:
            self._consumer.faction_warn(quitgame='won')
            return
        
        result = re.match(ReportParser._re_str_faction_quit_eliminated, l)
        if result:
            self._consumer.faction_warn(quitgame='eliminated')
            return
        
        result = re.match(ReportParser._re_str_faction_status, l)
        if result:
            what = result.group('what')
            num = int(result.group('num'))
            allowed = int(result.group('allowed'))
            self._consumer.faction_status(what=what, num=num, allowed=allowed)
            return
        
        result = re.match(ReportParser._re_str_faction_attitudes_default, l)
        if result:
            self._consumer.faction_attitudes(default=\
                    result.group('defaultattitude').lower())
            return
        
        result = re.match(ReportParser._re_str_faction_attitudes, l)
        if result:
            flist = []
            params = {result.group('attitude').lower(): flist}
            for f in result.group('factions').split(', '):
                result = re.match(r'(?P<name>[^(]+) \((?P<num>\d+)\)', f)
                if not result:
                    continue
                flist.append({'num': int(result.group('num')),
                              'name': result.group('name')})
            self._consumer.faction_attitudes(**params)
            return
        
        result = re.match(ReportParser._re_str_faction_unclaimed, l)
        if result:
            self._consumer.faction_unclaimed(
                    unclaimed=int(result.group('unclaimed')))
            return

    def parse_event(self, message_type, line):
        """Parse event or error message.
        
        Parameters:
            message_type
                **event** or **error**.
            line
                line to be parsed.
        
        """
        result = re.match(ReportParser._re_str_unit_error, line)
        if result:
            self._consumer.faction_event(message_type=message_type,
                                         message=result.group('message'),
                                         unit={'name': result.group('name'),
                                               'num': int(result.group('num'))})
        else:
            self._consumer.faction_event(message_type=message_type,
                                         message=line)
    
    def parse_skill(self, l):
        """Parses a skill description.
        
        Skills are described at the very beginning of the report,
        because the skill have just been studied or the player has
        issued a *show* order.
        
        For every skill found :meth:`~ReportConsumer.skill` is
        called. See :class:`ReportConsumer`documentation for further
        details.
        
        Parameter:
            l
                Line to be parsed
                
        """
        
        result = re.match(ReportParser._re_str_skill_line, l)
        # Empty lines
        if not result:
            return
        params = result.groupdict()
        params['level'] = int(params['level'])
        descr = result.group('descr')
        
        # Look from behind to the front for strings
        # No report
        if re.match(ReportParser._re_str_skill_no_report, descr):
            self._consumer.skill(**params)
            return
        
        # No improve by experience
        result = re.match('(?P<descr>.*)' + ReportParser._re_str_skill_no_exp,
                          descr)
        if result:
            descr = result.group('descr').rstrip()
            params['noexp'] = True
            
        # Cannot be teached
        result = re.match('(?P<descr>.*)' + ReportParser._re_str_skill_no_teach,
                          descr)
        if result:
            descr = result.group('descr').rstrip()
            params['noteach'] = True
        
        # Cannot be studied    
        result = re.match('(?P<descr>.*)' + ReportParser._re_str_skill_no_study,
                          descr)
        if result:
            descr = result.group('descr').rstrip()
            params['nostudy'] = True

        # Is it slow?
        result = re.match('(?P<descr>.*)' + \
                          ReportParser._re_str_skill_slow_study, descr)
        if result:
            descr = result.group('descr').rstrip()
            params['slowstudy'] = True

        # Cost of studying the skill
        result = re.match('(?P<descr>.*)' + ReportParser._re_str_skill_cost,
                          descr)
        if result:
            descr = result.group('descr').rstrip()
            params['cost'] = int(result.group('cost'))

        # This skills depends on
        result = re.match('(?P<descr>.*)' + ReportParser._re_str_skill_depends,
                          descr)
        if result:
            descr = result.group('descr').rstrip()
            params['depends'] = []
            for sk in re.split(r', | and ', result.group('depends')):
                result = re.match(ReportParser._re_str_skill_str_level, sk)
                if result:
                    params['depends'].append(result.groupdict())
                    params['depends'][-1]['level'] = int(result.group('level'))
        
        # Objects that can be built
        result = re.match('(?P<descr>.*)' + ReportParser._re_str_skill_builds,
                          descr)
        if result:
            descr = result.group('descr').rstrip()
            params['builds'] = []
            for obj in re.split(r'(?:, | or )(?=an?)', result.group('builds')):
                result = re.match(ReportParser._re_str_object_cost, obj)
                if result:
                    objdict = {'name': result.group('name'),
                               'cost': int(result.group('cost')),
                               'item': []}
                    params['builds'].append(objdict)
                    for it in re.split(' or ', result.group('items')):
                        res = re.match(ReportParser._re_str_item_str, it)
                        if res:
                            objdict['item'].append(res.groupdict())
        
        # Magic production can be described more than once    
        result = re.match(r'(?P<descr>.*)(?:' +
                          ReportParser._re_str_skill_magic_production + r')' +
                          r'(?P<magic_production>.*\.)', descr)
        if result:
            pItems = []
            production = {'command': 'cast',
                          'items': pItems}
            params['mProduction'] = production
            params['cast'] = True
        while result:
            descr = result.group('descr').rstrip()
            production_descr = result.group('magic_production')
            if production_descr.startswith('has a'):
                result = re.match(
                        ReportParser._re_str_skill_magic_production_100,
                        production_descr)
            else:
                result = re.match(ReportParser._re_str_skill_magic_production_1,
                                  production_descr)
            if result:
                mItem = dict()
                pItems.append(mItem)
                mItem['abr'] = result.group('abr')
                if production_descr.startswith('has a'):
                    mItem['name'] = result.group('name')
                    mItem['mOut'] = int(result.group('mOut'))
                else:
                    mItem['names'] = result.group('names')
                    if result.group('mOut'):
                        mItem['mOut'] = int(result.group('mOut')) * 100
                    else:
                        mItem['mOut'] = 100
                if result.group('mInput'):
                    mItem['mInput'] = []
                    for it in re.split(r', | and ', result.group('mInput')):
                        mItem['mInput'].append(ReportParser._parse_item_str(it))
                    
                
            # Try to match another magic produced item
            result = re.match(r'(?P<descr>.*)(?:' +
                              ReportParser._re_str_skill_magic_production + \
                              r')(?P<magic_production>.*\.)', descr)
            
        # Advanced products that can be discovered
        result = re.match(r'(?P<descr>.*)' + \
                          ReportParser._re_str_skill_production_discover,
                          descr)
        if result:
            descr = result.group('descr').rstrip()
            params['discovers'] = [{'names': i} for i in \
                                   re.split(r', | and ', result.group('items'))]
        
        # Normal production
        result = re.match(r'(?P<descr>.*)' + \
                          ReportParser._re_str_skill_production, descr)
        if result:
            descr = result.group('descr').rstrip()
            pItems = []
            production = {'command': result.group('command').lower(),
                          'items': pItems}
            params['production'] = production 
            if production['command'] == 'produce':
                for it in re.split(r'(?<=man\-month)s?(?:,? and |, )',
                                   result.group('production')):
                    result = re.match(
                            ReportParser._re_str_skill_production_produce, it)
                    if result:
                        itemdict = {
                            'abr': result.group('abr'),
                            'names': result.group('names'),
                            'pOut': int(result.group('pOut'))}
                        if result.group('skillout'):
                            itemdict['skillout'] = True
                        if result.group('pInput'):
                            if result.group('orinputs'):
                                itemdict['orinputs'] = True
                            itemdict['pInput'] = []
                            for i in re.split(', | and ',
                                              result.group('pInput')):
                                itemdict['pInput'].append(
                                        ReportParser._parse_item_str(i))
                        if result.group('pMonths'):
                            itemdict['pMonths'] = int(
                                    result.group('pMonths'))
                        else:
                            itemdict['pMonths'] = 1
                        pItems.append(itemdict)
            else:
                # Shipbuilding
                for shp in re.split(r'(?:,? and |, )(?=[^]]+\] from)',
                                    result.group('production')):
                    result = re.match(
                            ReportParser._re_str_skill_production_build, shp)
                    if result:
                        itemdict = {'abr': result.group('abr'),
                                    'names': result.group('names')}
                        if result.group('skillout'):
                            itemdict['skillout'] = True
                        if result.group('pInput'):
                            if result.group('orinputs'):
                                itemdict['orinputs'] = True
                            itemdict['pInput'] = []
                            for i in re.split(', | and ',
                                              result.group('pInput')):
                                itdict = ReportParser._parse_item_str(i)
                                itemdict['pMonths'] = itdict['amt']
                                itemdict['pInput'].append(itdict)
                        pItems.append(itemdict)
        
        # Combat spell
        result = re.match(r'(?P<descr>.*)' + \
                          ReportParser._re_str_skill_combat_spell, descr)
        if result:
            descr = result.group('descr').rstrip()
            params['combat'] = True
            special = result.group('special').strip()
            params['specialstr'] = special
            params['special'] = ReportParser._parse_special(special)
            
        # Cast
        if re.search(r'\bCAST\b', descr):
            params['cast'] = True
            
        # Foundational magic skill
        if re.match(ReportParser._re_str_skill_fundation, descr):
            params['foundation'] = True
            
        # Apprentice skill
        if re.match(ReportParser._re_str_skill_apprentice, descr):
            params['apprentice'] = True
        
        # Basic skill description remains
        if descr:
            params['skilldescr'] = descr
            
        self._consumer.skill(**params)

    def parse_item(self, line):
        """Parses an item description.
        
        As with skills, item descriptions appear at the very beginning
        of the report when they're first discovered or when the player
        issues a show order.
        
        When found, :meth:`ReportConsumer.item` is called. See
        :class:`ReportConsumer` documentation for further details.
        
        Parameter:
            line
                Line to be parsed.
        
        """
        if re.match(ReportParser._re_str_item_line + '.*, weight', line):
            self._consumer.item(**ReportParser._parse_item_item(line))
        elif re.match(ReportParser._re_str_item_line + '.*ship', line):
            self._consumer.item(**ReportParser._parse_item_ship(line))
        else:
            return
        
    def parse_structure(self, l):
        """Parse an object description line.
        
        As with skills and items, structure descriptions appear at the
        very beginning of the report when they're first discovered or
        when the player issues a show order.
        
        When found, :meth:`ReportConsumer.structure`is called. See
        :class:`Reportconsumer` documentation for further details.
        
        Parameter:
            l
                Line to be parsed.
        
        """
        
        result = re.match(ReportParser._re_str_object + r'(?P<extra>.*)', l)
        if not result:
            return
        extra = result.group('extra').strip()
        params = {'name': result.group('name'),
                  'structuretype': result.group('type')}
        if 'monster' in result.groupdict().keys() and result.group('monster'):
            params['monster'] = True
            if 'nomonstergrowth' in result.groupdict().keys() and \
                    result.group('nomonstergrowth'):
                params['nomonstergrowth'] = True
        if 'canenter' in result.groupdict().keys() and result.group('canenter'):
            params['canenter'] = True
        if result.group('protect'):
            params['protect'] = int(result.group('protect'))
        if result.group('bonus'):
            bonus = result.group('bonus')
            params['defense'] = dict()
            for b in re.split(', | and ', bonus):
                rb = re.match(r'(?P<def>\d+) against (?P<type>.+) attacks', b)
                if rb:
                    params['defense'][rb.group('type')] = int(rb.group('def'))
        
        # Special
        result = re.match(ReportParser._re_str_object_special + \
                          r'(?P<extra>.*)', extra)
        if result:
            params['specials'] = []
        while result:
            extra = result.group('extra').strip()
            sdict = {'specialname': result.group('specialname')}
            params['specials'].append(sdict)
            if 'not' in result.groupdict().keys() and result.group('not'):
                sdict['affected'] = False
            else:
                sdict['affected'] = True
            result = re.match(ReportParser._re_str_object_special + \
                              r'(?P<extra>.*)', extra)
        
        # Ship
        result = re.match(ReportParser._re_str_object_ship + \
                          r'(?P<extra>.*)', extra)
        if result:
            extra = result.group('extra').strip()
            params['sailors'] = int(result.group('sailors'))
        
        # Mages
        result = re.match(ReportParser._re_str_object_mages + \
                          r'(?P<extra>.*)', extra)
        if result:
            extra = result.group('extra').strip()
            if result.group('maxMages'):
                params['maxMages'] = int(result.group('maxMages'))
            else:
                params['maxMages'] = 1
        
        # No buildable
        result = re.match(ReportParser._re_str_object_nobuildable + \
                          r'(?P<extra>.*)', extra)
        if result:
            extra = result.group('extra').strip()
            params['nobuildable'] = True
            
        # Production aid
        result = re.match(ReportParser._re_str_object_productionAided + \
                          r'(?P<extra>.*)', extra)
        if result:
            extra = result.group('extra').strip()
            params['productionAided'] = result.group('names')
        
        # Never decay
        result = re.match(ReportParser._re_str_object_neverdecay + \
                          r'(?P<extra>.*)', extra)
        if result:
            extra = result.group('extra').strip()
            params['neverdecay'] = True
            
        # Decay
        result = re.match(ReportParser._re_str_object_decay, extra)
        if result:
            params['maxMaintenance'] = int(result.group('maxMaintenance'))
            params['maxMonthlyDecay'] = int(result.group('maxMonthlyDecay'))
            if result.group('item'):
                params['maintFactor'] = int(result.group('maintFactor'))
                params['maintItem'] = int(result.group('item'))
        
        self._consumer.structure(**params)
    
    def parse_region(self, l):
        """Parses a region"""
        # First region line
        result = re.match(ReportParser._re_str_region_id_line, l)
        if result:
            params = {'xloc': int(result.group('xloc')),
                      'yloc': int(result.group('yloc')),
                      'terrain': result.group('type'),
                      'name': result.group('name')}
            if result.group('zloc'):
                params['zloc'] = result.group('zloc')
            if result.group('population'):
                params['population'] = int(result.group('population'))
                params['racenames'] = result.group('racenames')
                params['wealth'] = int(result.group('wealth'))
            if result.group('townname'):
                params['town'] = {'name': result.group('townname'),
                                  'type': result.group('towntype')}
            self._consumer.region(**params)
            return
        
        # Weather
        result = re.match(ReportParser._re_str_region_weather, l)
        if result:
            params = {'weather': result.group('weather'),
                      'nxtweather': result.group('nxtweather')}
            if result.group('weathereffect'):
                if result.group('weathereffect') == 'unnaturally':
                    params['clearskies'] = True
                else:
                    params['blizzard'] = True
            self._consumer.region_weather(**params)
            return
        
        # Wages
        result = re.match(ReportParser._re_str_region_wages, l)
        if result:
            params = {'productivity': float(result.group('productivity'))}
            if result.group('amount'):
                params['amount'] = int(result.group('amount'))
            else:
                params['amount'] = 0
            self._consumer.region_wages(**params)
            return
        
        # Market
        result = re.match(ReportParser._re_str_region_market, l)
        if result and result.group('items') != 'none':
            if result.group('type') == 'Wanted':
                params = {'market': 'sell'}
            else:
                params = {'market': 'buy'}
            items = []
            params['items'] = items
            for it in re.split(', ', result.group('items')):
                item, price = it.split(' at $')
                item = ReportParser._parse_item_str(item)
                item['price'] = int(price)
                items.append(ItemMarket(**item))
            self._consumer.region_market(**params)
            return
        
        # Entertainment
        result = re.match(ReportParser._re_str_region_entertainment, l)
        if result:
            self._consumer.region_entertainment(amount= \
                                                int(result.group('amount')))
            return
            
        # Products
        result = re.match(ReportParser._re_str_region_products, l)
        if result and result.group('products') != 'none':
            pr = []
            for p in result.group('products').split(', '):
                pr.append(ReportParser._parse_item_str(p))
            self._consumer.region_products(products=pr)
            return
            
        # Exits
        result = re.match(ReportParser._re_str_region_exit, l)
        if result:
            params = {'direction': result.group('direction'),
                      'xloc': int(result.group('xloc')),
                      'yloc': int(result.group('yloc')),
                      'terrain': result.group('type'),
                      'name': result.group('name')}
            if result.group('zloc'):
                params['zloc'] = result.group('zloc')
            if result.group('townname'):
                params['town'] = {'name': result.group('townname'),
                                  'type': result.group('towntype')}
            self._consumer.region_exits(**params)
            return
        
        # Gate
        result = re.match(ReportParser._re_str_region_gate, l)
        if result:
            params = dict()
            if result.group('gate'):
                params['gate'] = int(result.group('gate'))
                params['gateopen'] = True
            else:
                params['gate'] = 0
                params['gateopen'] = False
            self._consumer.region_gate(**params)
            return
            
        # Object
        result = re.match(ReportParser._re_str_region_object, l)
        if result:
            params = {'name': result.group('name'),
                      'num': int(result.group('num'))}
            o = result.group('object')
            
            result = re.match(r'(?P<object>.+)' +
                              ReportParser._re_str_region_object_canenter, o)
            if result:
                o = result.group('object').strip()
                params['canenter'] = False
            
            result = re.match(r'(?P<object>.+)' +
                              ReportParser._re_str_region_object_runes, o)
            if result:
                o = result.group('object').strip()
                params['runes'] = True
            
            result = re.match(r'(?P<object>.+)' +
                              ReportParser._re_str_region_object_inner, o)
            if result:
                o = result.group('object').strip()
                params['inner'] = True
            
            result = re.match(r'(?P<object>.+)' +
                              ReportParser._re_str_region_object_maintenance, o)
            if result:
                o = result.group('object').strip()
                params['maintenance'] = True
            
            result = re.match(r'(?P<object>.+)' +
                              ReportParser._re_str_region_object_decay, o)
            if result:
                o = result.group('object').strip()
                params['decay'] = True
            
            result = re.match(r'(?P<object>.+)' +
                              ReportParser._re_str_region_object_incomplete, o)
            if result:
                o = result.group('object').strip()
                params['incomplete'] = int(result.group('incomplete'))
            
            if ',' in o:
                params['ob'], o = o.split(', ', 1)
                params['items'] = []
                for i in o.split(', '):
                    result = re.match('(?P<num>\d+) (?P<name>.+)', i)
                    n = int(result.group('num'))
                    if n == 1:
                        params['items'].append({'num': n,
                                                'name': result.group('name')})
                    else:
                        params['items'].append({'num': n,
                                                'names': result.group('name')})
            else:
                params['ob'] = {'name': o}
            
            self._consumer.region_structure(**params)
            return
            
        # Unit
        result = re.match(ReportParser._re_str_unit, l)
        if result:
            unit = result.group('unit')
            params = {'name': result.group('name'),
                      'num': int(result.group('num'))}
            
            if result.group('tab') == TAB:
                params['tab'] = True
            
            if result.group('factionname'):
                params['faction'] = {'name': result.group('factionname'),
                                     'num': int(result.group('factionnum'))}
                
            att = result.group('attitude')
            if att == '*':
                params['attitude'] = 'me'
            elif att == '=':
                params['attitude'] = 'ally'
            elif att == ':':
                params['attitude'] = 'friendly'
            elif att == '-':
                params['attitude'] = 'neutral'
            elif att == '%':
                params['attitude'] = 'unfriendly'
            elif att == '!':
                params['attitude'] = 'hostile'
                
            # Unit flags
            if result.group('reveal'):
                params['reveal'] = result.group('reveal')
            if result.group('consuming'):
                params['consuming'] = result.group('consuming')
            if result.group('spoils'):
                params['spoils'] = result.group('spoils')
            
            try:
                if result.group('guard'):
                    params['guard'] = 'guard'
            except:
                pass
            try:
                if result.group('avoiding'):
                    params['guard'] = 'avoid'
            except:
                pass
            try:
                if result.group('behind'):
                    params['behind'] = True
            except:
                pass
            try:
                if result.group('holding'):
                    params['holding'] = True
            except:
                pass
            try:
                if result.group('autotax'):
                    params['autotax'] = True
            except:
                pass
            try:
                if result.group('noaid'):
                    params['noaid'] = True
            except:
                pass
            try:
                if result.group('sharing'):
                    params['sharing'] = True
            except:
                pass
            try:
                if result.group('nocross'):
                    params['nocross'] = True
            except:
                pass
            
            # Visited (for quests)
            result = re.match('(?P<unit>.+)' + \
                              ReportParser._re_str_unit_visited, unit)
            if result:
                unit = result.group('unit').strip()
                params['visited'] = [v for v in \
                                     re.split(', | and ',
                                              result.group('visited'))]

            # Can study
            result = re.match('(?P<unit>.+)' + \
                              ReportParser._re_str_unit_canstudy, unit)
            if result:
                unit = result.group('unit').strip()
                params['canstudy'] = []
                for sk in result.group('canstudy').split(', '):
                    result = re.match(ReportParser._re_str_skill_str, sk)
                    params['canstudy'].append({'abbr': result.group('abbr'),
                                               'name': result.group('name')})
                    
            # Ready items
            for r in ('item', 'armor', 'weapon'):
                result = re.match('(?P<unit>.+)\. Ready ' + r + \
                                  r's?: (?P<items>.+)', unit)
                if not result:
                    continue
                unit = result.group('unit').strip()
                params['ready' + r] = []
                for it in result.group('items').split(', '):
                    result = re.match(ReportParser._re_str_item_str, it)
                    params['ready' + r].append(result.groupdict())
            
            # Combat spell
            result = re.match('(?P<unit>.+)' + \
                              ReportParser._re_str_unit_combat_skill, unit)
            if result:
                unit = result.group('unit').strip()
                params['combat'] = {'abbr': result.group('abbr'),
                                    'name': result.group('name')}
            
            # Skills
            result = re.match('(?P<unit>.+)' + \
                              ReportParser._re_str_unit_skills, unit)
            if result:
                unit = result.group('unit').strip()
                if result.group('skills') != 'none':
                    params['skills'] = []
                    for sk in result.group('skills').split(', '):
                        result = re.match(
                                ReportParser._re_str_unit_skills_skill, sk)
                        if not result:
                            continue
                        skilldict = {'abbr': result.group('abbr'),
                                     'name': result.group('name'),
                                     'level': int(result.group('level')),
                                     'days': int(result.group('days'))}
                        if result.group('rate'):
                            skilldict['rate'] = int(result.group('rate'))
                        params['skills'].append(skilldict)
            
            # Capacity
            result = re.match('(?P<unit>.+)' + \
                              ReportParser._re_str_unit_capacity, unit)
            if result:
                unit = result.group('unit').strip()
                params['weight'] = int(result.group('weight'))
                params['capacity'] = dict([(a, int(result.group(a))) \
                                           for a in ('flying',
                                                     'riding',
                                                     'walking',
                                                     'swimming')])
                
            # Items
            unit = unit.strip('. ,')
            params['items'] = []
            for it in unit.split(', '):
                itemdict = dict()
                params['items'].append(itemdict)
                result = re.match(ReportParser._re_str_item_unfinished, it)
                if result:
                    itemdict['unfinished'] = True
                    itemdict['num'] = int(result.group('num'))
                    it = result.group('item')
                result = re.match(ReportParser._re_str_item_illusion, it)
                if result:
                    itemdict['illusion'] = True
                    it = result.group('unit')
                itemdict.update(ReportParser._parse_item_str(it))

            self._consumer.region_unit(**params)
            return
    
    @staticmethod
    def _parse_item_item(line):
        """Parses an usual (ie, not ship) item line.
        
        Parameter:
            line
                Line to be parsed."""
        result = re.match(ReportParser._re_str_item_line + \
                          ReportParser._re_str_item_line_item, line)
        
        # Empty lines
        if not result:
            return
        params = result.groupdict()
        if result.group('illusion'):
            params['illusion'] = True
        else:
            del(params['illusion'])
        params['descr'] = ', weight ' + params['weight'] + params['descr']
        params['weight'] = int(result.group('weight'))
        descr = result.group('descr').rstrip()
        
        # Capacity
        result = re.match(ReportParser._re_str_item_hitchItem + \
                          r'(?P<descr>.*)', descr)
        if result:
            descr = result.group('descr').strip()
            params['hitch'] = {'item': {'abr': result.group('abr'),
                                        'name': result.group('name')},
                               'walk': int(result.group('cap'))}
        
        result = re.match(ReportParser._re_str_item_capacity + \
                          r'(?P<descr>.*)', descr)
        while result:
            descr = result.group('descr').strip()
            if result.group('typeShort'):
                if result.group('typeShort') == 'walk':
                    params['walking'] = 0
                elif result.group('typeShort') == 'ride':
                    params['riding'] = 0
                if result.group('typeShort') == 'swim':
                    params['swimming'] = 0
                if result.group('typeShort') == 'fly':
                    params['flying'] = 0
            else:
                params[result.group('type')] = int(result.group('cap'))
            
            result = re.match(ReportParser._re_str_item_capacity + \
                              r'(?P<descr>.*)', descr)
        
        # Speed
        result = re.match(ReportParser._re_str_item_speed, descr)
        if result:
            params['speed'] = int(result.group('speed'))
        
        # End with the common part of the description
        params.update(ReportParser._parse_item_common(descr))
        return params
            
    @staticmethod
    def _parse_item_ship(l):
        """Parses a ship item line.
        
        Parameter:
            l
                Line to be parsed.
                
        """
        
        result = re.match(ReportParser._re_str_item_line + \
                          ReportParser._re_str_item_ship + r'(?P<descr>.*)', l)
        if not result:
            return
        descr = result.group('descr').strip()
        shipdict = {'sailors': int(result.group('sailors'))}
        params = {'ship': shipdict, 'speed': int(result.group('speed')),
                  'abr': result.group('abr'), 'name': result.group('name')}
        if 'fly' in result.groupdict().keys() and result.group('fly'):
            params['flying'] = int(result.group('cap'))
        else:
            params['swimming'] = int(result.group('cap'))
        
        # Defense
        result = re.match(ReportParser._re_str_item_ship_object + \
                          r'(?P<descr>.*)', descr)
        if result:
            descr = result.group('descr').strip()
            shipdict['protect'] = int(result.group('protect'))
            shipdict['defense'] = dict()
            bonus = result.group('bonus')
            for b in re.split(', | and ', bonus):
                result = re.match(
                        r'(?P<def>\d+) against (?P<type>.+) attacks', b)
                if result:
                    shipdict['defense'][result.group('type')] = \
                            int(result.group('def'))
        
        # Mages
        result = re.match(ReportParser._re_str_item_ship_mages + \
                          r'(?P<descr>.*)', descr)
        if result:
            descr = result.group('descr').strip()
            if result.group('maxMages'):
                shipdict['maxMages'] = int(result.group('maxMages'))
            else:
                shipdict['maxMages'] = 1
        
        # End with the common part of the description
        params.update(ReportParser._parse_item_common(descr))
        return params
    
    @staticmethod
    def _parse_item_common(descr):
        """Parse common part of an item.
        
        This function parses the common part for both normal items and
        ship items.
        
        It's only parameter is the latter part of the item
        description string
        
        It returns a dictionary that should be used to update the
        parsed dictionary until this latter part is reached.
        
        Parameter:
            descr
                Partial item description line.
        
        """
        params = dict()
        
        # Look from behind to the front for strings
        # Max inventory
        result = re.match('(?P<descr>.*)' + \
                          ReportParser._re_str_item_max_inventory, descr)
        if result:
            descr = result.group('descr').rstrip()
            params['max_inventory'] = int(result.group('amt'))
            
        # Can't give
        result = re.match('(?P<descr>.*)' + \
                          ReportParser._re_str_item_cantgive, descr)
        if result:
            descr = result.group('descr').rstrip()
            params['cantgive'] = True 
        
        # Food
        result = re.match('(?P<descr>.*)' + \
                          ReportParser._re_str_item_food, descr)
        if result:
            descr = result.group('descr').rstrip()
            params['food'] = int(result.group('food'))
            
        # Battle item
        result = re.match('(?P<descr>.*)' + \
                          ReportParser._re_str_item_battle, descr)
        if result:
            descr = result.group('descr').rstrip()
            battledict = dict({'specialstr': result.group('special')})
            params['battle'] = battledict
            if result.group('mageonly'):
                battledict['mageonly'] = True
            if result.group('shield') == 'provides':
                battledict['shield'] = True
            
            # Battle item -> special
            special = result.group('special').rstrip()
            battledict['specialstr'] = special
            battledict['special'] = ReportParser._parse_special(special)
        
        # Mage only
        result = re.match('(?P<descr>.*)' + \
                          ReportParser._re_str_item_mageonly, descr)
        if result:
            descr = result.group('descr').rstrip()
            params['mageonly'] = True
        
        # Grant item
        result = re.match('(?P<descr>.*)' + \
                          ReportParser._re_str_item_grant, descr)
        if result:
            descr = result.group('descr').rstrip()
            grantdict = dict({'name': result.group('name'),
                              'maxGrant': int(result.group('maxGrant'))})
            params['grantSkill'] = grantdict
            if result.group('minGrant'):
                grantdict['minGrant'] = int(result.group('minGrant'))
            if result.group('fromSkills'):
                grantdict['fromSkills'] = [{'name': sk} for sk in \
                                            re.split(', | and ',
                                                     result.group('fromSkills'))
                                           ]
            else:
                grantdict['minGrant'] = grantdict['maxGrant']
        
        # Attributes - wind
        result = re.match('(?P<descr>.*)' + \
                          ReportParser._re_str_item_wind, descr)
        if result:
            descr = result.group('descr').rstrip()
            params['wind'] = {'windBoost': int(result.group('windBoost')),
                              'val': int(result.group('val'))}
        
        # Attributes - stealth
        result = re.match('(?P<descr>.*)' + \
                          ReportParser._re_str_item_stealth, descr)
        if result:
            descr = result.group('descr').rstrip()
            params['stealth'] = {'val': int(result.group('val'))}
            try:
                if result.group('perman'):
                    params['stealth']['perman'] = True
            except:
                pass
        
        # Attributes - observation
        result = re.match('(?P<descr>.*)' + \
                          ReportParser._re_str_item_observation, descr)
        if result:
            descr = result.group('descr').rstrip()
            params['observation'] = {'val': int(result.group('val'))}
            try:
                if result.group('perman'):
                    params['observation']['perman'] = True
            except:
                pass
        
        # Money
        result = re.match('(?P<descr>.*)' + \
                          ReportParser._re_str_item_money, descr)
        if result:
            descr = result.group('descr').rstrip()
            params['money'] = True
        
        # Resource
        result = re.match('(?P<descr>.*)' + \
                          ReportParser._re_str_item_resource, descr)
        if result:
            descr = result.group('descr').rstrip()
            params['resource'] = True
            
        # Mount
        result = re.match('(?P<descr>.*)' + \
                          ReportParser._re_str_item_mount, descr)
        if result:
            descr = result.group('descr').rstrip()
            params['mount'] = {'minBonus': int(result.group('minBonus')),
                               'maxBonus': int(result.group('maxBonus'))}
            
            if result.group('skill'):
                rsk = re.match(ReportParser._re_str_skill_str,
                               result.group('skill'))
                if rsk:
                    params['mount']['skill'] = rsk.groupdict()
            elif result.group('skill').startswith('No skill'):
                params['mount']['skill'] = None
            else:
                params['mount']['unridable'] = True
                
            if result.group('maxHamperedBonus'):
                params['mount']['maxHamperedBonus'] = \
                        int(result.group('maxHamperedBonus'))
            
            if result.group('special'):
                params['mount']['specialstr'] = result.group('special')
                params['mount']['special'] = \
                        ReportParser._parse_special(result.group('special'))
                        
        # Trade good
        result = re.match('(?P<descr>.*)' + \
                          ReportParser._re_str_item_trade, descr)
        if result:
            descr = result.group('descr').rstrip()
            if result.group('baseprice'):
                params['trade'] = {'baseprice': int(result.group('baseprice'))}
            else:
                params['trade'] = {'minbuy': int(result.group('minbuy')),
                                   'maxbuy': int(result.group('maxbuy')),
                                   'minsell': int(result.group('minsell')),
                                   'maxsell': int(result.group('maxsell'))}
                        
        # Tool
        result = re.match('(?P<descr>.*)' + \
                          ReportParser._re_str_item_tool, descr)
        if result:
            descr = result.group('descr').rstrip()
            itemlist = []
            params['tool'] = {'items': itemlist}
            for itboost in re.split(',? and |, ', result.group('items')):
                it, val = itboost.split(' by ')
                itdict = {'val': int(val)}
                itemlist.append(itdict)
                if it == 'entertainment':
                    itdict['name'] = it
                else:
                    result = re.match(ReportParser._re_str_item_str, it)
                    if result:
                        itdict.update(result.groupdict())
                        
        # Armor
        result = re.match('(?P<descr>.*)' + \
                          ReportParser._re_str_item_armor, descr)
        if result:
            descr = result.group('descr').rstrip()
            armordict = {'saves': []}
            params['armor'] = armordict
            if result.lastgroup == 'assassinate':
                armordict['useinassassinate'] = True
            for sv in re.split(', and |, ', result.group('saves')):
                result = re.match(ReportParser._re_str_item_armor_saves, sv)
                if not result:
                    continue
                armordict['saves'].append(
                        {'weapClass': result.group('class'),
                         'percent': int(result.group('percent'))})
        
        # Weapon
        result = re.match('(?P<descr>.*)' + \
                          ReportParser._re_str_item_weapon, descr)
        if result:
            descr = result.group('descr').rstrip()
            extra = result.group('extra').strip()
            wdict = {'class': result.group('weapClass'),
                     'attackBonus': 0, 'defenseBonus': 0}
            if result.group('range'):
                wdict['range'] = result.group('range')
            params['weapon'] = wdict
            
            result = re.match(ReportParser._re_str_item_weapon_skill + \
                              r'(?P<extra>.*)', extra)
            if result:
                extra = result.group('extra').strip()
                if result.group('abbr'):
                    wdict['skill'] = {'abbr': result.group('abbr'),
                                      'name': result.group('name')}
            
            result = re.match(ReportParser._re_str_item_weapon_bonus + \
                              r'(?P<extra>.*)', extra)
            while result:
                extra = result.group('extra').strip()
                bonus = int(result.group('bonus'))
                if result.group('type') == 'penalty':
                    bonus *= -1
                try:
                    if result.group('both'):
                        wdict['attackBonus'] = bonus
                        wdict['defenseBonus'] = bonus
                    else:
                        wdict[result.group('when') + 'Bonus'] = bonus
                except:
                    wdict[result.group('when') + 'Bonus'] = bonus
                result = re.match(ReportParser._re_str_item_weapon_bonus + \
                                  r'(?P<extra>.*)', extra)
            
            result = re.match(ReportParser._re_str_item_weapon_mount_bonus + \
                              r'(?P<extra>.*)', extra)
            if result:
                extra = result.group('extra').strip()
                bonus = int(result.group('bonus'))
                if result.group('type') == 'penalty':
                    bonus *= -1
                wdict['mountBonus'] = bonus
            
            result = re.match(ReportParser._re_str_item_weapon_nofoot + \
                              r'(?P<extra>.*)', extra)
            if result:
                extra = result.group('extra').strip()
                if result.group('foot') == 'foot':
                    wdict['nomount'] = True
                else:
                    wdict['nofoot'] = True
            
            result = re.match(ReportParser._re_str_item_weapon_ridingbonus + \
                              r'(?P<extra>.*)', extra)
            if result:
                extra = result.group('extra').strip()
                if result.group('attack'):
                    wdict['ridingbonus'] = True
                else:
                    wdict['ridingbonusdefense'] = True
            
            result = re.match(ReportParser._re_str_item_weapon_nodefense + \
                              r'(?P<extra>.*)', extra)
            if result:
                extra = result.group('extra').strip()
                wdict['nodefense'] = True
            
            result = re.match(\
                    ReportParser._re_str_item_weapon_noattackerskill + \
                    r'(?P<extra>.*)', extra)
            if result:
                extra = result.group('extra').strip()
                wdict['noattackerskill'] = True
            
            result = re.match(ReportParser._re_str_item_weapon_alwaysready + \
                    r'(?P<extra>.*)', extra)
            if result:
                extra = result.group('extra').strip()
                if result.group('ready').startswith('Wielders'):
                    wdict['alwaysready'] = True
            
            result = re.match(ReportParser._re_str_item_weapon_attacktype + \
                              r'(?P<extra>.*)', extra)
            if result:
                extra = result.group('extra').strip()
                wdict['attackType'] = result.group('attackType')
            
            result = re.match(ReportParser._re_str_item_weapon_numattacks + \
                              r'(?P<extra>.*)', extra)
            if result:
                extra = result.group('extra').strip()
                wdict['numAttacks'] = dict()
                if result.group('natts'):
                    wdict['numAttacks']['atts'] = -1*int(result.group('natts'))
                elif result.group('atts'):
                    wdict['numAttacks']['atts'] = int(result.group('atts'))
                else:
                    if result.group('attacksSkill').startswith('half'):
                        wdict['numAttacks']['attacksHalfSkill'] = True
                    else:
                        wdict['numAttacks']['attacksSkill'] = True
                    if result.group('matts'):
                        wdict['numAttacks']['atts'] = int(result.group('matts'))
                    else:
                        wdict['numAttacks']['atts'] = 0
        
        # Monster    
        result = re.match(r'(?P<descr>.*)' + \
                          ReportParser._re_str_item_monster + \
                          r'(?P<extra>.*)', descr)
        if result:
            descr = result.group('descr').rstrip()
            extra = result.group('extra').strip()
            mondict = {'attackLevel': int(result.group('attackLevel'))}
            params['monster'] = mondict
            
            # Defense
            defdict = dict()
            mondict['defense'] = defdict
            result = re.match(ReportParser._re_str_item_monster_resist + \
                              r'(?P<extra>.*)', extra)
            while result:
                extra = result.group('extra').strip()
                if result.group('val'):
                    defdict[result.group('type')] = int(result.group('val'))
                else:
                    defdict[result.group('type')] = result.group('valstr')
                result = re.match(ReportParser._re_str_item_monster_resist + \
                                  r'(?P<extra>.*)', extra)
            
            # Special
            result = re.match(ReportParser._re_str_item_monster_special + \
                              r'(?P<extra>.*)', extra)
            if result:
                extra = result.group('extra').strip()
                special = result.group('special').strip()
                mondict['specialstr'] = special
                mondict['special'] = ReportParser._parse_special(special)
            
            # Stats
            result = re.match(ReportParser._re_str_item_monster_stats + \
                              r'(?P<extra>.*)', extra)
            if result:
                extra = result.group('extra').strip()
                for k in result.groupdict().keys():
                    try:
                        mondict[k] = int(result.group(k))
                    except:
                        pass
            
            # Spoils
            result = re.match(ReportParser._re_str_item_monster_spoils, extra)
            if result:
                mondict['spoils'] = result.group('type')
        
        # Men    
        result = re.match('(?P<descr>.*)' + ReportParser._re_str_item_man + \
                          '(?P<extra>.*)', descr)
        if result:
            descr = result.group('descr').rstrip()
            extra = result.group('extra').strip()
            params['man'] = {'defaultLevel': int(result.group('defaultLevel'))}
            if result.group('specialLevel'):
                params['man']['specialLevel'] = \
                        int(result.group('specialLevel'))
                sklist = []
                params['man']['skills'] = sklist
                for sk in re.split(', | and ', result.group('skills')):
                    result = re.match(ReportParser._re_str_skill_str, sk)
                    if result:
                        sklist.append({'abbr': result.group('abbr'),
                                       'name': result.group('name')})
                    elif sk == 'all magical skills':
                        sklist.append({'abbr': 'MANI',
                                       'name': 'manipulation'})
        
        # Withdraw
        result = re.match('(?P<descr>.*)' + ReportParser._re_str_item_withdraw,
                          descr)
        if result:
            descr = result.group('descr').rstrip()
            params['withdraw'] = int(result.group('price'))
        
        return params
        
    
    @staticmethod
    def _parse_item_str(itemstr):
        """Parse item string
        
        Its only parameter is the item string to be parsed. Returns a
        dictionary with the amount of items, its abreviature and its
        name or names.
        
        Parameter:
            itemstr
                Item string.
        
        """
        result = re.match(ReportParser._re_str_item_amt_str, itemstr)
        if result:
            itdict = result.groupdict()
            if itdict['amt'] == 'unlimited':
                itdict['amt'] = -1
            else:
                itdict['amt'] = int(itdict['amt'])
        else:
            result = re.match(ReportParser._re_str_item_str, itemstr)
            if result:
                itdict = result.groupdict()
                itdict['amt'] = 1
        return itdict
    
    @staticmethod
    def _parse_special(special):
        """Parses the special string of an item or spell.
        
        Parameters:
            special
                The special string to be parsed.
        
        Returns:
            A dictionary with the parsed data.
            
        """
        specialdict = dict()
        result = re.match('(?P<special>.*)' + \
                          ReportParser._re_str_item_special_damage, special)
        # Battle item -> special -> damage
        if result:
            specialdict['damage'] = []
        while result:
            special = result.group('special').rstrip()
            damagedict = {'minnum': int(result.group('minnum')),
                          'maxnum': int(result.group('maxnum')),
                          'type': result.group('type')}
            if result.group('expandLevel'):
                damagedict['expandLevel'] = True
            specialdict['damage'].append(damagedict)
            
            # Battle item -> special -> damage -> effect
            if result.group('effect'):
                damagedict['effectstr'] = result.group('effect')
                effectdict = dict()
                damagedict['effect'] = effectdict
                effect = result.group('effect').rstrip()
                result = re.match(
                        ReportParser._re_str_item_special_damage_effect,
                        effect)
                if result:
                    effectdict['name'] = result.group('name')
                    if result.group('cancelEffect'):
                        effectdict['cancelEffect'] = \
                                result.group('cancelEffect')
                    if result.group('oneshot'):
                        if result.group('oneshot') == 'their next attack':
                            effectdict['oneshot'] = True
                        else:
                            effectdict['oneshot'] = False
                        effectdict['defMods'] = []
                        for mod in re.split(', ', result.group('effect')):
                            result = re.match('(?P<val>.+) to attack', mod)
                            if result:
                                effectdict['attackVal'] = \
                                        int(result.group('val'))
                                continue
                            result = re.match('(?P<val>.+) versus ' \
                                              '(?P<type>.+) attacks', mod)
                            if result:
                                effectdict['defMods'].append(
                                        {'type': result.group('type'),
                                         'val': int(result.group('val'))}
                                )
                else:
                    pass # raise ParseError?
            
            # Reads Battle item -> special -> damage
            result = re.match('(?P<special>.*)' + \
                              ReportParser._re_str_item_special_damage,
                              special)
                
        # Battle item -> special -> defbonus
        result = re.match('(?P<special>.*)' + \
                          ReportParser._re_str_item_special_defbonus,
                          special)
        if result:
            special = result.group('special').rstrip()
            specialdict['defs'] = []
            for defbonus in re.split(', (?:and )?', result.group('defs')):
                result = re.match(
                        ReportParser._re_str_item_special_defbonus_def,
                        defbonus)
                if result:
                    defdict = {'type': result.group('type'),
                               'val': int(result.group('val'))}
                    try:
                        if result.group('expandLevel'):
                            defdict['expandLevel'] = True
                    except:
                        pass
                    specialdict['defs'].append(defdict)
                
        # Battle item -> special -> shield
        result = re.match('(?P<special>.*)' + \
                          ReportParser._re_str_item_special_shield, special)
        if result:
            special = result.group('special').rstrip()
            if result.group('level'):
                specialdict['level'] = int(result.group('level'))
            specialdict['shield'] = [{'type': sh} for sh in \
                                     re.split(', (?:and )?',
                                              result.group('shields'))]
        
        # Battle item -> special -> nobuilding
        result = re.match('(?P<special>.*)' + \
                          ReportParser._re_str_item_special_nobuilding, special)
        if result:
            special = result.group('special').rstrip()
            specialdict['nobuilding'] = True
        
        # Battle item -> special -> nomonster
        result = re.match('(?P<special>.*)' + \
                          ReportParser._re_str_item_special_nomonster, special)
        if result:
            special = result.group('special').rstrip()
            specialdict['nomonster'] = True
        
        # Battle item -> special -> illusion
        result = re.match('(?P<special>.*)' + \
                          ReportParser._re_str_item_special_illusion, special)
        if result:
            special = result.group('special').rstrip()
            specialdict['illusion'] = True
        
        # Battle item -> special -> effectif | effectexcept
        result = re.match('(?P<special>.*)' + \
                          ReportParser._re_str_item_special_effectif, special)
        if result:
            special = result.group('special').rstrip()
            if result.group('effectif') == 'not':
                specialdict['effectexcept'] = True
            else:
                specialdict['effectif'] = True
            specialdict['effects'] = \
                    [{'name': ef} for ef in \
                            re.split(r', (?:or )?',
                                     result.group('effects'))]
        
        # Battle item -> special -> soldierif | soldierexcept
        result = re.match('(?P<special>.*)' + \
                          ReportParser._re_str_item_special_soldierif, special)
        if result:
            special = result.group('special').rstrip()
            if result.group('soldierif') == 'not':
                if result.group('mount'):
                    specialdict['mountexcept'] = True
                else:
                    specialdict['soldierexcept'] = True
            else:
                if result.group('mount'):
                    specialdict['mountif'] = True
                else:
                    specialdict['soldierif'] = True
            specialdict['targets'] = []
            for it in re.split(r', (?:or )?', result.group('items')):
                result = re.match(ReportParser._re_str_item_str, it)
                if result:
                    specialdict['targets'].append(
                            {'names': result.group('name'),
                             'abr': result.group('abr')})
        
        # Battle item -> special -> buildingif
        result = re.match('(?P<special>.*)' + \
                          ReportParser._re_str_item_special_buildingif, special)
        if result:
            special = result.group('special').rstrip()
            if result.group('buildingif') == 'which are inside':
                specialdict['buildingif'] = True
            else:
                specialdict['buildingexcept'] = True
            specialdict['buildings'] = [{'name': bd} for bd in \
                                        re.split(r', (?:or )?',
                                                 result.group('buildings'))]
        
        # Battle item -> special -> name and level
        result = re.match(ReportParser._re_str_item_special_name, special)
        if result:
            specialdict['name'] = result.group('specialname')
            if result.group('level'):
                specialdict['level'] = int(result.group('level'))
        
        return specialdict
    

if __name__ == '__main__':
    g = ReportConsumer()
    with open('report.3') as f:
        parser = ReportParser(g)
        parser.parse(f)
