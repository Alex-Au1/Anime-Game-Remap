from ..tools.TextTools import TextTools


ScriptPreamble = """
#
# ----- Note -----
# This script was auto-generated by FixRaidenBoss2's ScriptBuilder tool,
#   a build system tool used in FixRaidenBoss2's CD pipeline that transforms the API source code
#   into a single script
# ----------------
# 
# ########## START OF AUTO-GENERATED SCRIPT ##########
"""

Credits = """
# ===== Raiden Boss Fix =====
# Authors: NK#1321, Albert Gold#2696
#
# if you used it to remap your mods pls give credit for "Nhok0169" and "Albert Gold#2696"
# Special Thanks:
#   nguen#2011 (for support)
#   SilentNightSound#7430 (for internal knowdege so wrote the blendCorrection code)
#   HazrateGolabi#1364 (for being awesome, and improving the code)

"""

ScriptPostamble = """########### END OF AUTO-GENERATED SCRIPT ###########"""

CreditsFileLines = TextTools.getTextLines(Credits)