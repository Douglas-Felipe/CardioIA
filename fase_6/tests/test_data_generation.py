import pytest
import pandas as pd
from data.generate_dataset import generate_synthetic_data
from src.ml.train import FEATURE_COLUMNS, TARGET_COLUMN


@pytest.mark.unit
def test_synthetic_data_shape_and_columns():
    """Valida se o gerador sintético produz a quantidade exata de linhas e colunas."""
    n = 200
    df = generate_synthetic_data(n=n, random_seed=123)
    
    assert len(df) == n
    for col in FEATURE_COLUMNS:
        assert col in df.columns, f"Coluna esperada {col} ausente no DataFrame"
    assert TARGET_COLUMN in df.columns
    assert "risk_score" in df.columns


@pytest.mark.unit
def test_synthetic_data_value_bounds():
    """Valida se as variáveis respeitam os limites matemáticos e clínicos estipulados."""
    df = generate_synthetic_data(n=1000, random_seed=42)
    
    assert df["idade_media"].min() >= 18.0
    assert df["idade_media"].max() <= 90.0
    
    assert df["carga_sistema"].min() >= 30.0
    assert df["carga_sistema"].max() <= 100.0
    
    assert df["tempo_espera"].min() >= 5.0
    assert df["tempo_espera"].max() <= 180.0
    
    assert df["spo2_media"].min() >= 70.0
    assert df["spo2_media"].max() <= 100.0
    
    assert df["pa_sistolica"].min() >= 80.0
    assert df["pa_sistolica"].max() <= 200.0


@pytest.mark.unit
def test_target_logic_consistency():
    """Valida se a regra 'pico_risco = (risk_score >= 2).astype(int)' é estritamente satisfeita."""
    df = generate_synthetic_data(n=500, random_seed=99)
    expected_pico = (df["risk_score"] >= 2).astype(int)
    
    assert (df["pico_risco"] == expected_pico).all()
