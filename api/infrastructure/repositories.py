import os
import pandas as pd
from typing import List
from core.entities import PatientReport, Disease
from core.ports import DataRepositoryPort


class FileDataRepository(DataRepositoryPort):
    """
    Gateway de dados isolado encarregado por realizar as operações de
    banco de dados.
    """

    def __init__(self, relatos_path: str, ontologia_path: str):
        self._relatos_path = relatos_path
        self._ontologia_path = ontologia_path

    def get_patient_reports(self) -> List[PatientReport]:
        try:
            with open(self._relatos_path, "r", encoding="utf-8") as f:
                lines = [linha.strip() for linha in f if linha.strip()]
                return [PatientReport(text=line) for line in lines]
        except FileNotFoundError:
            print(f"Erro: Arquivo '{self._relatos_path}' não encontrado.")
            return []

    def get_diseases_ontology(self) -> List[Disease]:
        try:
            ontologia = pd.read_csv(self._ontologia_path)
            diseases = []
            for _, row in ontologia.iterrows():
                disease_name = row["Doenca_Associada"]
                symptoms = str(row["Sintomas_Base"])
                diseases.append(Disease(name=disease_name, symptoms_text=symptoms))
            return diseases
        except Exception as e:
            print(f"Erro ao ler '{self._ontologia_path}': {e}")
            return []
