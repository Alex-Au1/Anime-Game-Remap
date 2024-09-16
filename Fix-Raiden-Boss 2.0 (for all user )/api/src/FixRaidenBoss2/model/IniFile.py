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
import re
import os
import configparser
from functools import cmp_to_key
from typing import List, Dict, Optional, Set, Callable, TYPE_CHECKING, Any, Union, Tuple
##### EndExtImports

##### LocalImports
from ..constants.GenericTypes import Pattern
from ..constants.FilePathConsts import FilePathConsts
from ..constants.FileEncodings import FileEncodings
from ..exceptions.NoModType import NoModType
from .Model import Model
from .IfTemplate import IfTemplate
from .IniSectionGraph import IniSectionGraph
from .RemapBlendModel import RemapBlendModel
from .modtypes.ModType import ModType
from .iniparserdicts.KeepFirstDict import KeepFirstDict
from ..tools.Heading import Heading
from ..tools.files.FilePath import FilePath
from ..tools.TextTools import TextTools
from ..tools.files.FileService import FileService

if (TYPE_CHECKING):
    from ..view.Logger import Logger
##### EndLocalImports


##### Script
# IniFile: Class to handle .ini files
class IniFile(Model):
    """
    This class inherits from :class:`Model`

    Class for handling .ini files

    :raw-html:`<br />`

    .. note::
        We analyse the .ini file using Regex which is **NOT** the right way to do things
        since the modified .ini language that GIMI interprets is a **CFG** (context free grammer) and **NOT** a regular language.
   
        But since we are lazy and don't want make our own compiler with tokenizers, parsing algorithms (eg. SLR(1)), type checking, etc...
        this module should handle regular cases of .ini files generated using existing scripts (assuming the user does not do anything funny...)

    :raw-html:`<br />`

    Parameters
    ----------
    file: Optional[:class:`str`]
        The file path to the .ini file :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    logger: Optional[:class:`Logger`]
        The logger to print messages if necessary

    txt: :class:`str`
        Used as the text content of the .ini file if :attr:`IniFile.file` is set to ``None`` :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ""

    modTypes: Optional[Set[:class:`ModType`]]
        The types of mods that the .ini file should belong to :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    modsToFix: Optional[Set[:class:`str`]]
        The names of the mods we want to fix to :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    defaultModType: Optional[:class:`ModType`]
        The type of mod to use if the .ini file has an unidentified mod type :raw-html:`<br />` :raw-html:`<br />`
        If this value is ``None``, then will skip the .ini file with an unidentified mod type :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    version: Optional[:class:`float`]
        The game version we want the .ini file to be compatible with :raw-html:`<br />` :raw-html:`<br />`

        If This value is ``None``, then will retrieve the hashes/indices of the latest version. :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    Attributes
    ----------
    version: Optional[:class:`float`]
        The game version we want the .ini file to be compatible with :raw-html:`<br />` :raw-html:`<br />`

        If This value is ``None``, then will retrieve the hashes/indices of the latest version.

    _parser: `ConfigParser`_
        Parser used to parse very basic cases in a .ini file

    modTypes: Set[:class:`ModType`]
        The types of mods that the .ini file should belong to

    modsToFix: Set[:class:`str`]
        The names of the mods that we want to fix to

    _toFix: Set[:class:`str`]
        The names of the mods that will be fix to from this .ini file

    defaultModType: Optional[:class:`ModType`]
        The type of mod to use if the .ini file has an unidentified mod type

    _textureOverrideBlendRoot: Optional[:class:`str`]
        The name for the `section`_ containing the keywords: ``[.*TextureOverride.*Blend.*]``

    _sectionIfTemplates: Dict[:class:`str`, :class:`IfTemplate`]
        All the `sections`_ in the .ini file that can be parsed into an :class:`IfTemplate`

        For more info see :class:`IfTemplate`

        .. warning::
            The modified .ini language that GIMI uses introduces keywords that can be used before the key of a key-value pair :raw-html:`<br />`

            *eg. defining constants*

            .. code-block:: ini
                :linenos:

                [Constants]
                global persist $swapvar = 0
                global persist $swapscarf = 0
                global $active
                global $creditinfo = 0

            :raw-html:`<br />`

            `Sections`_ containing this type of pattern will not be parsed. But generally, these sections are irrelevant to fixing the Raiden Boss

    _resourceBlends: Dict[:class:`str`, :class:`IfTemplate`]
        `Sections`_ that are linked to 1 or more Blend.buf files.

        The keys are the name of the sections.

    _blendCommandsGraph: :class:`IniSectionGraph`
        All the `sections`_ that use some ``[Resource.*Blend.*]`` section.

    _nonBlendHashIndexCommandsGraph :class:`IniSectionGraph`
        All the `sections`_ that are not used by the ``[Resource.*Blend.*]`` sections and contains the target hashes/indices that need to be replaced

    _resourceCommandsGraph: :class:`IniSectionGraph`
        All the related `sections`_ to the ``[Resource.*Blend.*]`` sections that are used by `sections`_ related to the ``[TextureOverride.*Blend.*]`` sections.
        The keys are the name of the `sections`_.

    remapBlendModels: Dict[:class:`str`, :class:`RemapBlendModel`]
        The data for the ``[Resource.*RemapBlend.*]`` `sections`_ used in the fix

        The keys are the original names of the resource with the pattern ``[Resource.*Blend.*]``
    """

    ShortModTypeNameReplaceStr = "{{shortModTypeName}}"
    ModTypeNameReplaceStr = "{{modTypeName}}"
    Credit = f'\n; {ModTypeNameReplaceStr}remapped by NK#1321 and Albert Gold#2696. If you used it to remap your {ShortModTypeNameReplaceStr}mods pls give credit for "Nhok0169" and "Albert Gold#2696"\n; Thank nguen#2011 SilentNightSound#7430 HazrateGolabi#1364 for support'

    _oldHeading = Heading(".*Boss Fix", 15, "-")
    _defaultHeading = Heading(".*Remap", 15, "-")

    Hash = "hash"
    Vb1 = "vb1"
    Handling = "handling"
    Draw = "draw"
    Resource = "Resource"
    Blend = "Blend"
    Run = "run"
    MatchFirstIndex = "match_first_index"
    RemapBlend = f"Remap{Blend}"
    RemapFix = f"RemapFix"

    # -- regex strings ---

    _textureOverrideBlendPatternStr = r"^\s*\[\s*TextureOverride.*" + Blend + r".*\s*\]"
    _fixedTextureOverrideBlendPatternStr = r"^\s*\[\s*TextureOverride.*" + RemapBlend + r".*\s*\]"
    
    # --------------------
    # -- regex objects ---
    _sectionPattern = re.compile(r"^\s*\[.*\]")
    _textureOverrideBlendPattern = re.compile(_textureOverrideBlendPatternStr)
    _fixedTextureOverrideBlendPattern = re.compile(_fixedTextureOverrideBlendPatternStr)
    _fixRemovalPattern = re.compile(f"(; {_oldHeading.open()}((.|\n)*?); {_oldHeading.close()[:-2]}(-)*)|(; {_defaultHeading.open()}((.|\n)*?); {_defaultHeading.close()[:-2]}(-)*)")
    _removalPattern = re.compile(f"^\s*\[.*(" + RemapBlend + "|" + RemapFix + r").*\]")
    _sectionRemovalPattern = re.compile(f".*(" + RemapBlend + "|" + RemapFix + r").*")

    # -------------------

    _ifStructurePattern = re.compile(r"\s*(endif|if|else)")

    def __init__(self, file: Optional[str] = None, logger: Optional["Logger"] = None, txt: str = "", modTypes: Optional[Set[ModType]] = None, defaultModType: Optional[ModType] = None, 
                 version: Optional[float] = None, modsToFix: Optional[Set[str]] = None):
        super().__init__(logger = logger)

        self._filePath: Optional[FilePath] = None
        self.file = file
        self.version = version
        self._parser = configparser.ConfigParser(dict_type = KeepFirstDict, strict = False)

        self._fileLines = []
        self._fileTxt = ""
        self._fileLinesRead = False
        self._ifTemplatesRead = False
        self._setupFileLines(fileTxt = txt)

        if (modTypes is None):
            modTypes = set()
        if (modsToFix is None):
            modsToFix = set()

        self.defaultModType = defaultModType
        self.modTypes = modTypes
        self.modsToFix = modsToFix
        self._toFix: Set[str] = {}
        self._heading = self._defaultHeading.copy()

        self._isFixed = False
        self._setType(None)
        self._isModIni = False

        self._textureOverrideBlendRoot: Optional[str] = None
        self._textureOverrideBlendSectionName: Optional[str] = None
        self._sectionIfTemplates: Dict[str, IfTemplate] = {}
        self._resourceBlends: Dict[str, IfTemplate] = {}

        self._blendCommandsGraph = IniSectionGraph(set(), {}, remapNameFunc = self.getRemapBlendName)
        self._nonBlendHashIndexCommandsGraph = IniSectionGraph(set(), {}, remapNameFunc = self.getRemapFixName)
        self._resourceCommandsGraph = IniSectionGraph(set(), {}, remapNameFunc = self.getRemapResourceName)

        self.remapBlendModels: Dict[str, RemapBlendModel] = {}

    @property
    def filePath(self) -> Optional[FilePath]:
        """
        The path to the .ini file

        :getter: Returns the path to the file
        :type: Optional[:class:`FilePath`]
        """
        return self._filePath

    @property
    def file(self) -> Optional[str]:
        """
        The file path to the .ini file

        :getter: Returns the path to the file
        :setter: Sets the new path for the file
        :type: Optional[:class:`str`]
        """

        if (self._filePath is None):
            return None
        return self._filePath.path
    
    @file.setter
    def file(self, newFile: Optional[str]) -> str:
        if (newFile is not None and self._filePath is None):
            self._filePath = FilePath(newFile)
        elif (newFile is not None):
            self._filePath.path = newFile
        elif (self._filePath is not None):
            self._filePath = None

    @property
    def folder(self) -> str:
        """
        The folder where this .ini file resides :raw-html:`<br />` :raw-html:`<br />`

        If :attr:`IniFile.file` is set to ``None``, then will return the folder where this script is ran

        :getter: Retrieves the folder
        :type: :class:`str`
        """

        if (self._filePath is not None):
            return self._filePath.folder
        return FilePathConsts.CurrentDir

    @property
    def isFixed(self) -> bool:
        """
        Whether the .ini file has already been fixed

        :getter: Returns whether the .ini file has already been fixed
        :type: :class:`bool`
        """

        return self._isFixed
    
    @property
    def type(self) -> Optional[ModType]:
        """
        The type of mod the .ini file belongs to

        :getter: Returns the type of mod the .ini file belongs to
        :type: Optional[:class:`ModType`]
        """

        return self._type
    
    def _setType(self, newType: Optional[ModType]):
        self._type = newType
        self._heading.title = None
    
    @property
    def isModIni(self) -> bool:
        """
        Whether the .ini file belongs to a mod

        :getter: Returns whether the .ini file belongs to a mod
        :type: :class:`bool`
        """

        return self._isModIni
    
    @property
    def fileLinesRead(self) -> bool:
        """
        Whether the .ini file has been read

        :getter: Determines whether the .ini file has been read
        :type: :class:`bool`
        """

        return self._fileLinesRead
    
    @property
    def fileTxt(self) -> str:
        """
        The text content of the .ini file

        :getter: Returns the content of the .ini file
        :setter: Reads the new value for both the text content of the .ini file and the text lines of the .ini file 
        :type: :class:`str`
        """

        return self._fileTxt
    
    @fileTxt.setter
    def fileTxt(self, newFileTxt: str):
        self._fileTxt = newFileTxt
        self._fileLines = TextTools.getTextLines(self._fileTxt)

        self._fileLinesRead = True
        self._isFixed = False
        self._textureOverrideBlendRoot = None
        self._textureOverrideBlendSectionName = None

    @property
    def fileLines(self) -> List[str]:
        """
        The text lines of the .ini file :raw-html:`<br />` :raw-html:`<br />`

        .. note::
            For the setter, each line must end with a newline character (same behaviour as `readLines`_)

        :getter: Returns the text lines of the .ini file
        :setter: Reads the new value for both the text lines of the .ini file and the text content of the .ini file
        :type: List[:class:`str`]
        """

        return self._fileLines
    
    @fileLines.setter
    def fileLines(self, newFileLines: List[str]):
        self._fileLines = newFileLines
        self._fileTxt = "".join(self._fileLines)

        self._fileLinesRead = True
        self._isFixed = False
        self._textureOverrideBlendRoot = None
        self._textureOverrideBlendSectionName = None

    def clearRead(self, eraseSourceTxt: bool = False):
        """
        Clears the saved text read in from the .ini file

        .. note::
            If :attr:`IniFile.file` is set to ``None``, then the default run of this function
            with the argument ``eraseSourceTxt`` set to ``False`` will have no effect since the provided text from :attr:`IniFile._fileTxt` is the only source of data for the :class:`IniFile`

            If you also want to clear the above source text data, then run this function with the ``eraseSourceTxt`` argument set to ``True``

        Parameters
        ----------
        eraseSourceTxt: :class:`bool`
            Whether to erase the only data source for this class if :attr:`IniFile.file` is set to ``None``, see the note above for more info :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``False``
        """

        if (self._filePath is not None or eraseSourceTxt):
            self._fileLines = []
            self._fileTxt = ""
            self._fileLinesRead = False

            self._isFixed = False
            self._textureOverrideBlendRoot = None
            self._textureOverrideBlendSectionName = None

    def clear(self, eraseSourceTxt: bool = False):
        """
        Clears all the saved data for the .ini file

        .. note::
            Please see the note at :meth:`IniFile.clearRead`

        Parameters
        ----------
        eraseSourceTxt: :class:`bool`
            Whether to erase the only data source for this class if :attr:`IniFile.file` is set to ``None``, see the note at :meth:`IniFile.clearRead` for more info :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``False``
        """

        self.clearRead(eraseSourceTxt = eraseSourceTxt)
        self._heading = self._defaultHeading.copy()
        self._setType(None)
        self._isModIni = False

        self._ifTemplatesRead = False
        self._sectionIfTemplates = {}
        self._resourceBlends = {}

        self._blendCommandsGraph.build(newTargetSections = set(), newAllSections = {})
        self._nonBlendHashIndexCommandsGraph.build(newTargetSections = set(), newAllSections = {})
        self._resourceCommandsGraph.build(newTargetSections = set(), newAllSections = {})

        self.remapBlendModels = {}


    @property
    def availableType(self) -> Optional[ModType]:
        """
        Retrieves the type of mod identified for this .ini file

        .. note::
            This function is the same as :meth:`IniFile.type`, but will return :attr:`IniFile.defaultModType` if :meth:`IniFile.type` is ``None``

        Returns
        -------
        Optional[:class:`ModType`]
            The type of mod identified
        """

        if (self._type is not None):
            return self._type
        elif (self.defaultModType is not None):
            return self.defaultModType
        
        return None

    def read(self) -> str:
        """
        Reads the .ini file :raw-html:`<br />` :raw-html:`<br />`

        If :attr:`IniFile.file` is set to ``None``, then will read the existing value from :attr:`IniFile.fileTxt`

        Returns
        -------
        :class:`str`
            The text content of the .ini file
        """

        if (self._filePath is not None):
            self.fileTxt = FileService.read(self._filePath.path, "r", lambda filePtr: filePtr.read())
        return self._fileTxt
    
    def write(self) -> str:
        """
        Writes back into the .ini files based off the content in :attr:`IniFile._fileLines`

        Returns
        -------
        :class:`str`
            The text that is written to the .ini file
        """

        if (self._filePath is None):
            return self._fileTxt

        with open(self._filePath.path, "w", encoding = FileEncodings.UTF8.value) as f:
            f.write(self._fileTxt)

        return self._fileTxt

    def _setupFileLines(self, fileTxt: str = ""):
        if (self._filePath is None):
            self.fileTxt = fileTxt
            self._fileLinesRead = True

    def readFileLines(self) -> List[str]:
        """
        Reads each line in the .ini file :raw-html:`<br />` :raw-html:`<br />`

        If :attr:`IniFile.file` is set to ``None``, then will read the existing value from :attr:`IniFile.fileLines`

        Returns
        -------
        List[:class:`str`]
            All the lines read from the .ini file
        """

        if (self._filePath is not None):
            self.fileLines = FileService.read(self._filePath.path, "r", lambda filePtr: filePtr.readlines())
        return self._fileLines

    def _readLines(func):
        """
        Decorator to read all the lines in the .ini file first before running a certain function

        All the file lines will be saved in :attr:`IniFile._fileLines`

        Examples
        --------
        .. code-block:: python
            :linenos:

            @_readLines
            def printLines(self):
                for line in self._fileLines:
                    print(f"LINE: {line}")
        """

        def readLinesWrapper(self, *args, **kwargs):
            if (not self._fileLinesRead):
                self.readFileLines()
            return func(self, *args, **kwargs)
        return readLinesWrapper
    
    def checkIsMod(self) -> bool:
        """
        Reads the entire .ini file and checks whether the .ini file belongs to a mod

        .. note::
            If the .ini file has already been parsed (eg. calling :meth:`IniFile.checkModType` or :meth:`IniFile.parse`), then

            you only need to read :meth:`IniFile.isModIni`

        Returns
        -------
        :class:`bool`
            Whether the .ini file is a .ini file that belongs to some mod
        """
        
        self.clearRead()
        section = lambda line: False
        self.getSectionOptions(section, postProcessor = lambda startInd, endInd, fileLines, sectionName, srcTxt: "")
        return self._isModIni
    
    def _checkModType(self, line: str):
        """
        Checks if a line of text contains the keywords to identify whether the .ini file belongs to the types of mods in :attr:`IniFile.modTypes` :raw-html:`<br />` :raw-html:`<br />`

        * If :attr:`IniFile.modTypes` is not empty, then will find the first :class:`ModType` that where the line makes :meth:`ModType.isType` return ``True``
        * Otherwise, will see if the line matches with the regex, ``[.*TextureOverride.*Blend.*]`` 

        Parameters
        ----------
        line: :class:`str`
            The text to check
        """

        if (not self._isModIni and self.defaultModType is not None and 
            self._textureOverrideBlendSectionName is None and self._textureOverrideBlendPattern.search(line)):
            self._isModIni = True
            self._textureOverrideBlendSectionName = self._getSectionName(line)

        if (self._textureOverrideBlendRoot is not None):
            return
        
        if (not self.modTypes and self._textureOverrideBlendPattern.search(line)):
            self._textureOverrideBlendRoot = self._getSectionName(line)
            self._isModIni = True
            return

        for modType in self.modTypes:
            if (modType.isType(line)):
                self._textureOverrideBlendRoot = self._getSectionName(line)
                self._setType(modType)
                self._isModIni = True
                break

    def _checkFixed(self, line: str):
        """
        Checks if a line of text matches the regex, ``[.*TextureOverride.*RemapBlend.*]`` ,to identify whether the .ini file has been fixed

        Parameters
        ----------
        line: :class:`str`
            The line of text to check
        """

        if (not self._isFixed and self._fixedTextureOverrideBlendPattern.search(line)):
            self._isFixed = True

    def _parseSection(self, sectionName: str, srcTxt: str, save: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, str]]:
        """
        Regularly parses the key-value pairs of a certain `section`_

        The function parses uses `ConfigParser`_ to parse the `section`_.

        Parameters
        ----------
        sectionName: :class:`str`
            The name of the `section`_

        srcTxt: :class:`str`
            The text containing the entire `section`_

        save: Optional[Dict[:class:`str`, Any]]
            Place to save the parsed result for the `section`_  :raw-html:`<br />` :raw-html:`<br />`

            The result for the parsed `section`_ will be saved as a value in the dictionary while section's name will be used in the key for the dictionary :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        Returns
        -------
        Optional[Dict[:class:`str`, :class:`str`]]
            The result from parsing the `section`_

            .. note:: 
                If `ConfigParser`_ is unable to parse the section, then ``None`` is returned
        """

        result = None
        try:
            self._parser.read_string(srcTxt)
            result = dict(self._parser[sectionName])
        except Exception:
            return result

        try:
            save[sectionName] = result
        except TypeError:
            pass

        return result
    
    def _getSectionName(self, line: str) -> str:
        currentSectionName = line
        rightPos = currentSectionName.rfind("]")
        leftPos = currentSectionName.find("[")

        if (rightPos > -1 and leftPos > -1):
            currentSectionName = currentSectionName[leftPos + 1:rightPos]
        elif (rightPos > -1):
            currentSectionName = currentSectionName[:rightPos]
        elif (leftPos > -1):
            currentSectionName = currentSectionName[leftPos + 1:]

        return currentSectionName.strip()

    # retrieves the key-value pairs of a section in the .ini file. Manually parsed the file since ConfigParser
    #   errors out on conditional statements in .ini file for mods. Could later inherit from the parser (RawConfigParser) 
    #   to custom deal with conditionals
    @_readLines
    def getSectionOptions(self, section: Union[str, Pattern, Callable[[str], bool]], postProcessor: Optional[Callable[[int, int, List[str], str, str], Any]] = None, 
                          handleDuplicateFunc: Optional[Callable[[List[Any]], Any]] = None) -> Dict[str, Any]:
        """
        Reads the entire .ini file for a certain type of `section`_

        Parameters
        ----------
        section: Union[:class:`str`, `Pattern`_, Callable[[:class:`str`], :class:`bool`]]
            The type of section to find

            * If this argument is a :class:`str`, then will check if the line in the .ini file exactly matches the argument
            * If this argument is a `Pattern`_, then will check if the line in the .ini file matches the specified Regex pattern
            * If this argument is a function, then will check if the line in the .ini file passed as an argument for the function will make the function return ``True``

        postProcessor: Optional[Callable[[:class:`int`, :class:`int`, List[:class:`str`], :class:`str`, :class:`str`], Any]]
            Post processor used when a type of `section`_ has been found

            The order of arguments passed into the post processor will be:

            #. The starting line index of the `section`_ in the .ini file
            #. The ending line index of the `section`_ in the .ini file
            #. All the file lines read from the .ini file
            #. The name of the `section`_ found
            #. The entire text for the `section`_ :raw-html:`<br />` :raw-html:`<br />`

            **Default**: `None`

        handleDuplicateFunc: Optional[Callable[List[Any], Any]]
            Function to used to handle the case of multiple sections names :raw-html:`<br />` :raw-html:`<br />`

            If this value is set to ``None``, will keep all sections with the same names

            .. note::
                For this case, GIMI only keeps the first instance of all sections with same names

            :raw-html:`<br />`

            **Default**: ``None``

        Returns
        -------
        Dict[:class:`str`, Any]
            The resultant `sections`_ found

            The keys are the names of the `sections`_ found and the values are the content for the `section`_,
        """

        sectionFilter = None
        if (isinstance(section, str)):
            sectionFilter = lambda line: line == section
        elif callable(section):
            sectionFilter = section
        else:
            sectionFilter = lambda line: section.search(line)

        if (postProcessor is None):
            postProcessor = lambda startInd, endInd, fileLines, sectionName, srcTxt: self._parseSection(sectionName, srcTxt)

        result = {}
        currentSectionName = None
        currentSectionToParse = None
        currentSectionStartInd = -1

        fileLinesLen = len(self._fileLines)

        for i in range(fileLinesLen):
            line = self._fileLines[i]
            self._checkFixed(line)
            self._checkModType(line)

            # process the resultant section
            if (currentSectionToParse is not None and self._sectionPattern.search(line)):
                currentResult = postProcessor(currentSectionStartInd, i, self._fileLines, currentSectionName, currentSectionToParse)
                if (currentResult is None):
                    continue

                # whether to keep sections with the same name
                try:
                    result[currentSectionName]
                except KeyError:
                    result[currentSectionName] = [currentResult]
                else:
                    result[currentSectionName].append(currentResult)

                currentSectionToParse = None
                currentSectionName = None
                currentSectionStartInd = -1

            elif (currentSectionToParse is not None):
                currentSectionToParse += f"{line}"

            # keep track of the found section
            if (sectionFilter(line)):
                currentSectionToParse = f"{line}"
                currentSectionName = self._getSectionName(currentSectionToParse)
                currentSectionStartInd = i

        # get any remainder section
        if (currentSectionToParse is not None):
            currentResult = postProcessor(currentSectionStartInd, fileLinesLen, self._fileLines, currentSectionName, currentSectionToParse)
            try:
                result[currentSectionName]
            except:
                result[currentSectionName] = [currentResult]
            else:
                result[currentSectionName].append(currentResult)

        if (handleDuplicateFunc is None):
            return result

        # handle the duplicate sections with the same names
        for sectionName in result:
            result[sectionName] = handleDuplicateFunc(result[sectionName])

        return result

    def _removeSection(self, startInd: int, endInd: int, fileLines: List[str], sectionName: str, srcTxt: str) -> Tuple[int, int]:
        """
        Retrieves the starting line index and ending line index of where to remove a certain `section`_ from the read lines of the .ini file

        Parameters
        ----------
        startInd: :class:`int`
            The starting line index of the `section`_

        endInd: :class:`int`
            The ending line index of the `section`_

        fileLines: List[:class:`str`]
            All the file lines read from the .ini file

        sectionName: :class:`str`
            The name of the `section`_

        srcTxt: :class:`str`
            The text content of the `section`_

        Returns
        -------
        Tuple[:class:`int`, :class:`int`]
            The starting line index and the ending line index of the `section`_ to remove
        """

        fileLinesLen = len(fileLines)
        if (endInd > fileLinesLen):
            endInd = fileLinesLen

        if (startInd > fileLinesLen):
            startInd = fileLinesLen

        return (startInd, endInd)
    
    def removeSectionOptions(self, section: Union[str, Pattern, Callable[[str], bool]]):
        """
        Removes a certain type of `section`_ from the .ini file

        Parameters
        ----------
        section: Union[:class:`str`, `Pattern`_, Callable[[:class:`str`], :class:`bool`]]
            The type of `section`_ to remove
        """

        rangesToRemove = self.getSectionOptions(section, postProcessor = self._removeSection)
        partIndices = []

        for sectionName, ranges in rangesToRemove.items():
            for range in ranges:
                partIndices.append(range)

        self.fileLines = TextTools.removeLines(self._fileLines, partIndices)

    def _hasIfTemplateAtts(self, ifTemplate: IfTemplate, partIndex: int, part: Union[str, Dict[str, Any]]) -> bool:
        return isinstance(part, dict) and (self._isIfTemplateSubCommand(part) or self._isIfTemplateHash(part) or self._isIfTemplateMatchFirstIndex(part))

    def _setupIfTemplateAtts(self, ifTemplate: IfTemplate, partIndex: int, part: Union[str, Dict[str, Any]]):
        """
        Setup the attributes for the :class:`IfTemplate`

        Parameters
        ----------
        ifTemplate: :class:`IfTemplate`
            The :class:`IfTemplate` we are working with

        partIndex: :class:`int`
            The index for the part of the :class:`IfTemplate` we are working with

        part: Union[:class:`str`, Dict[:class:`str`, Any]]
            The part of the :class:`IfTemplate` we are working with
        """

        if (self._isIfTemplateSubCommand(part)):
            ifTemplate.calledSubCommands[partIndex] = self._getIfTemplateSubCommand(part)
        
        if (self._isIfTemplateHash(part)):
            ifTemplate.hashes.add(self._getIfTemplateHash(part))

        if (self._isIfTemplateMatchFirstIndex(part)):
            ifTemplate.indices.add(self._getIfTemplateMatchFirstIndex(part))


    def _createIfTemplate(self, ifTemplateParts: List[Union[str, Dict[str, Any]]], name: str = "") -> IfTemplate:
        """
        Creates an :class:`IfTemplate`

        Parameters
        ----------
        ifTemplateParts: List[Union[:class:`str`, Dict[:class:`str`, Any]]]
            The parts in the :class:`IfTemplate`

        name: :class:`str`
            The name of the `section`_ for the :class:`IfTemplate`

        Returns
        -------
        :class:`IfTemplate`
            The created :class:`IfTemplate` based off the imaginary 
        """

        result = IfTemplate(ifTemplateParts, name = name)
        result.find(pred = self._hasIfTemplateAtts, postProcessor = self._setupIfTemplateAtts)

        return result

    def _processIfTemplate(self, startInd: int, endInd: int, fileLines: List[str], sectionName: str, srcTxt: str) -> IfTemplate:
        """
        Parses a `section`_ in the .ini file as an :class:`IfTemplate`

        .. note::
            See :class:`IfTemplate` to see how we define an 'IfTemplate'

        Parameters
        ----------
        startInd: :class:`int`
            The starting line index of the `section`_

        endInd: :class:`int`
            The ending line index of the `section`_

        fileLines: List[:class:`str`]
            All the file lines read from the .ini file

        sectionName: :class:`str`
            The name of the `section`_

        srcTxt: :class:`str`
            The text content of the `section`_

        Returns
        -------
        :class:`IfTemplate`
            The generated :class:`IfTemplate` from the `section`_
        """

        ifTemplate = []
        dummySectionName = "dummySection"
        currentDummySectionName = f"{dummySectionName}"
        replaceSection = ""
        atReplaceSection = False

        for i in range(startInd + 1, endInd):
            line = fileLines[i]
            isConditional = bool(self._ifStructurePattern.match(line))

            if (isConditional and atReplaceSection):
                currentDummySectionName = f"{dummySectionName}{i}"
                replaceSection = f"[{currentDummySectionName}]\n{replaceSection}"

                currentPart = self._parseSection(currentDummySectionName, replaceSection)
                if (currentPart is None):
                    currentPart = {}

                ifTemplate.append(currentPart)
                replaceSection = ""

            if (isConditional):
                ifTemplate.append(line)
                atReplaceSection = False
                continue
            
            replaceSection += line
            atReplaceSection = True

        # get any remainder replacements in the if..else template
        if (replaceSection != ""):
            currentDummySectionName = f"{dummySectionName}END{endInd}"
            replaceSection = f"[{currentDummySectionName}]\n{replaceSection}"
            currentPart = self._parseSection(currentDummySectionName, replaceSection)
            if (currentPart is None):
                currentPart = {}

            ifTemplate.append(currentPart)

        # create the if template
        result = self._createIfTemplate(ifTemplate, name = sectionName)
        return result
    

    def getIfTemplates(self, flush: bool = False) -> Dict[str, IfTemplate]:
        """
        Retrieves all the :class:`IfTemplate`s for the .ini file

        .. note::
            This is the same as :meth:`IniFile.readIfTemplates`, but uses caching

        Parameters
        ----------
        flush: :class:`bool`
            Whether to re-parse the :class:`IfTemplates`s instead of using the saved cached values

        Returns
        -------
        Dict[:class:`str`, :class:`IfTempalte`]
            The parsed :class:`IfTemplate`s :raw-html:`<br />` :raw-html:`<br />`

            * The keys are the name of the :class:`IfTemplate`
            * The values are the corresponding :class:`IfTemplate`
        """

        if (not self._ifTemplatesRead or flush):
            self.readIfTemplates()
        return self._sectionIfTemplates

    def readIfTemplates(self) -> Dict[str, IfTemplate]:
        """
        Parses all the :class:`IfTemplate`s for the .ini file

        Returns
        -------
        Dict[:class:`str`, :class:`IfTempalte`]
            The parsed :class:`IfTemplate`s :raw-html:`<br />` :raw-html:`<br />`

            * The keys are the name of the :class:`IfTemplate`
            * The values are the corresponding :class:`IfTemplate`
        """

        self._sectionIfTemplates = self.getSectionOptions(self._sectionPattern, postProcessor = self._processIfTemplate, handleDuplicateFunc = lambda duplicates: duplicates[0])
        self._ifTemplatesRead = True
        return self._sectionIfTemplates 
    
    @classmethod
    def getMergedResourceIndex(cls, mergedResourceName: str) -> Optional[int]:
        """
        Retrieves the index number of a resource created by GIMI's ``genshin_merge_mods.py`` script

        Examples
        --------
        >>> IniFile.getMergedResourceIndex("ResourceCuteLittleEiBlend.8")
        8


        >>> IniFile.getMergedResourceIndex("ResourceCuteLittleEiBlend.Score.-100")
        -100


        >>> IniFile.getMergedResourceIndex("ResourceCuteLittleEiBlend.UnitTests")
        None


        >>> IniFile.getMergedResourceIndex("ResourceCuteLittleEiBlend")
        None

        Parameters
        ----------
        mergedResourceName: :class:`str`
            The name of the `section`_

        Returns
        -------
        Optional[:class:`int`]
            The index for the resource `section`_, if found and the index is an integer
        """
        result = None

        try:
            result = int(mergedResourceName.rsplit(".", 1)[-1])
        except:
            pass
            
        return result
    
    def _compareResources(self, resourceTuple1: Tuple[str, Optional[int]], resourceTuple2: Tuple[str, Optional[int]]) -> int:
        """
        Compare function used for sorting resources :raw-html:`<br />` :raw-html:`<br />`

        The order for sorting is the resources is:
        
        #. Resources that do are not suffixed by an index number
        #. Resource that are suffixed by an index number (see :meth:`IniFile.getMergedResourceIndex` for more info)

        Parameters
        ----------
        resourceTuple1: Tuple[:class:`str`, Optional[:class:`int`]]
            Data for the first resource in the compare function, contains:

            * Name of the resource
            * The index for the resource

        resourceTuple2: Tuple[:class:`str`, Optional[:class:`int`]]
            Data for the second resource in the compare function, contains:

            * Name of the resource
            * The index for the resource

        Returns
        -------
        :class:`int`
            The result for a typical compare function used in sorting

            * returns -1 if ``resourceTuple1`` should come before ``resourceTuple2``
            * returns 1 if ``resourceTuple1`` should come after ``resourceTuple2``
            * returns 0 if ``resourceTuple1`` is equal to ``resourceTuple2`` 
        """

        resourceKey1 = resourceTuple1[1]
        resourceKey2 = resourceTuple2[1]
        resource1MissingIndex = resourceKey1 is None
        resource2MissingIndex = resourceKey2 is None

        if (resource1MissingIndex):
            resourceKey1 = resourceTuple1[0]
        
        if (resource2MissingIndex):
            resourceKey2 = resourceTuple2[0]

        if ((resource1MissingIndex == resource2MissingIndex and resourceKey1 < resourceKey2) or (resource1MissingIndex and not resource2MissingIndex)):
            return -1
        elif ((resource1MissingIndex == resource2MissingIndex and resourceKey1 > resourceKey2) or (not resource1MissingIndex and resource2MissingIndex)):
            return 1
        
        return 0

    # Disabling the OLD ini
    def disIni(self, makeCopy: bool = False):
        """
        Disables the .ini file

        .. note::
            For more info, see :meth:`FileService.disableFile` 

        Parameters
        ----------
        makeCopy: :class:`bool`
            Whether to make a copy of the disabled .ini file :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``False``
        """

        if (self._filePath is None):
            return

        disabledPath = FileService.disableFile(self._filePath.path)
        if (makeCopy):
            FileService.copyFile(disabledPath, self._filePath.path)

    @classmethod
    def getFixedBlendFile(cls, blendFile: str, modName: str = "") -> str:
        """
        Retrieves the file path for the fixed RemapBlend.buf file

        Parameters
        ----------
        blendFile: :class:`str`
            The file path to the original Blend.buf file

        modName: :class:`str`
            The name of the mod to fix to

        Returns
        -------
        :class:`str`
            The file path of the fixed RemapBlend.buf file
        """

        blendFolder = os.path.dirname(blendFile)
        blendBaseName = os.path.basename(blendFile)
        blendBaseName = blendBaseName.rsplit(".", 1)[0]
        
        return os.path.join(blendFolder, f"{cls.getRemapBlendName(blendBaseName, modName = modName)}.buf")
    
    def getFixModTypeName(self) -> Optional[str]:
        """
        Retrieves the name of the type of mod corresponding to the .ini file to be used for the comment of the fix

        Returns
        -------
        Optional[:class:`str`]
            The name for the type of mod corresponding to the .ini file
        """
        if (self._type is None):
            return None
        return self._type.name.replace("\n", "").replace("\t", "")
    
    def getFixModTypeHeadingname(self):
        """
        Retrieves the name of the type of mod corresponding to the .ini file to be used in the header/footer divider comment of the fix

        Returns
        -------
        Optional[:class:`str`]
            The name for the type of mod to be displayed in the header/footer divider comment
        """

        modTypeName = self.getFixModTypeName()
        if (modTypeName is None):
            modTypeName = "GI"

        return modTypeName

    def getHeadingName(self):
        """
        Retrieves the title for the header of the divider comment of the fix

        Returns
        -------
        :class:`str`
            The title for the header of the divider comment
        """

        result = self.getFixModTypeHeadingname()
        if (result):
            result += " "

        return f"{result}Remap"

    def getFixHeader(self) -> str:
        """
        Retrieves the header text used to identify a code section has been changed by this fix
        in the .ini file

        Returns
        -------
        :class:`str`
            The header section comment to be used in the .ini file
        """
        
        if (self._heading.title is None):
            self._heading.title = self.getHeadingName()
        return f"; {self._heading.open()}"
    
    def getFixFooter(self) -> str:
        """
        Retrieves the footer text used to identify a code section has been changed by this fix
        in the .ini file

        Returns
        -------
        :class:`str`
            The footer section comment to be used in the .ini file
        """

        if (self._heading.title is None):
            self._heading.title = self.getHeadingName()
        return f"\n\n; {self._heading.close()}"
    
    def getFixCredit(self) -> str:
        """
        Retrieves the credit text for the code generated in the .ini file

        Returns
        -------
        :class:`str`
            The credits to be displayed in the .ini file
        """

        modTypeName = self.getFixModTypeName()
        shortModTypeName = modTypeName

        if (modTypeName is None):
            modTypeName = "Mod"
            shortModTypeName = ""

        if (modTypeName):
            modTypeName += " "
        
        if (shortModTypeName):
            shortModTypeName += " "
        
        return self.Credit.replace(self.ModTypeNameReplaceStr, modTypeName).replace(self.ShortModTypeNameReplaceStr, shortModTypeName)

    def _addFixBoilerPlate(func):
        """
        Decorator used to add the boilerplate code to identify a code section has been changed by this fix in the .ini file

        Examples
        --------
        .. code-block:: python
            :linenos:

            @_addFixBoilerPlate
            def helloWorld(self) -> str:
                return "Hello World"
        """

        def addFixBoilerPlateWrapper(self, *args, **kwargs):
            addFix = self.getFixHeader()
            addFix += self.getFixCredit()
            addFix += func(self, *args, **kwargs)
            addFix += self.getFixFooter()

            return addFix
        return addFixBoilerPlateWrapper
    
    @classmethod
    def getResourceName(cls, name: str) -> str:
        """
        Makes the name of a `section`_ to be used for the resource `sections`_ of a .ini file

        Examples
        --------
        >>> IniFile.getResourceName("CuteLittleEi")
        "ResourceCuteLittleEi"


        >>> IniFile.getResourceName("ResourceCuteLittleEi")
        "ResourceCuteLittleEi"

        Parameters
        ----------
        name: :class:`str`
            The name of the `section`_

        Returns
        -------
        :class:`str`
            The name of the `section`_ as a resource in a .ini file
        """

        if (not name.startswith(cls.Resource)):
            name = f"{cls.Resource}{name}"
        return name
    
    @classmethod
    def removeResourceName(cls, name: str) -> str:
        """
        Removes the 'Resource' prefix from a section's name

        Examples
        --------
        >>> IniFile.removeResourceName("ResourceCuteLittleEi")
        "CuteLittleEi"


        >>> IniFile.removeResourceName("LittleMissGanyu")
        "LittleMissGanyu"

        Parameters
        ----------
        name: :class:`str`
            The name of the `section`_

        Returns
        -------
        :class:`str`
            The name of the `section`_ with the 'Resource' prefix removed
        """

        if (name.startswith(cls.Resource)):
            name = name[len(cls.Resource):]

        return name
    
    @classmethod
    def getRemapBlendName(cls, name: str, modName: str = "") -> str:
        """
        Changes a `section`_ name to have the keyword 'RemapBlend' to identify that the `section`_
        is created by this fix

        Examples
        --------
        >>> IniFile.getRemapBlendName("EiTriesToUseBlenderAndFails", "Raiden")
        "EiTriesToUseRaidenRemapBlenderAndFails"


        >>> IniFile.getRemapBlendName("EiBlendsTheBlender", "Yae")
        "EiBlendsTheYaeRemapBlender"
    

        >>> IniFile.getRemapBlendName("ResourceCuteLittleEi", "Raiden")
        "ResourceCuteLittleEiRaidenRemapBlend"


        >>> IniFile.getRemapBlendName("ResourceCuteLittleEiRemapBlend", "Raiden")
        "ResourceCuteLittleEiRemapRaidenRemapBlend"

        Parameters
        ----------
        name: :class:`str`
            The name of the `section`_

        modName: :class:`str`
            The name of the mod to fix :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``""``

        Returns
        -------
        :class:`str`
            The name of the `section`_ with the added 'RemapBlend' keyword
        """

        nameParts = name.rsplit(cls.Blend, 1)
        namePartsLen = len(nameParts)

        remapName = f"{modName}{cls.RemapBlend}"
        if (namePartsLen > 1):
            name = remapName.join(nameParts)
        else:
            name += remapName

        return name
    
    @classmethod
    def getRemapFixName(cls, name: str, modName: str = "") -> str:
        """
        Changes a `section`_ name to have the suffix `RemapFix` to identify that the `section`_
        is created by this fix

        Examples
        --------
        >>> IniFile.getRemapFixName("EiIsDoneWithRemapFix", "Raiden")
        "EiIsDoneWithRaidenRemapFix"

        >>> IniFile.getRemapFixName("EiIsHappy", "Raiden")
        "EiIsHappyRaidenRemapFix"

        Parameters
        ----------
        name: :class:`str`
            The name of the `section`_

        modName: :class:`str`
            The name of the mod to fix :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``""``

        Returns
        -------
        :class:`str`
            The name of the `section`_ with the added 'RemapFix' keyword
        """

        remapName = f"{modName}{cls.RemapFix}"
        if (name.endswith(remapName)):
            return name
        elif(name.endswith(cls.RemapFix)):
            return name[:len(cls.RemapFix)] + remapName

        return name + remapName

    @classmethod
    def getRemapResourceName(cls, name: str, modName: str = "") -> str:
        """
        Changes the name of a section to be a new resource that this fix will create

        .. note::
            See :meth:`IniFile.getResourceName` and :meth:`IniFile.getRemapBlendName` for more info

        Parameters
        ----------
        name: :class:`str`
            The name of the section

        modName: :class:`str`
            The name of the mod to fix :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``""``

        Returns
        -------
        :class:`str`
            The name of the section with the prefix 'Resource' and the keyword 'Remap' added
        """

        name = cls.getRemapBlendName(name, modName = modName)
        name = cls.getResourceName(name)
        return name

    def _isIfTemplateResource(self, ifTemplatePart: Dict[str, Any]) -> bool:
        """
        Whether the content for some part of a `section`_ contains the key 'vb1'

        Parameters
        ----------
        ifTemplatePart: Dict[:class:`str`, Any]
            The key-value pairs for some part in a `section`_

        Returns
        -------
        :class:`bool`
            Whether 'vb1' is contained in the part
        """

        return self.Vb1 in ifTemplatePart
    
    def _isIfTemplateDraw(self, ifTemplatePart: Dict[str, Any]) -> bool:
        """
        Whether the content for some part of a `section`_ contains the key 'draw'

        Parameters
        ----------
        ifTemplatePart: Dict[:class:`str`, Any]
            The key-value pairs for some part in a `section`_

        Returns
        -------
        :class:`bool`
            Whether 'draw' is contained in the part
        """


        return self.Draw in ifTemplatePart
    
    def _isIfTemplateHash(self, ifTemplatePart: Dict[str, Any]) -> bool:
        """
        Whether the content for some part of a `section`_ contains the key 'hash'

        Parameters
        ----------
        ifTemplatePart: Dict[:class:`str`, Any]
            The key-value pairs for some part in a section

        Returns
        -------
        :class:`bool`
            Whether 'hash' is contained in the part
        """
                
        return self.Hash in ifTemplatePart
    
    def _isIfTemplateMatchFirstIndex(self, ifTemplatePart: Dict[str, Any]) -> bool:
        """
        Whether the content for some part of a `section`_ contains the key 'match_first_index'

        Parameters
        ----------
        ifTemplatePart: Dict[:class:`str`, Any]
            The key-value pairs for some part in a section

        Returns
        -------
        :class:`bool`
            Whether 'match_first_index' is contained in the part
        """
                
        return self.MatchFirstIndex in ifTemplatePart
    
    def _isIfTemplateSubCommand(self, ifTemplatePart: Dict[str, Any]) -> bool:
        """
        Whether the content for some part of a `section`_ contains the key 'run'

        Parameters
        ----------
        ifTemplatePart: Dict[:class:`str`, Any]
            The key-value pairs for some part in a section

        Returns
        -------
        :class:`bool`
            Whether 'run' is contained in the part
        """
                
        return self.Run in ifTemplatePart
    
    def _getIfTemplateResourceName(self, ifTemplatePart: Dict[str, Any]) -> Any:
        """
        Retrieves the value from the key, 'vb1', for some part of a `section`_

        Parameters
        ----------
        ifTemplatePart: Dict[:class:`str`, Any]
            The key-value pairs for some part in a `section`_

        Returns
        -------
        Any
            The corresponding value for the key 'vb1'
        """

        return ifTemplatePart[self.Vb1]
    
    def _getIfTemplateSubCommand(self, ifTemplatePart: Dict[str, Any]) -> Any:
        """
        Retrieves the value from the key, 'run', for some part of a `section`_

        Parameters
        ----------
        ifTemplatePart: Dict[:class:`str`, Any]
            The key-value pairs for some part in a `section`_

        Returns
        -------
        Any
            The corresponding value for the key 'run'
        """

        return ifTemplatePart[self.Run]
    
    def _getIfTemplateHash(self, ifTemplatePart: Dict[str, Any]) -> Any:
        """
        Retrieves the value from the key, 'hash', for some part of a `section`_

        Parameters
        ----------
        ifTemplatePart: Dict[:class:`str`, Any]
            The key-value pairs for some part in a `section`_

        Returns
        -------
        Any
            The corresponding value for the key 'hash'
        """

        return ifTemplatePart[self.Hash]
    
    def _getIfTemplateMatchFirstIndex(self, ifTemplatePart: Dict[str, Any]) -> Any:
        """
        Retrieves the value from the key, 'match_first_index', for some part of a `section`_

        Parameters
        ----------
        ifTemplatePart: Dict[:class:`str`, Any]
            The key-value pairs for some part in a `section`_

        Returns
        -------
        Any
            The corresponding value for the key 'match_first_index'
        """

        return ifTemplatePart[self.MatchFirstIndex]

    # _getAssetReplacement(assset, assetRepoAttName): Retrieves the replacement for 'asset'
    def _getAssetReplacement(self, asset: str, assetRepoAttName: str, modName: str) -> str:
        result = ""
        type = self.availableType

        if (type is not None):
            assetRepo = getattr(type, assetRepoAttName)
            result = assetRepo.replace(asset, version = self.version, toAssets = modName)
        else:
            raise NoModType()

        return result

    # _getHashReplacement(hash): Retrieves the hash replacement for 'hash'
    def _getHashReplacement(self, hash: str, modName: str) -> str:
        return self._getAssetReplacement(hash, "hashes", modName)
    
    # _getIndexReplacement(index): Retrieves the index replacement for 'index'
    def _getIndexReplacement(self, index: str, modName: str) -> str:
        return self._getAssetReplacement(index, "indices", modName)

    def _fillTextureOverrideRemapBlend(self, modName: str, sectionName: str, part: Dict[str, Any], partIndex: int, linePrefix: str, origSectionName: str) -> str:
        """
        Creates the **content part** of an :class:`IfTemplate` for the new sections created by this fix related to the ``[TextureOverride.*Blend.*]`` `sections`_

        .. note::
            For more info about an 'IfTemplate', see :class:`IfTemplate`

        Parameters
        ----------
        modName: :class:`str`
            The name for the type of mod to fix to

        sectionName: :class:`str`
            The new name for the section

        part: Dict[:class:`str`, Any]
            The content part of the :class:`IfTemplate` of the original [TextureOverrideBlend] `section`_

        partIndex: :class:`int`
            The index of where the content part appears in the :class:`IfTemplate` of the original `section`_

        linePrefix: :class:`str`
            The text to prefix every line of the created content part

        origSectionName: :class:`str`
            The name of the original `section`_

        Returns
        -------
        :class:`str`
            The created content part
        """

        addFix = ""

        for varName in part:
            varValue = part[varName]

            # filling in the subcommand
            if (varName == self.Run):
                subCommandName = self._getRemapName(varValue, modName, sectionGraph = self._blendCommandsGraph)
                subCommandStr = f"{self.Run} = {subCommandName}"
                addFix += f"{linePrefix}{subCommandStr}\n"

            # filling in the hash
            elif (varName == self.Hash):
                hash = self._getHashReplacement(varValue, modName)
                addFix += f"{linePrefix}{self.Hash} = {hash}\n"

            # filling in the vb1 resource
            elif (varName == self.Vb1):
                blendName = self._getIfTemplateResourceName(part)
                remapBlendName = self._getRemapName(blendName, modName, sectionGraph = self._resourceCommandsGraph, remapNameFunc = self.getRemapResourceName)
                fixStr = f'{self.Vb1} = {remapBlendName}'
                addFix += f"{linePrefix}{fixStr}\n"

            # filling in the handling
            elif (varName == self.Handling):
                fixStr = f'{self.Handling} = skip'
                addFix += f"{linePrefix}{fixStr}\n"

            # filling in the draw value
            elif (varName == self.Draw):
                fixStr = f'{self.Draw} = {varValue}'
                addFix += f"{linePrefix}{fixStr}\n"

            # filling in the indices
            elif (varName == self.MatchFirstIndex):
                index = self._getIndexReplacement(varValue, modName)
                addFix += f"{linePrefix}{self.MatchFirstIndex} = {index}\n"
                
        return addFix
    
    def _fillNonBlendSections(self, modName: str, sectionName: str, part: Dict[str, Any], partIndex: int, linePrefix: str, origSectionName: str) -> str:
        """
        Creates the **content part** of an :class:`IfTemplate` for the new sections created by this fix that are not related to the ``[TextureOverride.*Blend.*]`` `sections`_

        .. note::
            For more info about an 'IfTemplate', see :class:`IfTemplate`

        Parameters
        ----------
        modName: :class:`str`
            The name for the type of mod to fix to

        sectionName: :class:`str`
            The new name for the section

        part: Dict[:class:`str`, Any]
            The content part of the :class:`IfTemplate` of the original [TextureOverrideBlend] `section`_

        partIndex: :class:`int`
            The index of where the content part appears in the :class:`IfTemplate` of the original `section`_

        linePrefix: :class:`str`
            The text to prefix every line of the created content part

        origSectionName: :class:`str`
            The name of the original `section`_

        Returns
        -------
        :class:`str`
            The created content part
        """

        addFix = ""

        for varName in part:
            varValue = part[varName]

            # filling in the hash
            if (varName == self.Hash):
                newHash = self._getHashReplacement(varValue, modName)
                addFix += f"{linePrefix}{self.Hash} = {newHash}\n"

            # filling in the subcommand
            elif (varName == self.Run):
                subCommand = self._getRemapName(varValue, modName, sectionGraph = self._nonBlendHashIndexCommandsGraph, remapNameFunc = self.getRemapFixName)
                subCommandStr = f"{self.Run} = {subCommand}"
                addFix += f"{linePrefix}{subCommandStr}\n"

            # filling in the index
            elif (varName == self.MatchFirstIndex):
                newIndex = self._getIndexReplacement(varValue, modName)
                addFix += f"{linePrefix}{self.MatchFirstIndex} = {newIndex}\n"

            else:
                addFix += f"{linePrefix}{varName} = {varValue}\n"

        return addFix
    
    # fill the attributes for the sections related to the resources
    def _fillRemapResource(self, modName: str, sectionName: str, part: Dict[str, Any], partIndex: int, linePrefix: str, origSectionName: str):
        """
        Creates the **content part** of an :class:`IfTemplate` for the new `sections`_ created by this fix related to the ``[Resource.*Blend.*]`` `sections`_

        .. note::
            For more info about an 'IfTemplate', see :class:`IfTemplate`

        Parameters
        ----------
        modName: :class:`str`
            The name for the type of mod to fix to

        sectionName: :class:`str`
            The new name for the `section`_

        part: Dict[:class:`str`, Any]
            The content part of the :class:`IfTemplate` of the original ``[Resource.*Blend.*]`` `section`_

        partIndex: :class:`int`
            The index of where the content part appears in the :class:`IfTemplate` of the original `section`_

        linePrefix: :class:`str`
            The text to prefix every line of the created content part

        origSectionName: :class:`str`
            The name of the original `section`_

        Returns
        -------
        :class:`str`
            The created content part
        """

        addFix = ""

        for varName in part:
            varValue = part[varName]

            # filling in the subcommand
            if (varName == self.Run):
                subCommand = self._getRemapName(varValue, modName, sectionGraph = self._resourceCommandsGraph, remapNameFunc = self.getRemapResourceName)
                subCommandStr = f"{self.Run} = {subCommand}"
                addFix += f"{linePrefix}{subCommandStr}\n"

            # add in the type of file
            elif (varName == "type"):
                addFix += f"{linePrefix}type = Buffer\n"

            # add in the stride for the file
            elif (varName == "stride"):
                addFix += f"{linePrefix}stride = 32\n"

            # add in the file
            elif (varName == "filename"):
                remapModel = self.remapBlendModels[origSectionName]
                fixedBlendFile = remapModel.fixedBlendPaths[partIndex][modName]
                addFix += f"{linePrefix}filename = {fixedBlendFile}\n"

        return addFix
    
    # fills the if..else template in the .ini for each section
    def fillIfTemplate(self, modName: str, sectionName: str, ifTemplate: IfTemplate, fillFunc: Callable[[str, str, Union[str, Dict[str, Any]], int, int, str], str], origSectionName: Optional[str] = None) -> str:
        """
        Creates a new :class:`IfTemplate` for an existing `section`_ in the .ini file

        Parameters
        ----------
        modName: :class:`str`
            The name for the type of mod to fix to

        sectionName: :class:`str`
            The new name of the `section`_

        ifTemplate: :class:`IfTemplate`
            The :class:`IfTemplate` of the orginal `section`_

        fillFunc: Callable[[:class:`str`, :class:`str`, Union[:class:`str`, Dict[:class:`str`, Any], :class:`int`, :class:`str`, :class:`str`], :class:`str`]]
            The function to create a new **content part** for the new :class:`IfTemplate`
            :raw-html:`<br />` :raw-html:`<br />`

            .. note::
                For more info about an 'IfTemplate', see :class:`IfTemplate`

            :raw-html:`<br />`
            The parameter order for the function is:

            #. The name for the type of mod to fix to
            #. The new section name
            #. The corresponding **content part** in the original :class:`IfTemplate`
            #. The index for the content part in the original :class:`IfTemplate`
            #. The string to prefix every line in the **content part** of the :class:`IfTemplate`
            #. The original name of the section

        origSectionName: Optional[:class:`str`]
            The original name of the section.

            If this argument is set to ``None``, then will assume this argument has the same value as the argument for ``sectionName`` :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        Returns
        -------
        :class:`str`
            The text for the newly created :class:`IfTemplate`
        """

        addFix = f"[{sectionName}]\n"
        partIndex = 0
        linePrefix = ""

        if (origSectionName is None):
            origSectionName = sectionName

        for part in ifTemplate:
            # adding in the if..else statements
            if (isinstance(part, str)):
                addFix += part
                
                linePrefix = re.match(r"^[( |\t)]*", part)
                if (linePrefix):
                    linePrefix = linePrefix.group(0)
                    linePrefixLen = len(linePrefix)

                    linePrefix = part[:linePrefixLen]
                    lStrippedPart = part[linePrefixLen:]

                    if (lStrippedPart.find("endif") == -1):
                        linePrefix += "\t"
                partIndex += 1
                continue
            
            # add in the content within the if..else statements
            addFix += fillFunc(modName, sectionName, part, partIndex, linePrefix, origSectionName)

            partIndex += 1
            
        return addFix
    

    # _getCommonMods(): Retrieves the common mods that need to be fixed between all target graphs
    #   that are used for the fix
    def _getCommonMods(self) -> Set[str]:
        if (self._type is None):
            return set()
        
        result = set()
        hashes = self._type.hashes
        indices = self._type.indices

        graphs = [self._blendCommandsGraph, self._nonBlendHashIndexCommandsGraph, self._resourceCommandsGraph]
        for graph in graphs:
            commonMods = graph.getCommonMods(hashes, indices, version = self.version)
            if (not result):
                result = commonMods
            else:
                result = result.intersection(commonMods)

        return result
    

    def _setToFix(self) -> Set[str]:
        """
        Sets the names for the types of mods that will used in the fix

        Returns
        -------
        Set[:class:`str`]
            The names of the mods that will be used in the fix        
        """

        commonMods = self._getCommonMods()
        toFix = commonMods.intersection(self.modsToFix)
        type = self.availableType

        if (not toFix and type is not None):
            self._toFix = type.getModsToFix()
        elif (not toFix):
            self._toFix = commonMods
        else:
            self._toFix = toFix

        return self._toFix

    
    # _makeRemapNames(): Makes the required names used for the fix
    def _makeRemapNames(self):
        self._blendCommandsGraph.getRemapBlendNames(self._toFix)
        self._nonBlendHashIndexCommandsGraph.getRemapBlendNames(self._toFix)
        self._resourceCommandsGraph.getRemapBlendNames(self._toFix)


    # _getRemapName(sectionName, modName, sectionGraph, remapNameFunc): Retrieves the required remap name for the fix
    def _getRemapName(self, sectionName: str, modName: str, sectionGraph: Optional[IniSectionGraph] = None, remapNameFunc: Optional[Callable[[str, str], str]] = None) -> str:
        error = False
        if (sectionGraph is None):
            error = True

        if (not error):
            try:
                return sectionGraph.remapNames[sectionName][modName]
            except KeyError:
                error = True

        if (remapNameFunc is None):
            remapNameFunc = self.getRemapBlendName

        return remapNameFunc(sectionName, modName)


    def getModFixStr(self, modName: str, fix: str = ""):
        """
        Generates the newly added code in the .ini file for the fix of a single type of mod

        .. note::
            eg.
                If we are making the fix from ``Jean`` -> ``JeanCN`` and ``JeanSeaBreeze``,
                The code below will only make the fix for ``JeanCN``

            .. code-block::

                getModFixStr("JeanCN")


        Parameters
        ----------
        fix: :class:`str`
            Any existing text we want the result of the fix to add onto :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ""

        Returns
        -------
        :class:`str`
            The text for the newly generated code in the .ini file
        """

        hasNonBlendSections = bool(self._nonBlendHashIndexCommandsGraph.sections)
        hasResources = bool(self.remapBlendModels)

        if (self._blendCommandsGraph.sections or hasResources or hasNonBlendSections):
            fix += "\n"

        # get the fix string for all the texture override blends
        blendCommandTuples = self._blendCommandsGraph.runSequence
        for commandTuple in blendCommandTuples:
            section = commandTuple[0]
            ifTemplate = commandTuple[1]
            commandName = self._getRemapName(section, modName, sectionGraph = self._blendCommandsGraph)
            fix += self.fillIfTemplate(modName, commandName, ifTemplate, self._fillTextureOverrideRemapBlend)
            fix += "\n"

        if (hasNonBlendSections):
            fix += "\n"

        # get the fix string for non-blend sections
        nonBlendCommandTuples = self._nonBlendHashIndexCommandsGraph.runSequence
        for commandTuple in nonBlendCommandTuples:
            section = commandTuple[0]
            ifTemplate = commandTuple[1]
            commandName = self._getRemapName(section, modName, sectionGraph = self._nonBlendHashIndexCommandsGraph)
            fix += self.fillIfTemplate(modName, commandName, ifTemplate, self._fillNonBlendSections)
            fix += "\n"

        if (hasResources):
            fix += "\n"

        # get the fix string for the resources
        resourceCommandTuples = self._resourceCommandsGraph.runSequence
        resourceCommandsLen = len(resourceCommandTuples)
        for i in range(resourceCommandsLen):
            commandTuple = resourceCommandTuples[i]
            section = commandTuple[0]
            ifTemplate = commandTuple[1]

            resourceName = self._getRemapName(section, modName, sectionGraph = self._resourceCommandsGraph, remapNameFunc = self.getRemapResourceName)
            fix += self.fillIfTemplate(modName, resourceName, ifTemplate, self._fillRemapResource, origSectionName = section)

            if (i < resourceCommandsLen - 1):
                fix += "\n"

        return fix


    # get the needed lines to fix the .ini file
    @_addFixBoilerPlate
    def getFixStr(self, fix: str = "") -> str:
        """
        Generates the newly added code in the .ini file for the fix

        Parameters
        ----------
        fix: :class:`str`
            Any existing text we want the result of the fix to add onto :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ""

        Returns
        -------
        :class:`str`
            The text for the newly generated code in the .ini file
        """

        heading = Heading("", sideLen = 5, sideChar = "*")
        for modName in self._toFix:
            heading.title = modName
            currentFix = self.getModFixStr(modName)

            if (currentFix):
                fix += f"\n\n; {heading.open()}{currentFix}"

        return fix


    @_readLines
    def injectAddition(self, addition: str, beforeOriginal: bool = True, keepBackup: bool = True, fixOnly: bool = False) -> str:
        """
        Adds and writes new text to the .ini file

        Parameters
        ----------
        addition: :class:`str`
            The text we want to add to the file

        beforeOriginal: :class:`bool`
            Whether to add the new text before the original text :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``True``

        keepBackup: :class:`bool`
            Whether we want to make a backup copy of the .ini file :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``True``

        fixOnly: :class:`bool`
            Whether we are only fixing the .ini file without removing any previous changes :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``False``

        Returns
        -------
        :class:`str`
            The content of the .ini file with the new text added
        """

        original = "".join(self._fileLines)

        if (keepBackup and fixOnly and self._filePath is not None):
            self.print("log", "Cleaning up and disabling the OLD STINKY ini")
            self.disIni()

        result = ""
        if (beforeOriginal):
            result = f"{addition}\n\n{original}"
        else:
            result = f"{original}\n{addition}"

        # writing the fixed file
        if (self._filePath is not None):
            with open(self._filePath.path, "w", encoding = FileEncodings.UTF8.value) as f:
                f.write(result)

        self._isFixed = True
        return result
    
    # _getRemovalResource(sectionsToRemove): Retrieves the names of the resource sections to remove
    def _getRemovalResource(self, sectionsToRemove: Set[str]) -> Set[str]:
        result = set()
        allSections = self.getIfTemplates()
        removalSectionGraph = IniSectionGraph(sectionsToRemove, allSections)
        self._getBlendResources(result, removalSectionGraph)

        result = set(filter(lambda section: re.match(self._sectionRemovalPattern, section), result))
        return result

    @_readLines
    def _removeScriptFix(self, parse: bool = False) -> str:
        """
        Removes the dedicated section of the code in the .ini file that this script has made

        Parameters
        ----------
        parse: :class:`bool`
            Whether to keep track of the Blend.buf files that also need to be removed :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``False``

        Returns
        -------
        :class:`str`
            The new text content of the .ini file
        """

        if (not parse):
            self._fileTxt = re.sub(self._fixRemovalPattern, "", self._fileTxt)
        else:
            removedSectionsIndices = []
            txtLinesToRemove = []

            # retrieve the indices the dedicated section is located
            rangesToRemove = [match.span() for match in re.finditer(self._fixRemovalPattern, self._fileTxt)]
            for range in rangesToRemove:
                start = range[0]
                end = range[1]
                txtLines = TextTools.getTextLines(self._fileTxt[start : end])

                removedSectionsIndices.append(range)
                txtLinesToRemove += txtLines

            # retrieve the names of the sections the dedicated sections reference
            sectionNames = set()
            for line in txtLinesToRemove:
                if (re.match(self._sectionPattern, line)):
                    sectionName = self._getSectionName(line)
                    sectionNames.add(sectionName)

            resourceSections = self._getRemovalResource(sectionNames)

            # get the Blend.buf files that need to be removed
            self._makeRemovalRemapModels(resourceSections)
            
            # remove the dedicated section
            self._fileTxt = TextTools.removeParts(self._fileTxt, removedSectionsIndices)

        self.fileTxt = self._fileTxt.strip()
        result = self.write()

        self.clearRead()
        self._isFixed = False
        return result
    
    @_readLines
    def _removeFixSections(self, parse: bool = False) -> str:
        """
        Removes the [.*RemapBlend.*] sections of the .ini file that this script has made

        Parameters
        ----------
        parse: :class:`bool`
            Whether to keep track of the Blend.buf files that also need to be removed :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``False``

        Returns
        -------
        :class:`str`
            The new text content of the .ini file
        """

        if (not parse):
            self.removeSectionOptions(self._removalPattern)
        else:
            sectionsToRemove = self.getSectionOptions(self._removalPattern, postProcessor = self._removeSection)

            sectionNames = set()
            removedSectionIndices = []

            # get the indices and sections to remove
            for sectionName in sectionsToRemove:
                sectionRanges = sectionsToRemove[sectionName]
                sectionNames.add(sectionName)

                for range in sectionRanges:
                    removedSectionIndices.append(range)

            resourceSections = self._getRemovalResource(sectionNames)
            self._makeRemovalRemapModels(resourceSections)
            self.fileLines = TextTools.removeLines(self.fileLines, removedSectionIndices)

        result = self.write()
        self._removedSectionsIndices = None

        self.clearRead()
        self._isFixed = False
        return result

    def _removeFix(self, parse: bool = False) -> str:
        """
        Removes any previous changes that were probably made by this script :raw-html:`<br />` :raw-html:`<br />`

        For the .ini file will remove:

        #. All code surrounded by the *'---...--- .* Fix ---...----'* header/footer
        #. All `sections`_ containing the keywords ``RemapBlend``

        Parameters
        ----------
        parse: :class:`bool`
            Whether to keep track of the Blend.buf files that also need to be removed :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``False``

        Returns
        -------
        :class:`str`
            The new text content of the .ini file with the changes removed
        """

        self._removeScriptFix(parse = parse)    
        result = self._removeFixSections(parse = parse)
        return result

    @_readLines
    def removeFix(self, keepBackups: bool = True, fixOnly: bool = False, parse: bool = False) -> str:
        """
        Removes any previous changes that were probably made by this script and creates backup copies of the .ini file

        .. note::
            For more info about what gets removed from the .ini file, see :meth:`IniFile._removeFix`

        Parameters
        ----------
        keepBackup: :class:`bool`
            Whether we want to make a backup copy of the .ini file :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``True``

        fixOnly: :class:`bool`
            Whether we are only fixing the .ini file without removing any previous changes :raw-html:`<br />` :raw-html:`<br />`

            .. note::
                If this value is set to ``True``, then the previous changes made by this script will not be removed

            **Default**: ``False``

        parse: :class:`bool`
            Whether to also parse for the .*RemapBlend.buf files that need to be removed

        Returns
        -------
        :class:`str`
            The new text content of the .ini file with the changes removed
        """

        if (keepBackups and not fixOnly and self._filePath is not None):
            self.print("log", f"Creating Backup for {self._filePath.base}")
            self.disIni(makeCopy = True)

        if (fixOnly):
            return self._fileTxt

        if (self._filePath is not None):
            self.print("log", f"Removing any previous changes from this script in {self._filePath.base}")

        result = self._removeFix(parse = parse)
        return result
    
    def _makeRemapModel(self, ifTemplate: IfTemplate, toFix: Optional[Set[str]] = None, getFixedFile: Optional[Callable[[str], str]] = None) -> RemapBlendModel:
        """
        Creates the data needed for fixing a particular ``[Resource.*Blend.*]`` `section`_ in the .ini file

        Parameters
        ----------
        ifTemplate: :class:`IfTemplate`
            The particular `section`_ to extract data

        toFix: Optional[Set[:class:`str`]]
            The names of the mods to fix :raw-html:`<br />` :raw-html:`<br />`

            If this value is ``None``, then will used the names of the mods to fix from this class :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        getFixedFile: Optional[Callable[[:class:`str`, :class:`str`], :class:`str`]]
            The function for transforming the file path of a found .*Blend.buf file into a .*RemapBlend.buf file :raw-html:`<br />` :raw-html:`<br />`

            If this value is ``None``, then will use :meth:`IniFile.getFixedBlendFile` :raw-html:`<br />` :raw-html:`<br />`

            The parameters for the function are:

                # The path to the original file
                # The type of mod to fix to

            **Default**: ``None``

        Returns
        -------
        :class:`RemapBlendModel`
            The data for fixing the particular 
        """

        folderPath = self.folder

        if (toFix is None):
            toFix = self._toFix

        if (getFixedFile is None):
            getFixedFile = self.getFixedBlendFile

        origBlendPaths = {}
        fixedBlendPaths = {}
        partIndex = 0

        for part in ifTemplate:
            if (isinstance(part,str)):
                partIndex += 1
                continue

            origBlendFile = None
            try:
                origBlendFile = FileService.parseOSPath(part['filename'])
            except KeyError:
                partIndex += 1
                continue
            
            origBlendPaths[partIndex] = origBlendFile

            for modName in toFix:
                fixedBlendPath = getFixedFile(origBlendFile, modName = modName)
                try:
                    fixedBlendPaths[partIndex]
                except KeyError:
                    fixedBlendPaths[partIndex] = {}

                fixedBlendPaths[partIndex][modName] = fixedBlendPath

            partIndex += 1

        remapBlendModel = RemapBlendModel(folderPath, fixedBlendPaths, origBlendPaths = origBlendPaths)
        return remapBlendModel


    #_makeRemovalRemapModels(sectionNames): Retrieves the data needed for removing Blend.buf files from the .ini file
    def _makeRemovalRemapModels(self, sectionNames: Set[str]):
        for sectionName in sectionNames:
            ifTemplate = None
            try:
                ifTemplate = self._sectionIfTemplates[sectionName]
            except:
                continue

            self.remapBlendModels[sectionName] = self._makeRemapModel(ifTemplate, toFix = {""}, getFixedFile = lambda origFile, modName: origFile)


    def _makeRemapModels(self, resourceGraph: IniSectionGraph, toFix: Optional[Set[str]] = None, getFixedFile: Optional[Callable[[str], str]] = None) -> Dict[str, RemapBlendModel]:
        """
        Creates all the data needed for fixing the ``[Resource.*Blend.*]`` `sections`_ in the .ini file

        Parameters
        ----------
        resourceGraph: :class:`IniSectionGraph`
            The graph of `sections`_ for the resources

        toFix: Optional[Set[:class:`str`]]
            The names of the mods to fix :raw-html:`<br />` :raw-html:`<br />`

            If this value is ``None``, then will used the names of the mods to fix from this class :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        getFixedFile: Optional[Callable[[:class:`str`], :class:`str`]]
            The function for transforming the file path of a found .*Blend.buf file into a .*RemapBlend.buf file :raw-html:`<br />` :raw-html:`<br />`

            If this value is ``None``, then will use :meth:`IniFile.getFixedBlendFile` :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        Returns
        -------
        Dict[:class:`str`, :class:`RemapBlendModel`]
            The data for fixing the resource `sections`_

            The keys are the original names for the resource `sections`_ and the values are the required data for fixing the `sections`_
        """

        resourceCommands = resourceGraph.sections
        for resourceKey in resourceCommands:
            resourceIftemplate = resourceCommands[resourceKey]
            remapBlendModel = self._makeRemapModel(resourceIftemplate, toFix = toFix, getFixedFile = getFixedFile)
            self.remapBlendModels[resourceKey] = remapBlendModel

        return self.remapBlendModels

    def _getSubCommands(self, ifTemplate: IfTemplate, currentSubCommands: Set[str], subCommands: Set[str], subCommandLst: List[str]):
        for partIndex in ifTemplate.calledSubCommands:
            subCommand = ifTemplate.calledSubCommands[partIndex]
            if (subCommand not in subCommands):
                currentSubCommands.add(subCommand)
                subCommands.add(subCommand)
                subCommandLst.append(subCommand)

    def _getCommandIfTemplate(self, sectionName: str, raiseException: bool = True) -> Optional[IfTemplate]:
        """
        Retrieves the :class:`IfTemplate` for a certain `section`_ from `IniFile._sectionIfTemplate`

        Parameters
        ----------
        sectionName: :class:`str`
            The name of the `section`_

        raiseException: :class:`bool`
            Whether to raise an exception when the section's :class:`IfTemplate` is not found

        Raises
        ------
        :class:`KeyError`
            If the :class:`IfTemplate` for the `section`_ is not found and ``raiseException`` is set to `True`

        Returns
        -------
        Optional[:class:`IfTemplate`]
            The corresponding :class:`IfTemplate` for the `section`_
        """
        try:
            ifTemplate = self._sectionIfTemplates[sectionName]
        except Exception as e:
            if (raiseException):
                raise KeyError(f"The section by the name '{sectionName}' does not exist") from e
            else:
                return None
        else:
            return ifTemplate

    def _getBlendResources(self, blendResources: Set[str], blendCommandsGraph: IniSectionGraph):
        """
        Retrieves all the referenced resources that were called by `sections`_ related to the ``[TextureOverride.*Blend.*]`` `sections`_

        Parameters
        ----------
        blendResources: Set[:class:`str`]
            The result for all the resource `sections`_ that were referenced

        blendCommandsGraph: :class:`IniSectionGraph`
            The subgraph for all the `sections`_ related to the ``[TextureOverride.*Blend.*]`` `sections`_
        """

        blendSections = blendCommandsGraph.sections
        for sectionName in blendSections:
            ifTemplate = blendSections[sectionName]

            for part in ifTemplate:
                if (isinstance(part, str)):
                    continue

                if (self._isIfTemplateResource(part)):
                    resource = self._getIfTemplateResourceName(part)
                    blendResources.add(resource)

    def _getCommands(self, sectionName: str, subCommands: Set[str], subCommandLst: List[str]):
        """
        Low level function for retrieving all the commands/`sections`_ that are called from a certain `section`_ in the .ini file

        Parameters
        ----------
        sectionName: :class:`str`
            The name of the `section`_ we are starting from

        subCommands: Set[:class:`str`]
            The result for all of the `sections`_ that were called

        subCommandLst: List[:class:`str`]
            The result for all of the `sections`_ that were called while maintaining the order
            the `sections`_ are called in the call stack

        Raises
        ------
        :class:`KeyError`
            If the :class:`IfTemplate` is not found for some `section`_
        """

        currentSubCommands = set()
        ifTemplate = self._getCommandIfTemplate(sectionName)

        # add in the current command if it has not been added yet
        if (sectionName not in subCommands):
            subCommands.add(sectionName)
            subCommandLst.append(sectionName)

        # get all the unvisited subcommand sections to visit
        self._getSubCommands(ifTemplate, currentSubCommands, subCommands, subCommandLst)

        # visit the children subcommands that have not been visited yet
        for sectionName in currentSubCommands:
            self._getCommands(sectionName, subCommands, subCommandLst)


    # _getTargetHashAndIndexSections(blendCommandNames): Retrieves the sections with target hashes and indices
    def _getTargetHashAndIndexSections(self, blendCommandNames: Set[str]) -> Set[IfTemplate]:
        if (self._type is None and self.defaultModType is None):
            return set()
        
        type = self._type
        if (self._type is None):
            type = self.defaultModType

        result = {}
        hashes = set(type.hashes.fromAssets)
        indices = set(type.indices.fromAssets)
        
        # get the sections with the hashes/indices
        for sectionName in self._sectionIfTemplates:
            ifTemplate = self._sectionIfTemplates[sectionName]
            if (sectionName in blendCommandNames):
                continue

            if (hashes.intersection(ifTemplate.hashes) or indices.intersection(ifTemplate.indices)):
                result[sectionName] = ifTemplate

        return result

    # parse(): Parses the merged.ini file for any info needing to keep track of
    def parse(self):
        """
        Parses the .ini file

        Raises
        ------
        :class:`KeyError`
            If a certain resource `section`_ is not found :raw-html:`<br />` :raw-html:`<br />`
            
            (either the name of the `section`_ is not found in the .ini file or the `section`_ was skipped due to some error when parsing the `section`_)
        """

        self._blendCommandsGraph.build(newTargetSections = [], newAllSections = {})
        self._resourceCommandsGraph.build(newTargetSections = [], newAllSections = {})
        self.remapBlendModels = {}

        self.getIfTemplates(flush = True)
        if (self.defaultModType is not None and self._textureOverrideBlendSectionName is not None and self._textureOverrideBlendRoot is None):
            self._textureOverrideBlendRoot = self._textureOverrideBlendSectionName

        try:
            self._sectionIfTemplates[self._textureOverrideBlendRoot]
        except:
            return

        blendResources = set()

        # build the blend commands DFS forest
        subCommands = { self._textureOverrideBlendRoot }
        self._blendCommandsGraph.build(newTargetSections = subCommands, newAllSections = self._sectionIfTemplates)

        # build the DFS forest for the other sections that contain target hashes/indices that are not part of the blend commands
        hashIndexSections = self._getTargetHashAndIndexSections(set(self._blendCommandsGraph.sections.keys()))
        self._nonBlendHashIndexCommandsGraph.build(newTargetSections = hashIndexSections, newAllSections= self._sectionIfTemplates)

        # keep track of all the needed blend dependencies
        self._getBlendResources(blendResources, self._blendCommandsGraph)

        # sort the resources
        resourceCommandLst = list(map(lambda resourceName: (resourceName, self.getMergedResourceIndex(resourceName)), blendResources))
        resourceCommandLst.sort(key = cmp_to_key(self._compareResources))
        resourceCommandLst = list(map(lambda resourceTuple: resourceTuple[0], resourceCommandLst))

        # keep track of all the subcommands that the resources call
        self._resourceCommandsGraph.build(newTargetSections = resourceCommandLst, newAllSections = self._sectionIfTemplates)

        # get the required files that need fixing
        self._setToFix()
        self._makeRemapNames()
        self._makeRemapModels(self._resourceCommandsGraph)

    def fix(self, keepBackup: bool = True, fixOnly: bool = False) -> str:
        """
        Fixes the .ini file

        Parameters
        ----------
        keepBackup: :class:`bool`
            Whether we want to make a backup copy of the .ini file :raw-html:`<br />` :raw-html:`<br />`

            **Default**: `True`

        fixOnly: :class:`bool`
            Whether we are only fixing the .ini file without removing any previous changes :raw-html:`<br />` :raw-html:`<br />`

            **Default**: `False`

        Returns
        -------
        :class:`str`
            The new content of the .ini file which includes the fix
        """

        fix = ""
        fix += self.getFixStr(fix = fix)
        result = self.injectAddition(f"\n\n{fix}", beforeOriginal = False, keepBackup = keepBackup, fixOnly = fixOnly)
        self._isFixed = True
        return result
##### EndScript