##### Credits

# ===== Raiden Boss Fix =====
# Authors: NK#1321, Albert Gold#2696
#
# if you used it to remap your mods pls give credit for "Nhok0169" and "Albert Gold#2696"
# Special Thanks:
#   nguen#2011 (for support)
#   SilentNightSound#7430 (for internal knowdege so wrote the blendCorrection code)
#   HazrateGolabi#1364 (for being awesome, and improving the code)

##### EndCredits


##### LocalImports
from .Error import Error
##### EndLocalImports


##### Script
class NoModType(Error):
    """
    This Class inherits from :class:`Error`

    Exception when trying to fix a mod of some unidentified mod type

    Parameters
    ----------
    type: :class:`str`
        The name for the type of mod specified 
    """

    def __init__(self):
        super().__init__(f"No mod type specified when fixing the .ini file")
##### EndScript