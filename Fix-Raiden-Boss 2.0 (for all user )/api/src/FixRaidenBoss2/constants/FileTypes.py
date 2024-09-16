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


##### ExtImports
from enum import Enum
##### EndExtImports

##### LocalImports
from .FileExt import FileExt
##### EndLocalImports


##### Script
class FileTypes(Enum):
    Default = "file"
    Ini = f"*{FileExt.Ini.value} file"
    Blend = f"Blend{FileExt.Buf.value}"
    RemapBlend = f"Remap{Blend}"
    Log = f"RemapFixLog{FileExt.Txt.value}"
##### EndScript