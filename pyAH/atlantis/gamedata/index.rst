.. _atlantis.gamedata:

~~~~~~~~~~~~~~~~~~~~~~~~
:obj:`atlantis.gamedata`
~~~~~~~~~~~~~~~~~~~~~~~~

:ref:`atlantis.gamedata` subpackage contains some modules in charge of handling
Atlantis PBEM gamedata, since a game's rules (static information not changing
during the game) to turn information, as map, orders, etc. All of these modules
use :mod:`atlantis.helpers.json` functions to *dump* and *load* their data.

Modules in :ref:`atlantis.gamedata` package:

.. autosummary::
   atlantis.gamedata.item
   atlantis.gamedata.gamedata
   atlantis.gamedata.map
   atlantis.gamedata.region
   atlantis.gamedata.rules
 
Contents of :ref:`atlantis.gamedata` package:

.. toctree::
   :maxdepth: 2
   
   item
   gamedata
   map
   region
   rules
