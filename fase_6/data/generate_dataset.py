import numpy as np
import pandas as pd
from pathlib import Path
import sys

# Permitir import de src se executado diretamente
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.config import DATASET_CSV_PATH


def generate_synthetic_data(n: int = 5000, random_seed: int = 42) -> pd.DataFrame:
    """
    Gera a base de dados sintética de pacientes.
    
    Args:
        n: Quantidade de instâncias a serem geradas.
        random_seed: Semente de números aleatórios para reprodutibilidade.
        
    Returns:
        DataFrame com as 10 variáveis clínicas/operacionais, risk_score e pico_risco.
    """
    np.random.seed(random_seed)
    
    df = pd.DataFrame({
        "idade_media": np.random.normal(55, 12, n).clip(18, 90),
        "carga_sistema": np.random.uniform(30, 100, n),
        "tempo_espera": np.random.normal(45, 20, n).clip(5, 180),
        "fc_media": np.random.normal(85, 15, n).clip(50, 150),
        "spo2_media": np.random.normal(95, 3, n).clip(70, 100),
        "pa_sistolica": np.random.normal(125, 20, n).clip(80, 200),
        "temperatura": np.random.normal(24, 5, n).clip(10, 40),
        "densidade_eventos": np.random.poisson(3, n),
        "eventos_24h": np.random.poisson(2, n),
        "disponibilidade_recursos": np.random.uniform(20, 100, n)
    })
    
    risk_score = (
        (df["carga_sistema"] > 80).astype(int) +
        (df["tempo_espera"] > 60).astype(int) +
        (df["spo2_media"] < 92).astype(int) +
        (df["fc_media"] > 110).astype(int) +
        (df["eventos_24h"] > 4).astype(int) +
        (df["disponibilidade_recursos"] < 40).astype(int)
    )
    
    df["risk_score"] = risk_score
    df["pico_risco"] = (risk_score >= 2).astype(int)
    
    return df


def save_dataset(output_path: Path = DATASET_CSV_PATH, n: int = 5000, random_seed: int = 42) -> Path:
    """Gera e salva o dataset no disco em formato CSV."""
    df = generate_synthetic_data(n=n, random_seed=random_seed)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Dataset sintético gerado com sucesso em: {output_path} ({len(df)} registros)")
    print(f"Distribuição da variável alvo (pico_risco):\n{df['pico_risco'].value_counts(normalize=True)}")
    return output_path


if __name__ == "__main__":
    save_dataset()
