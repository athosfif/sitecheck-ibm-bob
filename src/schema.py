"""
schema.py — estrutura canônica de um achado e do relatório.

Um achado é um dict com os campos abaixo; nunca adicione campos extras
sem atualizar este módulo e os testes correspondentes.
"""

SEVERITIES = ("high", "medium", "low")
STATES = ("open", "fixed", "regressed", "unverified")


def make_finding(
    *,
    id: str,
    title: str,
    severity: str,
    file: str,
    location: str,
    reproduction: str,
    evidence: str,
    recommendation: str,
    state: str = "open",
    recheck_result: str | None = None,
) -> dict:
    """Retorna um achado validado. Lança ValueError em campos inválidos."""
    if severity not in SEVERITIES:
        raise ValueError(f"severity deve ser um de {SEVERITIES}, recebeu {severity!r}")
    if state not in STATES:
        raise ValueError(f"state deve ser um de {STATES}, recebeu {state!r}")
    return {
        "id": id,
        "title": title,
        "severity": severity,
        "file": file,
        "location": location,
        "reproduction": reproduction,
        "evidence": evidence,
        "recommendation": recommendation,
        "state": state,
        "recheck_result": recheck_result,
    }


def make_report(findings: list[dict], checked_file: str) -> dict:
    """Agrega achados em um relatório. findings pode ser lista vazia."""
    return {
        "schema_version": "1",
        "checked_file": checked_file,
        "total_findings": len(findings),
        "findings": findings,
    }
