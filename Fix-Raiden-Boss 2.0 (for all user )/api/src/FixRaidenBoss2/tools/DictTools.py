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
from typing import Dict, Any, Hashable, Optional, Callable
##### EndExtImports


##### Script
class DictTools():
    """
    Tools for handling with Dictionaries
    """

    @classmethod
    def getFirstKey(cls, dict: Dict[Any, Any]) -> Any:
        """
        Retrieves the first key in a dictionary

        Parameters
        ----------
        dict: Dict[Any, Any]
            The dictionary we are working with

            .. note::
                The dictionary must not be empty

        Returns
        -------
        Any
            The first key of the dictionary
        """

        return next(iter(dict))

    @classmethod
    def getFirstValue(cls, dict: Dict[Any, Any]) -> Any:
        """
        Retrieves the first value in a dictionary

        Parameters
        ----------
        dict: Dict[Any, Any]
            The dictionary we are working with

        Returns
        -------
        Any
            The first value of the dictionary
        """

        return dict[cls.getFirstKey(dict)]
    
    @classmethod
    def update(cls, srcDict: Dict[Hashable, Any], newDict: Dict[Hashable, Any], combineDuplicate: Optional[Callable[[Any, Any], Any]] = None) -> Dict[Hashable, Any]:
        """
        Updates ``srcDict`` based off the new values from ``newDict``

        Parameters
        ----------
        srcDict: Dict[Hashable, Any]
            The dictionary to be updated

        newDict: Dict[Hashable, Any]
            The dictionary to help with updating ``srcDict``

        combineDuplicate: Optional[Callable[[Any, Any], Any]]
            Function for handling cases where there contains the same key in both dictionaries :raw-html:`<br />` :raw-html:`<br />`

            * The first parameter comes from ``srcDict``
            * The second parameter comes from ``newDict``

            If this value is set to ``None``, then will use the key from ``newDict`` :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        Returns
        -------
        Dict[Hashable, Any]
            Reference to the updated dictionary
        """

        if (combineDuplicate is None):
            srcDict.update(newDict)
            return srcDict
        
        combinedValues = {}
        srcDictLen = len(srcDict)
        newDictLen = len(newDict)
        
        shortDict = srcDict
        longDict = newDict
        if (srcDictLen > newDictLen):
            shortDict = newDict
            longDict = srcDict

        for key in shortDict:
            if (key in longDict):
                combinedValues[key] = combineDuplicate(srcDict[key], newDict[key])

        srcDict.update(newDict)
        srcDict.update(combinedValues)
        return srcDict


    @classmethod
    def combine(cls, dict1: Dict[Hashable, Any], dict2: Dict[Hashable, Any], combineDuplicate: Optional[Callable[[Any, Any], Any]] = None) -> Dict[Hashable, Any]:
        """
        Creates a new dictionary from combining 2 dictionaries

        Parameters
        ----------
        dict1: Dict[Hashable, Any]
            The destination of where we want the combined dictionaries to be stored

        dict2: Dict[Hashable, Any]
            The dictionary we want to combine with

        combineDuplicate: Optional[Callable[[Any, Any], Any]]
            Function for handling cases where there contains the same key in both dictionaries

            If this value is set to ``None``, then will use the key from 'dict2' :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        makeNewCopy: :class:`bool`
            Whether we want the resultant dictionary to be newly created or to be updated into ``dict1``

        Returns
        -------
        Dict[Hashable, Any]
            The new combined dictionary
        """

        new_dict = {**dict1, **dict2}

        if (combineDuplicate is None):
            return new_dict

        for key in new_dict:
            if key in dict1 and key in dict2:
                new_dict[key] = combineDuplicate(new_dict[key], dict1[key])

        return new_dict
    
    @classmethod
    def invert(cls, dict: Dict[Hashable, Hashable]) -> Dict[Hashable, Hashable]:
        """
        Inverts a dictionary by making the keys the values and the values the keys

        Parameters
        ----------
        dict: Dict[Hashable, Hashable]
            The dictionary to invert

        Returns
        -------
        Dict[Hashable, Hashable]
            The inverted dictionary
        """

        return {v: k for k, v in dict.items()}
##### EndScript