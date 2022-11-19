from abc import ABC, abstractmethod

class OsierEquation(ABC):

    def __init__(self) -> None:
        pass        

    @abstractmethod
    def _do(self, technology_list, X):
        pass