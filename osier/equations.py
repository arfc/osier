from abc import ABC, abstractmethod

class OsierEquation(ABC):

    def __init__(self) -> None:
        

    @abstractmethod
    def _do(self, technology_list, X):
        pass