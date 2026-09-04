from abc import ABC, abstractmethod

from usm.pack_file import PACKFile


class PackParser(ABC):

    @abstractmethod
    def read(self, file: str) -> PACKFile:
        ...

    @abstractmethod
    def extract(self, file: str) -> None:
        ...

    @abstractmethod
    def build(self, name: str, pack: PACKFile) -> None:
        ...

    def list(self, file: str) -> None:
        print(f"Listing is not supported by {type(self).__name__}.")
