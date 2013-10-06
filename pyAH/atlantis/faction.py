from . import rules

r = rules.Rules()

class Faction:
    type = { 'war': 1, 'trade': 1, 'magic': 1 }

    def set_type(self, war = 0, trade = 0, magic = 0):
        '''\
        Set faction type.

        Faction type is defined by the Faction Points spent on each
        Faction area.

        Faction points must be positive integers and must not total
        more than rules.GameDefs.faction_points points. Given values
        are converted to integers if they have other type.

        Raises:
        
            ValueError    if values cannot be converted to integers or
            they are negative values
            
            OverflowError if assigned points are more than
            rules.GameDefs.faction_points
            
            Warning       if faction types are not used in the game.
            Faction type is changed anyway

        '''
        new_type = { 'war': war, 'trade': trade, 'magic': magic }
        try:
            r.check_faction_type(**new_type)
        except Exception:
            raise
        else:
            self.type = new_type

if __name__ == '__main__':
    f = Faction()
    r.game_defs.faction_limit_type = rules.GameDefs.FACLIM_UNLIMITED
    f.set_type(1,1,2)
    print(f.type)
