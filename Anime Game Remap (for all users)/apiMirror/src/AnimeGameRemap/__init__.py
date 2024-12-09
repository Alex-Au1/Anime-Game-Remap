
#
# ===== Note =====
#
# This library was auto-generated by AG Remap's APIMirrorBuilder tool,
#   a build system tool used in AG Remap's CI pipeline that creates a mirror for the existing
#   API source code since we cannot rename the original name of 'FixRaidenBoss2' to 'Anime Game Remap' in Pypi,
#   therefore, we decided to make a brand new package that mirrors the original API.
#
# ***** APIMirrorBuilder Stats *****
#
# Version: 1.0.0
# Authors: Albert Gold#2696
# Datetime Ran: Monday, December 09, 2024 08:50:51.137 AM UTC
# Run Hash: 0b2192f8-473e-46b2-a7f0-f9bd4bbfeefe
# 
# **********************************
# ================
#

# ===== Anime Game Remap (AG Remap) =====
# Authors: NK#1321, Albert Gold#2696
#
# if you used it to remap your mods pls give credit for "Nhok0169" and "Albert Gold#2696"
# Special Thanks:
#   nguen#2011 (for support)
#   SilentNightSound#7430 (for internal knowdege so wrote the blendCorrection code)
#   HazrateGolabi#1364 (for being awesome, and improving the code)

#
# ***** AG Remap Stats *****
#
# Version: 4.1.3
# Authors: NK#1321, Albert Gold#2696
# Datetime Compiled: Monday, December 09, 2024 08:50:51.137 AM UTC
# Build Hash: 49262131-c5e3-443b-9dd1-9b557818f4c0
#
# **************************
#

from FixRaidenBoss2 import Colours, ColourConsts, FileExt, FileTypes, FileEncodings, FilePrefixes, FileSuffixes, FilePathConsts, ImgFormats, IniKeywords, IniBoilerPlate, GIBuilder, IfPredPartType, ModTypeBuilder, ModTypes, ShortCommandOpts, CommandOpts, HashData, IndexData, VGRemapData, BadBlendData, BlendFileNotRecognized, ConflictingOptions, DuplicateFileException, Error, FileException, InvalidModType, MissingFileException, NoModType, RemapMissingBlendFile, Hashes, Indices, ModAssets, ModIdAssets, VGRemaps, BlendFile, File, IniFile, TextureFile, KeepFirstDict, BaseIniFixer, GIMIFixer, GIMIObjMergeFixer, GIMIObjRegEditFixer, GIMIObjReplaceFixer, GIMIObjSplitFixer, IniFixBuilder, MultiModFixer, BaseRegEditFilter, RegEditFilter, RegNewVals, RegRemap, RegRemove, RegTexAdd, RegTexEdit, BaseIniParser, GIMIObjParser, GIMIParser, IniParseBuilder, BaseIniRemover, IniRemover, IniRemoveBuilder, BasePixelFilter, ColourReplace, InvertAlpha, HighlightShadow, TempControl, BaseTexFilter, HueAdjust, BaseTexEditor, TexEditor, TexCreator, ModType, IfContentPart, IfPredPart, IfTemplate, IfTemplatePart, IniResourceModel, IniTexModel, Colour, ColourRange, IniSectionGraph, Mod, Model, FileStats, Version, VGRemap, Cache, LruCache, FileService, FilePath, Algo, Builder, DictTools, FlyweightBuilder, Heading, ListTools, TextTools, Logger, RemapService, remapMain

__all__ = ["Colours", "ColourConsts", "FileExt", "FileTypes", "FileEncodings", "FilePrefixes", "FileSuffixes", "FilePathConsts", "ImgFormats", "IniKeywords", "IniBoilerPlate", "GIBuilder", "IfPredPartType", "ModTypeBuilder", "ModTypes", "ShortCommandOpts", "CommandOpts", "HashData", "IndexData", "VGRemapData", "BadBlendData", "BlendFileNotRecognized", "ConflictingOptions", "DuplicateFileException", "Error", "FileException", "InvalidModType", "MissingFileException", "NoModType", "RemapMissingBlendFile", "Hashes", "Indices", "ModAssets", "ModIdAssets", "VGRemaps", "BlendFile", "File", "IniFile", "TextureFile", "KeepFirstDict", "BaseIniFixer", "GIMIFixer", "GIMIObjMergeFixer", "GIMIObjRegEditFixer", "GIMIObjReplaceFixer", "GIMIObjSplitFixer", "IniFixBuilder", "MultiModFixer", "BaseRegEditFilter", "RegEditFilter", "RegNewVals", "RegRemap", "RegRemove", "RegTexAdd", "RegTexEdit", "BaseIniParser", "GIMIObjParser", "GIMIParser", "IniParseBuilder", "BaseIniRemover", "IniRemover", "IniRemoveBuilder", "BasePixelFilter", "ColourReplace", "InvertAlpha", "HighlightShadow", "TempControl", "BaseTexFilter", "HueAdjust", "BaseTexEditor", "TexEditor", "TexCreator", "ModType", "IfContentPart", "IfPredPart", "IfTemplate", "IfTemplatePart", "IniResourceModel", "IniTexModel", "Colour", "ColourRange", "IniSectionGraph", "Mod", "Model", "FileStats", "Version", "VGRemap", "Cache", "LruCache", "FileService", "FilePath", "Algo", "Builder", "DictTools", "FlyweightBuilder", "Heading", "ListTools", "TextTools", "Logger", "RemapService", "remapMain"]