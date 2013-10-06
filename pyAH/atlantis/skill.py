'''Handles all skill related stuff'''

class SkillLevel:
    '''Represents all information for a skill level'''
    level = None
    descr = None

    def __init__(self, level):
        '''Creates a new skill level'''
        self.level = level

    def set_skill_level(self, **attr):
        '''Set data for the skill level'''
        pass
        

class Skill:
    '''Class representing a skill

    Attributes:
       abbr    Four char length abbreviature for the skill
       name    Complete name of the skill
       descr   General description of the skill

    '''
    abbr = None
    name = None
    descr = None
    levels = dict()

    def __init__(self, abbr, name):
        '''Creates a new skill with the give abbreviature and name'''
        self.abbr = abbr
        self.name = name

    def set_skill(self, level, **attr):
        '''Set data for a skill level'''
        if level not in self.levels.keys():
            self.levels[level] = SkillLevel(level)
            
        self.levels[level].set_skill_level(**attr)
        
        
