from core.entities import PatientReport, Disease
from core.use_cases import DiagnosePatientUseCase

class DummyDataRepository:
    def get_patient_reports(self):
        return [PatientReport(text="A minha cabeça não aguenta")]

    def get_diseases_ontology(self):
        return [Disease(name="Hipertensão Teste", symptoms_text="cabeça zumbido")]

class DummyNLPService:
    def train(self, documents):
        pass

    def find_most_similar(self, query):
        return (0, 0.99) # Sempre retorna o primeiro item com alta confiança da camada stub

def test_diagnose_patient_use_case():
    repo = DummyDataRepository()
    nlp = DummyNLPService()
    use_case = DiagnosePatientUseCase(repo, nlp)
    
    results = use_case.execute()
    
    assert len(results) == 1
    assert results[0].suggested_disease == "Hipertensão Teste"
    assert results[0].confidence == 0.99
