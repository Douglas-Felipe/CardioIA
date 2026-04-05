import os
from infrastructure.repositories import FileDataRepository
from infrastructure.nlp_service import TfidfNlpService
from core.use_cases import DiagnosePatientUseCase


def main():
    print("=== Módulo de Diagnóstico Clean Architecture (TF-IDF) ===\n")

    # Resolve caminhos relativos ao arquivo atual
    base_dir = os.path.dirname(os.path.abspath(__file__))
    relatos_path = os.path.join(base_dir, "data", "relatos.txt")
    ontologia_path = os.path.join(base_dir, "data", "ontologia.csv")

    # 1. Instancia as implementações de Infraestrutura
    repository = FileDataRepository(relatos_path, ontologia_path)
    nlp_service = TfidfNlpService()

    # 2. Injeta as interfaces no Caso de Uso
    use_case = DiagnosePatientUseCase(repository, nlp_service)

    # 3. Executa a regra de negócio central
    resultados = use_case.execute(confidence_threshold=0.15)

    # 4. Consumo dos dados
    for i, res in enumerate(resultados, 1):
        print(f'Relato {i}: "{res.report.text}"')
        print(
            f"   -> Diagnóstico Sugerido: [{res.suggested_disease}] (Confiança: {res.confidence:.4f})\n"
        )


if __name__ == "__main__":
    main()
