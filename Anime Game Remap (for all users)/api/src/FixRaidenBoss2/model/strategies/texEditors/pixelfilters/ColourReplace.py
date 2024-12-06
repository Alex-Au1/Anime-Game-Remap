##### Credits

# ===== Anime Game Remap (AG Remap) =====
# Authors: NK#1321, Albert Gold#2696
#
# if you used it to remap your mods pls give credit for "Nhok0169" and "Albert Gold#2696"
# Special Thanks:
#   nguen#2011 (for support)
#   SilentNightSound#7430 (for internal knowdege so wrote the blendCorrection code)
#   HazrateGolabi#1364 (for being awesome, and improving the code)

##### EndCredits

##### ExtImports
from typing import Optional, Union
##### EndExtImports

##### LocalImports
from ....textures.Colour import Colour
from ....textures.ColourRange import ColourRange
from .BasePixelFilter import BasePixelFilter
##### EndLocalImports


##### Script
class ColourReplace(BasePixelFilter):
    """
    This class inherits from :class:`BasePixelFilter`

    Replaces a coloured pixel

    Paramaters
    ----------
    replaceColour: :class:`Colour`
        The colour to fill in

    colourToReplace: Optional[Union[:class:`Colour`, :class:`ColourRange`]]
        The colour to find to be replaced. If this value is ``None``, then will always replace the colour of the pixel :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    replaceAlpha: :class:`bool`
        Whether to also replace the alpha channel of the original colour :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``True``

    Attributes
    ----------
    replaceColour: :class:`Colour`
        The colour to fill in

    colourToReplace: Optional[Union[:class:`Colour`, :class:`ColourRange`]]
        The colour to find to be replaced. If this value is ``None``, then will always replace the colour of the pixel

    replaceAlpha: :class:`bool`
        Whether to also replace the alpha channel of the original colour
    """

    def __init__(self, replaceColour: Colour, colourToReplace: Optional[Union[Colour, ColourRange]] = None, replaceAlpha: bool = True):
        self.colourToReplace = colourToReplace
        self.replaceColour = replaceColour
        self.replaceAlpha = replaceAlpha

    def transform(self, pixel: Colour):
        if (self.colourToReplace is None or self.colourToReplace.match(pixel)):
            pixel.copy(self.replaceColour, withAlpha = self.replaceAlpha)
##### EndScript