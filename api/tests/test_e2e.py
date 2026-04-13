import os
from infrastructure.repositories import FileDataRepository
from infrastructure.nlp_service import TfidfNlpService
from core.use_cases import DiagnosePatientUseCase

def test_process_diagnostics_end_to_end():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    relatos = os.path.join(base_dir, 'data', 'relatos.txt')
    ontologia = os.path.join(base_dir, 'data', 'ontologia.csv')
    
    repository = FileDataRepository(relatos, ontologia)
    nlp_service = TfidfNlpService()
    use_case = DiagnosePatientUseCase(repository, nlp_service)
    
    resultados = use_case.execute()
    
    assert len(resultados) == 8
    doencas = [res.suggested_disease for res in resultados]
    
    assert "Infarto do Miocárdio (Angina)" in doencas
    assert "Hipertensão Arterial" in doencas
    assert "Insuficiência Cardíaca" in doencas
