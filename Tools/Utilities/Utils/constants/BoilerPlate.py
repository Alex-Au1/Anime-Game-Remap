from .StrReplacements import VersionReplace, RanDateTimeReplace, BuildHashReplace, RanHashReplace, BuiltDateTimeReplace, AuthorReplace
from ..TextTools import TextTools
from .toolStats import ScriptBuilderStats, ScriptStats, APIStats, APIMirrorStats, APIMirrorBuilderStats


ScriptPreamble = f"""
#
# ===== Note =====
#
# This script was auto-generated by {APIStats.shortTitle}'s {ScriptBuilderStats.name} tool,
#   a build system tool used in {APIStats.shortTitle}'s CI pipeline that transforms the API source code
#   into a single script
#
# For more info, check out the Github to {ScriptBuilderStats.name} at:
# https://github.com/nhok0169/Anime-Game-Remap/tree/nhok0169/Tools/ScriptBuilder
#
# ***** {ScriptBuilderStats.name} Stats *****
#
# Version: {VersionReplace}
# Authors: {ScriptBuilderStats.getOldDiscNames()}
# Datetime Ran: {RanDateTimeReplace}
# Run Hash: {RanHashReplace}
# 
# *******************************
# ================
# 
# ########## START OF AUTO-GENERATED SCRIPT ##########
"""

MirrorPreamble = f"""
#
# ===== Note =====
#
# This library was auto-generated by {APIStats.shortTitle}'s {APIMirrorBuilderStats.name} tool,
#   a build system tool used in {APIStats.shortTitle}'s CI pipeline that creates a mirror for the existing
#   API source code since we cannot rename the original name of '{APIStats.name}' to '{APIStats.title}' in Pypi,
#   therefore, we decided to make a brand new package that mirrors the original API.
#
# ***** {APIMirrorBuilderStats.name} Stats *****
#
# Version: {VersionReplace}
# Authors: {APIMirrorBuilderStats.getOldDiscNames()}
# Datetime Ran: {RanDateTimeReplace}
# Run Hash: {RanHashReplace}
# 
# *******************************
# ================
#
"""

Credits = f"""
# ===== {APIStats.title} ({APIStats.shortTitle}) =====
# Authors: NK#1321, Albert Gold#2696
#
# if you used it to remap your mods pls give credit for "Nhok0169" and "Albert Gold#2696"
# Special Thanks:
#   nguen#2011 (for support)
#   SilentNightSound#7430 (for internal knowdege so wrote the blendCorrection code)
#   HazrateGolabi#1364 (for being awesome, and improving the code)

"""


ScriptPreambleScriptStats = f"""
#
# ***** {ScriptStats.shortTitle} Stats *****
#
# Version: {VersionReplace}
# Authors: {ScriptStats.getOldDiscNames()}
# Datetime Compiled: {BuiltDateTimeReplace}
# Build Hash: {BuildHashReplace}
#
# ****************************************
#

"""

APIMirrorPreambleStats = f"""
#
# ***** {APIMirrorStats.shortTitle} Stats *****
#
# Version: {VersionReplace}
# Authors: {APIMirrorStats.getOldDiscNames()}
# Datetime Compiled: {BuiltDateTimeReplace}
# Build Hash: {BuildHashReplace}
#
# ****************************************
#

"""

ScriptChangeDir = """
# change our current working directory to this file, allowing users to run program
#   by clicking on the script instead of running by CLI
if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
"""

ScriptPostamble = """########### END OF AUTO-GENERATED SCRIPT ###########"""

CreditsFileLines = TextTools.getTextLines(Credits)