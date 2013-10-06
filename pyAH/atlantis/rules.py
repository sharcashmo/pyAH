from atlantis import syntaxrules

class GameDefs:
    """\
    This class store game definitions and constants

    The class define appropiate default values for each parameter.
    Constants:

    Faction limit types:
        FACLIM_MAGE_COUNT
        FACLIM_FACTION_TYPES
        FACLIM_UNLIMITED

    Attributes:
        faction_limit_type    Type of faction limits in effect in the\
        game
        faction_points        Max number of faction points\
    """
    FACLIM_MAGE_COUNT, FACLIM_FACTION_TYPES, FACLIM_UNLIMITED = range(3)
    
    faction_limit_type = FACLIM_FACTION_TYPES
    faction_points = 5

class RulesWarning(Warning):
    pass

class RulesError(Exception):
    pass
        
class Rules:
    '''High level class for Game Rules.

    This class keeps track of all game rules and provides handy
    functions to check actions against these rules.

    Attributes:
        game_defs   Game definition constants
        
    '''
    game_defs = None

    def __init__(self):
        '''Creates the Rules object and set values for its attributes'''
        self.game_defs = GameDefs()

    def check_faction_type(self, war = 0, trade = 0, magic = 0):
        '''Checks whether faction type is valid.
        
        If faction types are not used in current game it raises a
        Warning. If assigned faction points exceed allowed max faction
        points it raises an Error.
        
        '''
        syntaxrules.check_unsigned_integer(war=war, trade=trade, magic=magic)

        if self.game_defs.faction_limit_type != \
           GameDefs.FACLIM_FACTION_TYPES:
            raise RulesWarning('no faction types in this game: {0}'.format(self.game_defs.faction_limit_type)) 

        if (sum((war, trade, magic)) > self.game_defs.faction_points):
            raise RulesError('at most {0} faction points are allowed'.
                             format(self.game_defs.faction_points))

if __name__ == '__main__':
    pass
