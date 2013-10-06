"""This module implements an Atlantis game map.

An Atlantis map is made of several map levels. It's convenient having
several 2D levels than having a 3D map as 


Main class defined in this module is
:class:`~atlantis.gamedata.gamedata.GameData`, a class that implements
:class:`atlantis.parsers.reportparser.ReportConsumer` and thus will
hold all data read from Atlantis PBEM reports."""

#from atlantis.gamedata.region import Region

class Map():
    """:class:`Map` holds all data of Atlantis PBEM map.
    """
    
    regions = None
    
    def __init__(self):
        """Create an empty map."""
        self.regions = dict()
    
    def add_region_info(self, region):
        """Add a region to the map.
        
        This method adds new region information to the map. Actually
        it doesn't add always the region, but looks for it in its
        regions dictionary and updates its data if needed.
        
        :param region: :class:`Region` data to be added to the map.
        
        """

        if region.location in self.regions.keys():
            self.regions[region.location].update(region)
        else:
            self.regions[region.location] = region