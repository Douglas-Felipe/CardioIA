import subprocess
import sys
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent


@pytest.mark.e2e
def test_cli_execution():
    """Valida se o comando CLI 'python main.py --test-case' roda com exit code 0 e exibe as seções esperadas."""
    python_bin = BASE_DIR / ".venv" / "bin" / "python"
    main_py = BASE_DIR / "main.py"
    
    result = subprocess.run(
        [str(python_bin), str(main_py), "--test-case"],
        capture_output=True,
        text=True,
        cwd=str(BASE_DIR)
    )
    
    assert result.returncode == 0, f"CLI falhou: {result.stderr}"
    stdout = result.stdout
    assert "CardioIA Fase 6" in stdout
    assert "RISCO PREVISTO:" in stdout
    assert "PROTOCOLOS SUGERIDOS:" in stdout
    assert "Agente Orquestrador" in stdout
    assert "Agente Planejador" in stdout
