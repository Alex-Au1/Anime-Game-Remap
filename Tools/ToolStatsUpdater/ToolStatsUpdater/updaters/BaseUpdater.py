import sys

from ..constants.Paths import UtilitiesPath

sys.path.insert(1, UtilitiesPath)
from Utils.SoftwareMetadata import SoftwareMetadata


# BaseUpdater: Updates the software metadta for some source
class BaseUpdater():
    def __init__(self, src: str, softwareMetadata: SoftwareMetadata):
        self.src = src
        self.softwareMetadata = softwareMetadata

    # update(): Updates the source
    def update(self):
        pass