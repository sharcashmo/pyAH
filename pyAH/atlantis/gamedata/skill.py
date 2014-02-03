"""Handles Atlantis PBEM items.

What units are able to do is mainly determined by their *skills*. Also
learnable skills is what difference men races between them, and them all
from leaders.

This module does not have information about *skills* characteristics.
That is handled by :class:`atlantis.gamedata.rules.SkillType`. Classes
defined in :mod:`atlantis.gamedata.item`, instead, reference actual
instances of *skills* in the game.

*Skills* are mainly related to *units*. A *unit* can know one or more
*skills*, be able to learn a set of *skills* after knowing their
prerrequisites or having the *skill* as his combat spell.

*Skills* are also related to some *item* types. Men *items* have a set
of *skills* they can specialize in, or most produced *items* need a
*skill* to be produced.

"""


from atlantis.helpers.json import JsonSerializable
from atlantis.helpers.comparable import RichComparable # For testing


class Skill(JsonSerializable, RichComparable):
    """Skill reference.
    
    This class holds any reference to a skill: a skill is referenced by
    its abbreviature and its name.
    
    Public attributes of :class:`Skill` are:
    
    .. attribute:: abr
    
       Four (or less) characters abbreviature of the skill, as ``comb``.
       
    .. attribute:: name
    
       Name of the skill, as ``combat``.
    
    """
    def __init__(self, abr, name):
        """:class:`Skill` constructor.
        
        :param abr: abbreviature of the skill.
        :param name: name of the skill.
        
        """
        self.abr = abr
        self.name = name
    
    def json_serialize(self):
        """Return a serializable version of :class:`Skill`.
        
        :return: a *dict* representing the :class:`Skill`
            object.
        
        .. seealso::
           :class:`atlantis.helpers.json.JsonSerializable`
        
        """
        return {'abr': self.abr, 'name': self.name}
    
    @staticmethod
    def json_deserialize(json_object):
        """Load :class:`Skill` from a deserialized json object.

        :param json_object: object returned by :func:`json.load`.
        
        :return: the :class:`Skill` object from json data.
        
        .. seealso::
           :class:`atlantis.helpers.json.JsonSerializable`
        
        """
        return Skill(**json_object)


class SkillLevel(Skill):
    """Skill level.
    
    This class holds any reference to a skill level. This can appear in
    a skill description as prerrequisites or in a battle report.
    
    This class extends :class:`Skill` adding a level attribute.
    
    Public attributes in addition to those defined in :class:`Skill`:
    
    .. attribute:: level
    
       Level of the skill
    
    """
    def __init__(self, abr, name, level):
        """:class:`SkillLevel` constructor.
        
        :param abr: skill abbreviature.
        :param name: skill name.
        :param level: skill level.
        
        """
        Skill.__init__(self, abr, name)
        self.level = level
    
    def json_serialize(self):
        """Return a serializable version of :class:`SkillLevel`.
        
        :return: a *dict* representing the :class:`SkillLevel`
            object.
        
        .. seealso::
           :class:`atlantis.helpers.json.JsonSerializable`
        
        """
        
        json_object = Skill.json_serialize(self)
        json_object.update(level=self.level)
        return json_object
    
    @staticmethod
    def json_deserialize(json_object):
        """Load :class:`SkillLevel` from a deserialized json object.

        :param json_object: object returned by :func:`json.load`.
        
        :return: the :class:`SkillLevel` object from json data.
        
        .. seealso::
           :class:`atlantis.helpers.json.JsonSerializable`
        
        """
        return SkillLevel(**json_object)


class SkillDays(SkillLevel):
    """Skill days.
    
    This class holds any reference to a skill days. This can appear in
    unit reports as the skill known by the unit.
    
    This class extends :class:`SkillLevel` adding a days attribute.
    
    Public attributes in addition to those defined in
    :class:`SkillLevel`:
    
    .. attribute:: days
    
       Days of study of the skill.
    
    """
    def __init__(self, abr, name, level, days, rate=0):
        """:class:`SkillDays` constructor.
        
        :param abr: abbreviature of the skill.
        :param name: name of the skill.
        :param name: skill level.
        :param days: days of study.
        :param rate: rate of study. It's only used when study requires
            experience.
        
        """
        
        SkillLevel.__init__(self, abr, name, level)
        self.days = days
        self.rate = rate
    
    def json_serialize(self):
        """Return a serializable version of :class:`SkillDays`.
        
        :return: a *dict* representing the :class:`SkillDays`
            object.
        
        .. seealso::
           :class:`atlantis.helpers.json.JsonSerializable`
        
        """
        
        json_object = SkillLevel.json_serialize(self)
        json_object.update(days=self.days, rate=self.rate)
        return json_object
    
    @staticmethod
    def json_deserialize(json_object):
        """Load :class:`SkillDays` from a deserialized json object.

        :param json_object: object returned by :func:`json.load`.
        
        :return: the :class:`SkillDays` object from json data.
        
        .. seealso::
           :class:`atlantis.helpers.json.JsonSerializable`
        
        """
        return SkillDays(**json_object)