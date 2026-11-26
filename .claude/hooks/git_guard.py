#!/usr/bin/env python3
"""git_guard.py - PreToolUse hook (Bash) que aplica o Art. 11 da CONSTITUTION.md.

Bloqueia (exit 2) comandos Git/GitHub que nenhum agente pode executar:
  - gh pr merge / git merge na branch protegida
  - gh pr review --approve
  - push --force / -f / --force-with-lease / --mirror
  - push direto para branch protegida, ou apagar branch remota
  - git commit enquanto o HEAD está numa branch protegida
  - git reset --hard / git clean -fd* / rebase em branch protegida

Exit codes: 0 = liberado · 2 = bloqueado (o motivo vai para o stderr e o Claude lê).
Só usa a stdlib.
"""
import json
import re
import subprocess
import sys

PROTECTED = {"main", "master", "develop"}
PROT_RE = r"(?:main|master|develop)"

RULES = [
    (r"\bgh\s+pr\s+merge\b",
     "Merge é exclusivo do humano (Art. 7, gates F4/P3)."),
    (r"\bgh\s+pr\s+review\b[^;&|]*--approve\b",
     "Aprovar PR é do humano. Use --comment ou --request-changes."),
    (r"\bgit\s+push\b[^;&|]*(?:\s--force(?:-with-lease)?\b|\s-f\b|\s--mirror\b|\s\+\S)",
     "push forçado reescreve histórico publicado (Art. 11.6)."),
    (r"\bgit\s+push\b[^;&|]*(?:\s--delete\b|\s-d\b|\s:\S)",
     "Apagar branch remota é proibido aos agentes (Art. 11.6)."),
    (r"\bgit\s+push\b[^;&|]*\s(?:\S+:)?" + PROT_RE + r"(?:\s|$)",
     "Push direto para branch protegida (Art. 11.1)."),
    (r"\bgit\s+reset\b[^;&|]*--hard\b",
     "reset --hard descarta trabalho de forma irreversível."),
    (r"\bgit\s+clean\b[^;&|]*\s-[a-zA-Z]*f",
     "git clean -f apaga arquivos não rastreados de forma irreversível."),
]

BRANCH_RULES = [
    (r"\bgit\s+commit\b", "Commit direto em branch protegida (Art. 11.1). Crie a branch da feature."),
    (r"\bgit\s+merge\b", "Merge em branch protegida é do humano (Art. 11.6)."),
    (r"\bgit\s+rebase\b", "Rebase em branch protegida reescreve histórico (Art. 11.6)."),
]


def current_branch(cwd):
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd or None, capture_output=True, text=True, timeout=10,
        )
        return out.stdout.strip() if out.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def block(reason, command):
    sys.stderr.write(
        f"[git_guard] BLOQUEADO: {reason}\n"
        f"Comando: {command}\n"
        "Se isso é realmente necessário, peça ao humano para executar manualmente.\n"
    )
    sys.exit(2)


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)  # entrada inesperada: não bloqueia ferramentas que não são Bash

    if data.get("tool_name") != "Bash":
        sys.exit(0)

    command = (data.get("tool_input") or {}).get("command", "") or ""
    if not command.strip():
        sys.exit(0)

    for pattern, reason in RULES:
        if re.search(pattern, command):
            block(reason, command)

    if any(re.search(p, command) for p, _ in BRANCH_RULES):
        branch = current_branch(data.get("cwd"))
        if branch in PROTECTED:
            for pattern, reason in BRANCH_RULES:
                if re.search(pattern, command):
                    block(f"{reason} (HEAD = {branch})", command)

    sys.exit(0)


if __name__ == "__main__":
    main()
