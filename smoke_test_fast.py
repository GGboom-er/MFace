import sys
import maya.standalone
try:
    maya.standalone.initialize(name='python')
except Exception:
    pass
import maya.cmds as cmds

# Disable all dialogs for automated testing
def mock_prompt(*args, **kwargs):
    if kwargs.get('query') or kwargs.get('q'):
        return "TestSDKName"
    return "OK"

cmds.confirmDialog = lambda *args, **kwargs: "OK"
cmds.promptDialog = mock_prompt

for m in list(sys.modules.keys()):
    if m.startswith('MFace2'):
        del sys.modules[m]
if "Y:\\GGbommer\\scripts" not in sys.path:
    sys.path.insert(0, "Y:\\GGbommer\\scripts")

import MFace2
import MFace2.test as test
import MFace2.preset as preset
import traceback
from MFace2.core import Ctrl

def run_integration_tests():
    print("--- 1. Testing Rigs Building & Presets (Fast) ---")
    test.test_brow()

    print("--- 2. Testing Preset Save & Load (Decoupled Backend) ---")
    preset_name = "IntegrationTestPresetFast"
    if preset_name in preset.get_presets():
        preset.delete_preset(preset_name)

    preset.create_preset(preset_name)
    preset.save_preset_plane(preset_name)
    preset.save_preset_ctrl(preset_name)
    preset.save_preset_face_sdk(preset_name)

    # Delete the rig
    cmds.select("FCtrlBrow_M")
    Ctrl.delete_selected()

    # Decoupled callback
    def dummy_ask(modules):
        return modules, {}

    import MFace2.tools as tools
    tools.build_all()
    preset.load_preset(preset_name, ask_modules_cb=dummy_ask)

    print("--- 3. Testing Face Pose (FACS) Backend ---")
    test.test_face_pose_edit()

    print("ALL INTEGRATION TESTS PASSED")

try:
    run_integration_tests()
    result = {"status": "SUCCESS"}
except Exception as e:
    result = {"status": "FAILED", "error": traceback.format_exc()}
