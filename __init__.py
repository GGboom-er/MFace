from importlib import reload
from . import shared
from . import control
from . import nodes
from . import data
from . import fits
from . import core
from . import rigs
from . import bs
from . import duplicate_edit
from . import facs
from . import drives
from . import sampling
from . import authoring
from . import fastPin
from . import preset
from . import tools
from . import setmgr
from . import ui
from . import test

def reload_modules():
    reload(shared)
    reload(control)
    reload(data)
    reload(nodes)
    reload(fits)
    reload(core)
    reload(rigs)
    reload(duplicate_edit)
    reload(bs)
    reload(facs)
    reload(drives)
    reload(sampling)
    reload(authoring)
    reload(fastPin)
    reload(preset)
    reload(tools)
    reload(setmgr)
    reload(ui)
    reload(test)

reload_modules()





