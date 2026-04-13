from typing import List
from .entities import DiagnosticResult
from .ports import DataRepositoryPort, NLPServicePort


class DiagnosePatientUseCase:
    """
    Orquestrador que executa o processo de diagnóstico.
    """

    def __init__(self, repository: DataRepositoryPort, nlp_service: NLPServicePort):
        self._repository = repository
        self._nlp_service = nlp_service

    def execute(self, confidence_threshold: float = 0.05) -> List[DiagnosticResult]:
        # Busca todas queixas de clientes e patologias base no banco
        reports = self._repository.get_patient_reports()
        diseases = self._repository.get_diseases_ontology()

        if not reports or not diseases:
            return []

        # Calcula a bag of words nos textos-sintoma mapeados nas doenças
        disease_texts = [d.symptoms_text for d in diseases]
        self._nlp_service.train(disease_texts)

        results = []
        # Analisa uma frase por vez, verificando as similaridades em matrizes de NLP
        for report in reports:
            best_idx, confidence = self._nlp_service.find_most_similar(report.text)

            if confidence > confidence_threshold:
                disease_name = diseases[best_idx].name
            else:
                disease_name = "Inconclusivo"

            results.append(
                DiagnosticResult(
                    report=report, suggested_disease=disease_name, confidence=confidence
                )
            )

        return results
