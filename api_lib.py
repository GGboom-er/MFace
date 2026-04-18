from maya import cmds
import os
import sys

use_default = False

version = int(round(float(cmds.about(q=1, v=1))))
pyd_path = os.path.abspath(__file__+"/../plug-ins/maya%i" % version).replace("\\", "/")
py_path = os.path.abspath(__file__+"/../plug-ins/maya%s" % "default").replace("\\", "/")
if version == 2022:
    if sys.version[0] == "2":
        pyd_path = os.path.abspath(__file__ + "/../cores/maya%i_2" % version).replace("\\", "/")
if os.path.exists(pyd_path):
    path = pyd_path
else:
    path = py_path

if use_default:
    path = py_path

# Use normpath and normcase for robust cross-os matching
norm_target = os.path.normcase(os.path.normpath(path))
exists = False
for p in sys.path:
    if os.path.normcase(os.path.normpath(p)) == norm_target:
        exists = True
        break

if not exists:
    sys.path.insert(0, path)


import bs_api


