'''This module handles high level game data structure'''

from atlantis.gamedata.gamedata import GameData
from atlantis.parsers.reportparser import ReportParser

class Turn:
    '''Handles turn (historic) data of the game

    Attributes:
        year          Year of the turn
        month         Month of the turn
        known_skills  Known skills from previous turns
        new_skills    New skills at the turn

    '''
    year = 0
    month = 0
    known_skills = None
    new_skills = None

    def __init__(self, year, month, previous_turn=None):
        '''Creates the turn object'''
        self.year = year
        self.month = month
        self.new_skills = set()
        if previous_turn:
            self.known_skills = previous_turn.known_skills.copy()
            self.known_skills |= previous_turn.new_skills
        else:
            self.known_skills = set()

    def __eq__(self, other):
        '''When it's the same turn'''
        return (self.year == other.year and self.month == other.month)

    def __ne__(self, other):
        '''When it isn't the same turn'''
        return (self.year != other.year or self.month != other.month)

    def __lt__(self, other):
        '''When it's less than the other turn'''
        return (self.year < other.year or
                self.year == other.year and self.month < other.month)

    def __le__(self, other):
        '''When it's less or equal than the other turn'''
        return (self.year < other.year or
                self.year == other.year and self.month <= other.month)

    def __gt__(self, other):
        '''When it's more than the other turn'''
        return (self.year > other.year or
                self.year == other.year and self.month > other.month)

    def __ge__(self, other):
        '''When it's more or equal than the other turn'''
        return (self.year > other.year or
                self.year == other.year and self.month >= other.month)

    def before(self, year, month):
        '''Returns true is turn is previous to year, month date'''
        return (self.year < year or
                self.year == year and self.month < month)

    def compute(self, previous):
        '''Compute data from previous turn'''
        self.known_skills |= previous.known_skills | previous.new_skills
        self.new_skills -= self.known_skills
        

class Game:
    """Handles all game data.

    Public attributes:
    turns   Turns list
    skills  Skills dictionary
    year    Year number of the report (starting from 1)
    month   Month number of the report (starting from 1)
        
    """
    turns = None
    skills = None
    year = 0
    month = 0
    _current_turn = None

    def __init__(self):
        """Create a new game"""
        self.turns = []
        self.skills = dict()
        self._current_turn = None

    def set_turn(self, year, month):
        '''Set current turn'''
        self.year = year
        self.month = month
        if self.turns:
            if self.turns[-1].before(year, month):
                self._current_turn = Turn(year, month, self.turns[-1])
                self.turns.append(self._current_turn)
            else:
                for t in reversed(self.turns):
                    if t.before(year, month):
                        self._current_turn = Turn(year, month, t)
                        self.turns.append(self._current_turn)
                        self.turns.sort()
                        break
                else:
                    self._current_turn = Turn(year, month)
                    self.turns.append(self._current_turn)
                    self.turns.sort()
                self.compute_turns()
        else:
            self._current_turn = Turn(year, month)
            self.turns.append(self._current_turn)

    def compute_turns(self):
        '''Recompute data for turns when inserting an old one'''
        handle_turns = [t for t in self.turns
                        if not t.before(self.year, self.month)]
        k = None
        for t in handle_turns:
            if k:
                t.compute(k)
            k = t

if __name__ == '__main__':
    gd = GameData()
    parser = ReportParser(gd)
    with open('report.1') as f:
        parser.parse(f)

    print('total', len(gd.map.regions))
    oceans = [r for r in gd.map.regions.values() if r.terrain == 'ocean']
    print('oceans', len(oceans))
    forests = [r for r in gd.map.regions.values() if r.terrain == 'forest']
    print('forests', len(forests))
    mountains = [r for r in gd.map.regions.values() if r.terrain == 'mountain']
    print('mountains', len(mountains))