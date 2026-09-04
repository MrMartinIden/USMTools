from .generic_mash_header import *
from .resource_directory import *
from .resource_pack_header import *


class PACKFile:
    pack_header: resource_pack_header
    mash_header: generic_mash_header
    directory: resource_directory
    file_size: int
    resources: dict[str, bytes]

    def __init__(self, pack_header, mash_header, directory, file_size, resources):
        self.pack_header = pack_header
        self.mash_header = mash_header
        self.directory = directory
        self.file_size = file_size
        self.resources = resources
