from dataclasses import dataclass


@dataclass
class PatientReport:
    """Representa a entrada natural, a reclamação bruta do paciente."""

    text: str


@dataclass
class Disease:
    """Entidade médica de base mapeando uma doença teórica e seus sintomas esperados."""

    name: str  # Nome clínico (Ex: Hipertensão)
    symptoms_text: str  # Palavras-chave associadas (Ex: dor de cabeça, zumbido)


@dataclass
class DiagnosticResult:
    """Modelo que agrupa um relato com a predição."""

    report: PatientReport
    suggested_disease: str
    confidence: float  # Nível métrico de assertividade matemática (ex: Cosseno > 0)
