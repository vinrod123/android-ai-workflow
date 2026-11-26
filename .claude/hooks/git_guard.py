#!/usr/bin/env python3
"""git_guard.py - PreToolUse hook (Bash) que aplica o Art. 11 da CONSTITUTION.md.

Atua só dentro de um projeto Android (raiz do repositório com settings.gradle ou
settings.gradle.kts). Fora disso, por exemplo no próprio repositório do kit, libera tudo.

Bloqueia (exit 2):
  Art. 11.1 / 11.6:
  - gh pr merge, gh pr review --approve
  - push --force / -f / --force-with-lease / --mirror, apagar branch remota
  - push direto para branch protegida
  - git commit / merge / rebase com o HEAD numa branch protegida
  - git reset --hard, git clean -f
  Art. 11.8 (o repositório é só do app):
  - git add de caminho do workflow, ou git add -f/--force
  - git add amplo (., -A, --all) sem o .git/info/exclude configurado
  - git commit com arquivo do workflow no stage (ou rastreado, com -a)

A lista de caminhos do workflow vem de workflow/git-exclude.txt (com fallback interno).
Exit codes: 0 = liberado · 2 = bloqueado (o motivo vai para o stderr e o Claude lê).
Só usa a stdlib.
"""
import fnmatch
import json
import os
import re
import shlex
import subprocess
import sys

PROTECTED = {"main", "master", "develop"}
PROT_RE = r"(?:main|master|develop)"
DEFAULT_WORKFLOW_PATHS = ["CONSTITUTION.md", "CLAUDE.md", "CLAUDE.local.md", ".claude/", "workflow/"]
GIT = r"\bgit\s+(?:-C\s+\S+\s+)?"

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
    (GIT + r"commit\b", "Commit direto em branch protegida (Art. 11.1). Crie a branch da feature."),
    (GIT + r"merge\b", "Merge em branch protegida é do humano (Art. 11.6)."),
    (GIT + r"rebase\b", "Rebase em branch protegida reescreve histórico (Art. 11.6)."),
]

BROAD_ADD = {".", "-A", "--all", ":/", "*", "-u", "--update"}


# ----------------------------------------------------------------------------- util

def git(args, cwd):
    try:
        out = subprocess.run(["git", *args], cwd=cwd or None,
                             capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout if out.returncode == 0 else None


def block(reason, command):
    sys.stderr.write(
        f"[git_guard] BLOQUEADO: {reason}\n"
        f"Comando: {command}\n"
        "Se isso é realmente necessário, peça ao humano para executar manualmente.\n"
    )
    sys.exit(2)


def repo_root(cwd):
    top = git(["rev-parse", "--show-toplevel"], cwd)
    return top.strip() if top else None


def is_android_project(root):
    return bool(root) and any(
        os.path.isfile(os.path.join(root, name))
        for name in ("settings.gradle.kts", "settings.gradle")
    )


def load_workflow_paths(root):
    for base in (os.environ.get("CLAUDE_PROJECT_DIR"), root):
        if not base:
            continue
        try:
            with open(os.path.join(base, "workflow", "git-exclude.txt"), encoding="utf-8") as f:
                pats = [ln.strip() for ln in f if ln.strip() and not ln.strip().startswith("#")]
            if pats:
                return [p.lstrip("/") for p in pats]
        except OSError:
            continue
    return list(DEFAULT_WORKFLOW_PATHS)


def norm(path):
    p = path.strip().strip("'\"").replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    return p


def is_workflow_path(path, pats):
    p = norm(path)
    if not p:
        return False
    for pat in pats:
        if pat.endswith("/"):
            if p == pat[:-1] or p.startswith(pat):
                return True
        elif p == pat or fnmatch.fnmatch(p, pat):
            return True
    return False


def exclude_configured(cwd, pats):
    rel = git(["rev-parse", "--git-path", "info/exclude"], cwd)
    if rel is None:
        return True  # não é repositório Git: nada a proteger
    path = rel.strip()
    if not os.path.isabs(path):
        path = os.path.join(cwd or os.getcwd(), path)
    try:
        with open(path, encoding="utf-8") as f:
            lines = {ln.strip().lstrip("/") for ln in f}
    except OSError:
        return False
    return all(p in lines for p in pats)


def split_segments(command):
    return [s for s in re.split(r"&&|\|\||;|\|", command) if s.strip()]


def args_after(segment, subcmd):
    m = re.search(GIT + subcmd + r"\b(.*)", segment)
    if not m:
        return None
    rest = m.group(1)
    try:
        return shlex.split(rest, posix=True)
    except ValueError:
        return rest.split()


# ----------------------------------------------------------------------- Art. 11.8

def check_workflow_isolation(command, cwd, pats):
    for seg in split_segments(command):
        args = args_after(seg, "add")
        if args is None:
            continue
        for a in args:
            if a == "--force" or (a.startswith("-") and not a.startswith("--") and "f" in a[1:]):
                block("git add -f/--force pode forçar arquivo do workflow para o Git (Art. 11.8).", command)
        for a in args:
            if not a.startswith("-") and is_workflow_path(a, pats):
                block(f"'{a}' é arquivo do workflow e nunca é commitado (Art. 11.8).", command)
        if any(a in BROAD_ADD for a in args) and not exclude_configured(cwd, pats):
            block("git add amplo sem o .git/info/exclude configurado com workflow/git-exclude.txt "
                  "(Art. 11.8). Configure a exclusão antes.", command)

    if re.search(GIT + r"commit\b", command):
        staged = git(["diff", "--cached", "--name-only"], cwd) or ""
        names = staged.splitlines()
        if re.search(GIT + r"commit\b[^;&|]*(?:\s-[a-zA-Z]*a\b|\s--all\b)", command):
            names += (git(["diff", "--name-only"], cwd) or "").splitlines()
        bad = sorted({n for n in names if is_workflow_path(n, pats)})
        if bad:
            block("arquivos do workflow no commit (Art. 11.8): " + ", ".join(bad)
                  + ". Tire do stage com 'git restore --staged <arquivo>'.", command)


# ---------------------------------------------------------------------------- main

def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    if data.get("tool_name") != "Bash":
        sys.exit(0)

    command = (data.get("tool_input") or {}).get("command", "") or ""
    if not command.strip():
        sys.exit(0)

    cwd = data.get("cwd")
    root = repo_root(cwd)
    if not is_android_project(root):
        sys.exit(0)  # o guard só vale dentro do projeto Android

    for pattern, reason in RULES:
        if re.search(pattern, command):
            block(reason, command)

    if any(re.search(p, command) for p, _ in BRANCH_RULES):
        branch = (git(["rev-parse", "--abbrev-ref", "HEAD"], cwd) or "").strip()
        if branch in PROTECTED:
            for pattern, reason in BRANCH_RULES:
                if re.search(pattern, command):
                    block(f"{reason} (HEAD = {branch})", command)

    check_workflow_isolation(command, cwd, load_workflow_paths(root))
    sys.exit(0)


if __name__ == "__main__":
    main()
