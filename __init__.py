from importlib import reload
from . import control
from . import nodes
from . import data
from . import fits
from . import core
from . import rigs
from . import bs
from . import facs
from . import fastPin
from . import preset
from . import tools
from . import setmgr
from . import ui
from . import test

def reload_modules():
    reload(control)
    reload(data)
    reload(nodes)
    reload(fits)
    reload(core)
    reload(rigs)
    reload(bs)
    reload(facs)
    reload(fastPin)
    reload(preset)
    reload(tools)
    reload(setmgr)
    reload(ui)
    reload(test)

reload_modules()





