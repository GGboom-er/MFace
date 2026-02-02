from importlib import reload
from . import control
from . import node
from . import data
from . import fits
from . import core
from . import rigs
from . import bs
from . import facs
from . import fastPin
from . import preset
from . import tools
from . import ui
from . import test

def reload_modules():
    reload(control)
    reload(data)
    reload(node)
    reload(fits)
    reload(core)
    reload(rigs)
    reload(bs)
    reload(facs)
    reload(fastPin)
    reload(preset)
    reload(tools)
    reload(ui)
    reload(test)

reload_modules()





