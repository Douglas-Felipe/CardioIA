import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

# Garantir importações locais
sys.path.append(str(Path(__file__).resolve().parent))

from src.schemas import PatientData
from src.agents.runner import MultiAgentPipelineRunner

console = Console()

# Caso oficial de teste
DEFAULT_TEST_CASE = {
    "idade_media": 62,
    "carga_sistema": 92,
    "tempo_espera": 75,
    "fc_media": 118,
    "spo2_media": 89,
    "pa_sistolica": 100,
    "temperatura": 37.5,
    "densidade_eventos": 7,
    "eventos_24h": 5,
    "disponibilidade recursos": 25
}


def display_pipeline_execution(runner: MultiAgentPipelineRunner):
    """Renderiza uma tabela visual rica com os eventos de handoffs e tools dos agentes."""
    table = Table(title="[bold cyan]Fluxo Multiagente CardioIA (Mapika Decider & Agentes Especializados)[/bold cyan]", box=box.ROUNDED)
    table.add_column("Tipo", style="bold yellow", width=14)
    table.add_column("Origem", style="magenta", width=26)
    table.add_column("Destino", style="green", width=28)
    table.add_column("Conteúdo / Ação", style="white")

    for msg in runner.history:
        color = "cyan"
        if msg.message_type == "decision":
            color = "bold magenta"
        elif msg.message_type == "handoff":
            color = "bold yellow"
        elif msg.message_type == "tool_call":
            color = "blue"
        elif msg.message_type == "tool_result":
            color = "green"
        elif msg.message_type == "final_output":
            color = "bold green"

        table.add_row(
            f"[{color}]{msg.message_type.upper()}[/{color}]",
            msg.sender,
            msg.recipient,
            str(msg.content)[:120] + ("..." if len(str(msg.content)) > 120 else "")
        )

    console.print(table)


def run_test_case(patient_dict: dict = DEFAULT_TEST_CASE):
    """Executa a triagem multiagente para o caso padrão do."""
    console.print(Panel(
        "[bold green]Iniciando Triagem Multiagente do Paciente[/bold green]\n"
        f"Dados de Entrada:\n{patient_dict}",
        title="CardioIA Fase 6 - Sistema Multiagente",
        border_style="cyan"
    ))

    runner = MultiAgentPipelineRunner()
    final_response = runner.run(patient_dict)

    display_pipeline_execution(runner)

    console.print("\n" + "=" * 60)
    console.print("[bold yellow]RESPOSTA DO SISTEMA:[/bold yellow]\n")
    console.print(Panel(
        final_response.format_task_output(),
        title="[bold green]Saída Consolidada pelo Agente Planejador[/bold green]",
        border_style="green"
    ))
    if final_response.plano_contingencia:
        console.print(f"[bold cyan]Plano de Contingência Operacional:[/bold cyan] {final_response.plano_contingencia}")
    console.print("=" * 60 + "\n")
    return final_response


def run_interactive_mode():
    """Modo interativo no terminal permitindo ao usuário digitar dados clínicos."""
    console.print(Panel("[bold cyan]Modo Interativo de Triagem Hospitalar[/bold cyan]\nDigite os parâmetros clínicos:"))

    def ask_float(prompt: str, default: float) -> float:
        val = input(f"{prompt} [{default}]: ").strip()
        return float(val) if val else default

    dados = {
        "idade_media": ask_float("Idade média", 62.0),
        "carga_sistema": ask_float("Carga do sistema (%)", 92.0),
        "tempo_espera": ask_float("Tempo de espera (min)", 75.0),
        "fc_media": ask_float("Frequência cardíaca (bpm)", 118.0),
        "spo2_media": ask_float("SpO2 (%)", 89.0),
        "pa_sistolica": ask_float("PA Sistólica (mmHg)", 100.0),
        "temperatura": ask_float("Temperatura (°C)", 37.5),
        "densidade_eventos": ask_float("Densidade de eventos", 7.0),
        "eventos_24h": ask_float("Eventos em 24h", 5.0),
        "disponibilidade_recursos": ask_float("Disponibilidade de recursos (%)", 25.0),
    }

    run_test_case(dados)


def main():
    parser = argparse.ArgumentParser(description="CardioIA Fase 6 - Pipeline Multiagente de Risco Cardíaco")
    parser.add_argument("--test-case", action="store_true", help="Executa o caso de teste padrão")
    parser.add_argument("--interactive", action="store_true", help="Inicia a entrada interativa de parâmetros clínicos")
    args = parser.parse_args()

    if args.interactive:
        run_interactive_mode()
    else:
        # Padrão: executa o caso de teste oficial
        run_test_case()


if __name__ == "__main__":
    main()
