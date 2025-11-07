try:
    from importlib import reload
except ImportError:
    pass

from .. import rigs
reload(rigs)
from . import base
from . import cluster
from . import fit
from . import facs
from . import preset
from . import main
reload(base)
reload(fit)
reload(cluster)
reload(facs)
reload(preset)
reload(main)
show = main.show
