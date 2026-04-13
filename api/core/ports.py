from abc import ABC, abstractmethod
from typing import List, Tuple
from .entities import PatientReport, Disease


class DataRepositoryPort(ABC):
    @abstractmethod
    def get_patient_reports(self) -> List[PatientReport]:
        pass

    @abstractmethod
    def get_diseases_ontology(self) -> List[Disease]:
        pass


class NLPServicePort(ABC):
    @abstractmethod
    def train(self, documents: List[str]) -> None:
        pass

    @abstractmethod
    def find_most_similar(self, query: str) -> Tuple[int, float]:
        """Retorna (índice_do_mais_similar, pontuação_de_confiança)"""
        pass
