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
import os
from collections import deque, defaultdict
from typing import Optional, Dict, Set, DefaultDict, Callable, List
##### EndExtImports

##### LocalImports
from .constants.FilePathConsts import FilePathConsts
from .constants.FileTypes import FileTypes
from .controller.enums.CommandOpts import CommandOpts
from .constants.FileExt import FileExt
from .constants.FileEncodings import FileEncodings
from .constants.FilePrefixes import FilePrefixes
from .exceptions.InvalidModType import InvalidModType
from .exceptions.ConflictingOptions import ConflictingOptions
from .view.Logger import Logger
from .model.modtypes.ModTypes import ModTypes
from .model.modtypes.ModType import ModType
from .model.Mod import Mod
from .model.IniFile import IniFile
from .tools.files.FileService import FileService
from .tools.DictTools import DictTools
from .tools.Heading import Heading
##### EndLocalImports


##### Script
class RemapService():
    """
    The overall class for remapping modss

    Parameters
    ----------
    path: Optional[:class:`str`]
        The file location of where to run the fix. :raw-html:`<br />` :raw-html:`<br />`

        If this attribute is set to ``None``, then will run the fix from wherever this class is called :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    keepBackups: :class:`bool`
        Whether to keep backup versions of any .ini files that the script fixes :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``True``

    fixOnly: :class:`bool`
        Whether to only fix the mods without removing any previous changes this fix script may have made :raw-html:`<br />` :raw-html:`<br />`

        .. warning::
            if this is set to ``True`` and :attr:`undoOnly` is also set to ``True``, then the fix will not run and will throw a :class:`ConflictingOptions` exception

        :raw-html:`<br />`

        **Default**: ``False``

    undoOnly: :class:`bool`
        Whether to only undo the fixes previously made by the fix :raw-html:`<br />` :raw-html:`<br />`

        .. warning::
            if this is set to ``True`` and :attr:`fixOnly` is also set to ``True``, then the fix will not run and will throw a :class:`ConflictingOptions` exception

        :raw-html:`<br />`

        **Default**: ``True``

    readAllInis: :class:`bool`
        Whether to read all the .ini files that the fix encounters :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``False``

    types: Optional[:class:`str`]
        A string containing the names for all the types of mods to fix. Each type of mod is seperated using a comma (,)  :raw-html:`<br />` :raw-html:`<br />`

        If this argument is the empty string or this argument is ``None``, then will fix all the types of mods supported by this fix :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    defaultType: Optional[:class:`str`]
        The name for the type to use if a mod has an unidentified type :raw-html:`<br />` :raw-html:`<br />`

        If this value is ``None``, then mods with unidentified types will be skipped :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    log: Optional[:class:`str`]
        The folder location to log the run of the fix into a seperate text file :raw-html:`<br />` :raw-html:`<br />`

        If this value is ``None``, then will not log the fix :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    verbose: :class:`bool`
        Whether to print the progress for fixing mods :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``True``

    handleExceptions: :class:`bool`
        When an exception is caught, whether to silently stop running the fix :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``False``

    version: Optional[:class:`float`]
        The game version we want the fix to be compatible with :raw-html:`<br />` :raw-html:`<br />`

        If This value is ``None``, then will retrieve the hashes/indices of the latest version. :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    Attributes
    ----------
    _loggerBasePrefix: :class:`str`
        The prefix string for the logger used when the fix returns back to the original directory that it started to run

    logger: :class:`Logger`
        The logger used to pretty print messages

    _path: :class:`str`
        The file location of where to run the fix.

    keepBackups: :class:`bool`
        Whether to keep backup versions of any .ini files that the script fixes

    fixOnly: :class:`bool`
        Whether to only fix the mods without removing any previous changes this fix script may have made

    undoOnly: :class:`bool`
        Whether to only undo the fixes previously made by the fix

    readAllInis: :class:`bool`
        Whether to read all the .ini files that the fix encounters

    types: Set[:class:`ModType`]
        All the types of mods that will be fixed.

    defaultType: Optional[:class:`ModType`]
        The type to use if a mod has an unidentified type

    verbose: :class:`bool`
        Whether to print the progress for fixing mods

    version: Optional[:class:`float`]
        The game version we want the fix to be compatible with :raw-html:`<br />` :raw-html:`<br />`

        If This value is ``None``, then will retrieve the hashes/indices of the latest version.

    handleExceptions: :class:`bool`
        When an exception is caught, whether to silently stop running the fix

    _logFile: :class:`str`
        The file path of where to generate a log .txt file

    _pathIsCWD: :class:`bool`
        Whether the filepath that the program runs from is the current directory where this module is loaded

    modsFixed: :class:`int`
        The number of mods that have been fixed

    skippedMods: Dict[:class:`str`, :class:`Exception`]
        All the mods that have been skipped :raw-html:`<br />` :raw-html:`<br />`

        The keys are the absolute path to the mod folder and the values are the exception that caused the mod to be skipped

    blendsFixed: Set[:class:`str`]
        The absolute paths to all the Blend.buf files that have been fixed

    skippedBlendsByMods: DefaultDict[:class:`str`, Dict[:class:`str`, :class:`Exception`]]
        The RemapBlend.buf files that got skipped :raw-html for each mod :raw-html:`<br />` :raw-html:`<br />`

        * The outer key is the absolute path to the mod folder
        * The inner key is the absolute path to the RemapBlend.buf file
        * The value in the inner dictionary is the exception that caused the RemapBlend.buf file to be skipped

    skippedBlends: Dict[:class:`str`, :class:`Exception`]
        The RemapBlend.buf files that got skipped  :raw-html:`<br />` :raw-html:`<br />`

        The keys are the absolute path to the RemapBlend.buf file and the values are the exception that caused the RemapBlend.buf file to be skipped

    inisFixed: Set[:class:`str`]
        The absolute paths to the fixed .ini files

    inisSkipped: Dict[:class:`str`, :class:`Exception`]
        The .ini files that got skipped :raw-html:`<br />` :raw-html:`<br />`

        The keys are the absolute file paths to the .ini files and the values are exceptions that caused the .ini file to be skipped

    removedRemapBlends: Set[:class:`str`]
        Previous RemapBlend.buf files that are removed

    undoedInis: Set[:class:`str`]
        .ini files that got cleared out of any traces of previous fixes

        .. note::
            These .ini files may or may not have been previously fixed. A path to some .ini file in this attribute **DOES NOT** imply
            that the .ini file previously had a fix
    """

    def __init__(self, path: Optional[str] = None, keepBackups: bool = True, fixOnly: bool = False, undoOnly: bool = False, 
                 readAllInis: bool = False, types: Optional[str] = None, defaultType: Optional[str] = None, log: Optional[str] = None, 
                 verbose: bool = True, handleExceptions: bool = False, version: Optional[float] = None):
        self.log = log
        self._loggerBasePrefix = ""
        self.logger = Logger(logTxt = log, verbose = verbose)
        self._path = path
        self.keepBackups = keepBackups
        self.fixOnly = fixOnly
        self.undoOnly = undoOnly
        self.readAllInis = readAllInis
        self.types = types
        self.defaultType = defaultType
        self.verbose = verbose
        self.version = version
        self.handleExceptions = handleExceptions
        self._pathIsCwd = False
        self.__errorsBeforeFix = None

        # certain statistics about the fix
        self.modsFixed = 0
        self.skippedMods: Dict[str, Exception] = {}
        self.blendsFixed: Set[str] = set()
        self.skippedBlendsByMods: DefaultDict[str, Dict[str, Exception]] = defaultdict(lambda: {})
        self.skippedBlends: Dict[str, Exception] = {}
        self.inisFixed = set()
        self.inisSkipped: Dict[str, Exception] = {}
        self.removedRemapBlends: Set[str] = set()
        self.undoedInis: Set[str] = set()
        self._visitedRemapBlendsAtRemoval: Set[str] = set()

        self._setupModPath()
        self._setupModTypes()
        self._setupDefaultModType()

        if (self.__errorsBeforeFix is None):
            self._printModsToFix()

    @property
    def pathIsCwd(self):
        """
        Whether the filepath that the program runs from is the current directory where this module is loaded

        :getter: Returns whether the filepath that the program runs from is the current directory of where the module is loaded
        :type: :class:`bool`
        """

        return self._pathIsCwd
    
    @property
    def path(self) -> str:
        """
        The filepath of where the fix is running from

        :getter: Returns the path of where the fix is running
        :setter: Sets the path for where the fix runs
        :type: :class:`str`
        """

        return self._path
    
    @path.setter
    def path(self, newPath: Optional[str]):
        self._path = newPath
        self._setupModPath()
        self.clear()

    @property
    def log(self) -> str:
        """
        The folder location to log the run of the fix into a seperate text file

        :getter: Returns the file path to the log
        :setter: Sets the path for the log
        :type: :class:`str`
        """

        return self._log
    
    @log.setter
    def log(self, newLog: Optional[str]):
        self._log = newLog
        self._setupLogPath()

    def clear(self, clearLog: bool = True):
        """
        Clears up all the saved data

        Paramters
        ---------
        clearLog: :class:`bool`
            Whether to also clear out any saved data in the logger
        """

        self.modsFixed = 0
        self.skippedMods = {}
        self.blendsFixed = set()
        self.skippedBlendsByMods = defaultdict(lambda: {})
        self.skippedBlends = {}
        self.inisFixed = set()
        self.inisSkipped = {}
        self.removedRemapBlends = set()
        self.undoedInis = set()
        self._visitedRemapBlendsAtRemoval = set()

        if (clearLog):
            self.logger.clear()
    
    def _setupModPath(self):
        """
        Sets the filepath of where the fix will run from
        """

        self._pathIsCwd = False
        if (self._path is None):
            self._path = FilePathConsts.DefaultPath
            self._pathIsCwd = True
            return

        self._path = FileService.parseOSPath(self._path)
        self._path = FileService.parseOSPath(os.path.abspath(self._path))
        self._pathIsCwd = (self._path == FilePathConsts.DefaultPath)

    def _setupLogPath(self):
        """
        Sets the folder path for where the log file will be stored
        """

        if (self._log is not None):
            self._log = FileService.parseOSPath(os.path.join(self._log, FileTypes.Log.value))

    def _setupModTypes(self):
        """
        Sets the types of mods that will be fixed
        """

        if (isinstance(self.types, set)):
            return

        modTypes = set()
        if (self.types is None or self.readAllInis):
            modTypes = ModTypes.getAll()

        # search for the types of mods to fix
        else:
            typesLst = self.types.split(",")

            for typeStr in typesLst:
                modType = ModTypes.search(typeStr)
                modTypeFound = bool(modType is not None)

                if (modTypeFound):
                    modTypes.add(modType)
                elif (self.__errorsBeforeFix is None):
                    self.__errorsBeforeFix = InvalidModType(typeStr)
                    return

        self.types = modTypes

    def _setupDefaultModType(self):
        """
        Sets the default mod type to be used for an unidentified mod
        """

        if (not self.readAllInis):
            self.defaultType = None
        elif (self.defaultType is None):
            self.defaultType = ModTypes.Raiden.value
            return

        if (self.defaultType is None or isinstance(self.defaultType, ModType)):
            return

        self.defaultType = ModTypes.search(self.defaultType)

        if (self.defaultType is None and self.__errorsBeforeFix is None):
            self.__errorsBeforeFix = InvalidModType(self.defaultType)

    def _printModsToFix(self):
        """
        Prints out the types of mods that will be fixed
        """

        self.logger.includePrefix = False

        self.logger.openHeading("Types of Mods To Fix", 5)
        self.logger.space()

        if (not self.types):
            self.logger.log("All mods")
        else:
            for type in self.types:
                self.logger.bulletPoint(f"{type.name}")
        
        self.logger.space()
        self.logger.closeHeading()
        self.logger.split() 
        self.logger.includePrefix = True
    
    # fixes an ini file in a mod
    def fixIni(self, ini: IniFile, mod: Mod, fixedRemapBlends: Set[str]) -> bool:
        """
        Fixes an individual .ini file for a particular mod

        .. note:: 
            For more info about how we define a 'mod', go to :class:`Mod`

        Parameters
        ----------
        ini: :class:`IniFile`
            The .ini file to fix

        mod: :class:`Mod`
            The mod being fixed

        fixedRemapBlends: Set[:class:`str`]
            All of the RemapBlend.buf files that have already been fixed.

        Returns
        -------
        :class:`bool`
            Whether the particular .ini file has just been fixed
        """

        # check if the .ini is belongs to some mod
        if (ini is None or not ini.isModIni):
            return False

        if (self.undoOnly):
            return True

        fileBaseName = os.path.basename(ini.file)
        iniFullPath = FileService.absPathOfRelPath(ini.file, mod.path)

        if (iniFullPath in self.inisSkipped):
            self.logger.log(f"the ini file, {fileBaseName}, has alreaedy encountered an error")
            return False
        
        if (iniFullPath in self.inisFixed):
            self.logger.log(f"the ini file, {fileBaseName}, is already fixed")
            return True

        # parse the .ini file
        self.logger.log(f"Parsing {fileBaseName}...")
        ini.parse()

        if (ini.isFixed):
            self.logger.log(f"the ini file, {fileBaseName}, is already fixed")
            return True

        # fix the blends
        self.logger.log(f"Fixing the {FileTypes.Blend.value} files for {fileBaseName}...")
        currentBlendsFixed, currentBlendsSkipped = mod.correctBlend(fixedRemapBlends = fixedRemapBlends, skippedBlends = self.skippedBlends, fixOnly = self.fixOnly)
        self.blendsFixed = self.blendsFixed.union(currentBlendsFixed)

        if (currentBlendsSkipped):
            DictTools.update(self.skippedBlendsByMods[mod.path], currentBlendsSkipped)

        # writing the fixed file
        self.logger.log(f"Making the fixed ini file for {fileBaseName}")
        ini.fix(keepBackup = self.keepBackups, fixOnly = self.fixOnly)

        return True

    # fixes a mod
    def fixMod(self, mod: Mod, fixedRemapBlends: Set[str]) -> bool:
        """
        Fixes a particular mod

        .. note:: 
            For more info about how we define a 'mod', go to :class:`Mod`

        Parameters
        ----------
        mod: :class:`Mod`
            The mod being fixed

        fixedRemapBlends: Set[:class:`str`]
            all of the RemapBlend.buf files that have already been fixed.

        Returns
        -------
        :class:`bool`
            Whether the particular mod has just been fixed
        """

        # remove any backups
        if (not self.keepBackups):
            mod.removeBackupInis()

        for ini in mod.inis:
            ini.checkIsMod()

        # undo any previous fixes
        if (not self.fixOnly):
            undoedInis, removedRemapBlends = mod.removeFix(self.blendsFixed, self.inisFixed, self._visitedRemapBlendsAtRemoval, self.inisSkipped, keepBackups = self.keepBackups, fixOnly = self.fixOnly)
            self.removedRemapBlends = self.removedRemapBlends.union(removedRemapBlends)
            self.undoedInis = self.undoedInis.union(undoedInis)

        result = False
        firstIniException = None
        inisLen = len(mod.inis)

        for i in range(inisLen):
            ini = mod.inis[i]
            iniFullPath = FileService.absPathOfRelPath(ini.file, mod.path)
            iniIsFixed = False

            try:
                iniIsFixed = self.fixIni(ini, mod, fixedRemapBlends)
            except Exception as e:
                self.logger.handleException(e)
                self.inisSkipped[iniFullPath] = e 

                if (firstIniException is None):
                    firstIniException = e

            if (firstIniException is None and iniFullPath in self.inisSkipped):
                firstIniException = self.inisSkipped[iniFullPath]

            result = (result or iniIsFixed)

            if (not iniIsFixed):
                continue
            
            if (i < inisLen - 1):
                self.logger.space()

            self.inisFixed.add(iniFullPath)

        if (not result and firstIniException is not None):
            self.skippedMods[mod.path] = firstIniException

        return result
    
    def addTips(self):
        """
        Prints out any useful tips for the user to know
        """

        self.logger.includePrefix = False

        if (not self.undoOnly or self.keepBackups):
            self.logger.split()
            self.logger.openHeading("Tips", sideLen = 10)

            if (self.keepBackups):
                self.logger.bulletPoint(f'Hate deleting the "{FilePrefixes.BackupFilePrefix.value}" {FileExt.Ini.value}/{FileExt.Txt.value} files yourself after running this script? (cuz I know I do!) Run this script again (on CMD) using the {CommandOpts.DeleteBackup.value} option')

            if (not self.undoOnly):
                self.logger.bulletPoint(f"Want to undo this script's fix? Run this script again (on CMD) using the {CommandOpts.Revert.value} option")

            if (not self.readAllInis):
                self.logger.bulletPoint(f"Were your {FileTypes.Ini.value}s not read? Run this script again (on CMD) using the {CommandOpts.All.value} option")

            self.logger.space()
            self.logger.log("For more info on command options, run this script (on CMD) using the --help option")
            self.logger.closeHeading()

        self.logger.includePrefix = True


    def reportSkippedAsset(self, assetName: str, assetDict: Dict[str, Exception], warnStrFunc: Callable[[str], str]):
        """
        Prints out the exception message for why a particular .ini file or Blend.buf file has been skipped

        Parameters
        ----------
        assetName: :class:`str`
            The name for the type of asset (files, folders, mods, etc...) that was skipped

        assetDict: Dict[:class:`str`, :class:`Exception`]
            Locations of where exceptions have occured for the particular asset :raw-html:`<br />` :raw-html:`<br />`

            The keys are the absolute folder paths to where the exception occured

        wantStrFunc: Callable[[:class:`str`], :class:`str`]
            Function for how we want to print out the warning for each exception :raw-html:`<br />` :raw-html:`<br />`

            Takes in the folder location of where the exception occured as a parameter
        """

        if (assetDict):
            message = f"\nWARNING: The following {assetName} were skipped due to warnings (see log above):\n\n"
            for dir in assetDict:
                message += warnStrFunc(dir)

            self.logger.error(message)
            self.logger.space()

    def warnSkippedBlends(self, modPath: str):
        """
        Prints out all of the Blend.buf files that were skipped due to exceptions

        Parameters
        ----------
        modPath: :class:`str`
            The absolute path to a particular folder
        """

        parentFolder = os.path.dirname(self._path)
        relModPath = FileService.getRelPath(modPath, parentFolder)
        modHeading = Heading(f"Mod: {relModPath}", 5)
        message = f"{modHeading.open()}\n\n"
        blendWarnings = self.skippedBlendsByMods[modPath]
        
        for blendPath in blendWarnings:
            relBlendPath = FileService.getRelPath(blendPath, self._path)
            message += self.logger.getBulletStr(f"{relBlendPath}:\n\t{Heading(type(blendWarnings[blendPath]).__name__, 3, '-').open()}\n\t{blendWarnings[blendPath]}\n\n")
        
        message += f"{modHeading.close()}\n"
        return message

    def reportSkippedMods(self):
        """
        Prints out all of the mods that were skipped due to exceptions

        .. note:: 
            For more info about how we define a 'mod', go to :class:`Mod`
        """

        self.reportSkippedAsset("mods", self.skippedMods, lambda dir: self.logger.getBulletStr(f"{dir}:\n\t{Heading(type(self.skippedMods[dir]).__name__, 3, '-').open()}\n\t{self.skippedMods[dir]}\n\n"))
        self.reportSkippedAsset(f"{FileTypes.Ini.value}s", self.inisSkipped, lambda file: self.logger.getBulletStr(f"{file}:\n\t{Heading(type(self.inisSkipped[file]).__name__, 3, '-').open()}\n\t{self.inisSkipped[file]}\n\n"))
        self.reportSkippedAsset(f"{FileTypes.Blend.value} files", self.skippedBlendsByMods, lambda dir: self.warnSkippedBlends(dir))

    def reportSummary(self):
        skippedMods = len(self.skippedMods)
        foundMods = self.modsFixed + skippedMods
        fixedBlends = len(self.blendsFixed)
        skippedBlends = len(self.skippedBlends)
        foundBlends = fixedBlends + skippedBlends
        fixedInis = len(self.inisFixed)
        skippedInis = len(self.inisSkipped)
        foundInis = fixedInis + skippedInis
        removedRemapBlends = len(self.removedRemapBlends)
        undoedInis = len(self.undoedInis)

        self.logger.openHeading("Summary", sideLen = 10)
        self.logger.space()
        
        modFixMsg = ""
        blendFixMsg = ""
        iniFixMsg = ""
        removedRemappedMsg = ""
        undoedInisMsg = ""
        if (not self.undoOnly):
            modFixMsg = f"Out of {foundMods} found mods, fixed {self.modsFixed} mods and skipped {skippedMods} mods"
            iniFixMsg = f"Out of the {foundInis} {FileTypes.Ini.value}s within the found mods, fixed {fixedInis} {FileTypes.Ini.value}s and skipped {skippedInis} {FileTypes.Ini.value}s"
            blendFixMsg = f"Out of the {foundBlends} {FileTypes.Blend.value} files within the found mods, fixed {fixedBlends} {FileTypes.Blend.value} files and skipped {skippedBlends} {FileTypes.Blend.value} files"
        else:
            modFixMsg = f"Out of {foundMods} found mods, remove fix from {self.modsFixed} mods and skipped {skippedMods} mods"

        if (not self.fixOnly and undoedInis > 0):
            undoedInisMsg = f"Removed fix from up to {undoedInis} {FileTypes.Ini.value}s"

            if (self.undoOnly):
                undoedInisMsg += f" and skipped {skippedInis} {FileTypes.Ini.value}s"

        if (not self.fixOnly and removedRemapBlends > 0):
            removedRemappedMsg = f"Removed {removedRemapBlends} old {FileTypes.RemapBlend.value} files"


        self.logger.bulletPoint(modFixMsg)
        if (iniFixMsg):
            self.logger.bulletPoint(iniFixMsg)

        if (blendFixMsg):
            self.logger.bulletPoint(blendFixMsg)

        if (undoedInisMsg):
            self.logger.bulletPoint(undoedInisMsg)

        if (removedRemappedMsg):
            self.logger.bulletPoint(removedRemappedMsg)

        self.logger.space()
        self.logger.closeHeading()

    def createLog(self):
        """
        Creates a log text file that contains all the text printed on the command line
        """

        if (self._log is None):
            return

        self.logger.includePrefix = False
        self.logger.space()

        self.logger.log(f"Creating log file, {FileTypes.Log.value}")

        self.logger.includePrefix = True

        with open(self._log, "w", encoding = FileEncodings.UTF8.value) as f:
            f.write(self.logger.loggedTxt)

    def createMod(self, path: Optional[str] = None, files: Optional[List[str]] = None) -> Mod:
        """
        Creates a mod

        .. note:: 
            For more info about how we define a 'mod', go to :class:`Mod`

        Parameters
        ----------
        path: Optional[:class:`str`]
            The absolute path to the mod folder. :raw-html:`<br />` :raw-html:`<br />`
            
            If this argument is set to ``None``, then will use the current directory of where this module is loaded

        files: Optional[List[:class:`str`]]
            The direct children files to the mod folder (does not include files located in a folder within the mod folder). :raw-html:`<br />` :raw-html:`<br />`

            If this parameter is set to ``None``, then the module will search the folders for you

        Returns
        -------
        :class:`Mod`
            The mod that has been created
        """

        path = FileService.getPath(path)
        mod = Mod(path = path, files = files, logger = self.logger, types = self.types, defaultType = self.defaultType, version = self.version)
        return mod

    def _fix(self):
        """
        The overall logic for fixing a bunch of mods

        For finding out which folders may contain mods, this function:
            #. recursively searches all folders from where the :attr:`RemapService.path` is located
            #. for every .ini file in a valid mod and every Blend.buf file encountered that is encountered, recursively search all the folders from where the .ini file or Blend.buf file is located

        .. note:: 
            For more info about how we define a 'mod', go to :class:`Mod`
        """

        if (self.__errorsBeforeFix is not None):
            raise self.__errorsBeforeFix

        if (self.fixOnly and self.undoOnly):
            raise ConflictingOptions([CommandOpts.FixOnly.value, CommandOpts.Revert.value])

        parentFolder = os.path.dirname(self._path)
        self._loggerBasePrefix = os.path.basename(self._path)
        self.logger.prefix = os.path.basename(FilePathConsts.DefaultPath)

        visitedDirs = set()
        visitingDirs = set()
        dirs = deque()
        dirs.append(self._path)
        visitingDirs.add(self._path)
        fixedRemapBlends = set()
    
        while (dirs):
            path = dirs.popleft()
            fixedMod = False

            # skip if the directory has already been visited
            if (path in visitedDirs):
                visitingDirs.remove(path)
                visitedDirs.add(path)
                continue 
            
            self.logger.split()

            # get the relative path to where the program runs
            self.logger.prefix = FileService.getRelPath(path, parentFolder)

            # try to make the mod, skip if cannot be made
            try:
                mod = self.createMod(path = path)
            except Exception as e:
                visitingDirs.remove(path)
                visitedDirs.add(path)
                continue
            
            # fix the mod
            try:
                fixedMod = self.fixMod(mod, fixedRemapBlends)
            except Exception as e:
                self.logger.handleException(e)
                if (mod.inis):
                    self.skippedMods[path] = e

            # get all the folders that could potentially be other mods
            modFiles, modDirs = FileService.getFilesAndDirs(path = path, recursive = True)

            if (mod.inis):
                for ini in mod.inis:
                    for _, blendModel in ini.remapBlendModels.items():
                        resourceModDirs = map(lambda partIndex: os.path.dirname(blendModel.origFullPaths[partIndex]), blendModel.origFullPaths) 
                        modDirs += resourceModDirs
            
            # add in all the folders that need to be visited
            for dir in modDirs:
                if (dir in visitedDirs):
                    continue

                if (dir not in visitingDirs):
                    dirs.append(dir)
                visitingDirs.add(dir)

            # increment the count of mods found
            if (fixedMod):
                self.modsFixed += 1

            visitingDirs.remove(path)
            visitedDirs.add(path)

        self.logger.split()
        self.logger.prefix = self._loggerBasePrefix
        self.reportSkippedMods()
        self.logger.space()
        self.reportSummary()


    def fix(self):
        """
        Fixes a bunch of mods

        see :meth:`_fix` for more info
        """
        
        try:
            self._fix()
        except Exception as e:
            if (self.handleExceptions):
                self.logger.handleException(e)
            else:
                self.createLog()
                raise e from e
        else:
            noErrors = bool(not self.skippedMods and not self.skippedBlendsByMods)

            if (noErrors):
                self.logger.space()
                self.logger.log("ENJOY")

            self.logger.split()

            if (noErrors):
                self.addTips()

        self.createLog()
##### EndScript