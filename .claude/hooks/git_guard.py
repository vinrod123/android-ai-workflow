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
  Art. 11.9 (sem rastro de IA nem do workflow no GitHub do app):
  - mensagem de commit, título/corpo/comentário de PR e issue, ou nome de branch
    com atribuição de IA, arquivo .md, pasta do workflow, artigo, gate, comando
    ou nome de agente (texto inline, em heredoc ou no arquivo de --body-file / -F)

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

TRACE_RULES = [
    (re.compile(r"co-authored-by", re.I), "linha Co-Authored-By"),
    (re.compile(r"generated (with|by)|gerad[oa]s? (com|por|pel[oa])", re.I), "frase de geração automática"),
    (re.compile(r"\bclaude\b|anthropic", re.I), "menção ao Claude/Anthropic"),
    (re.compile(r"\b(chat)?gpt\b|openai|copilot|\bllms?\b", re.I), "menção a ferramenta de IA"),
    (re.compile(r"\bIA\b|\bAI\b"), "menção a IA"),
    (re.compile("\U0001F916"), "emoji de robô"),
    (re.compile(r"\.md\b", re.I), "arquivo .md"),
    (re.compile(r"(?<![\w.-])(workflow|\.claude)/", re.I), "pasta do workflow"),
    (re.compile(r"constitui[çc][ãa]o|constitution", re.I), "constituição do workflow"),
    (re.compile(r"\bart\.\s?\d", re.I), "artigo da constituição"),
    (re.compile(r"\bgates?\b", re.I), "gate do workflow"),
    (re.compile(r"\b(F[1-4]|P[0-3])\b"), "código de gate"),
    (re.compile(r"(?<![\w/])/(feature|bootstrap)\b", re.I), "comando do workflow"),
    (re.compile(r"\b(product-owner|tech-lead|test-engineer|security-reviewer|docs-writer|"
                r"engineering-manager|refactorer|planner|verifier|sub-?agent\w*)\b", re.I),
     "nome de agente"),
]

SEPARATORS = {"&&", "||", ";", "|", "&"}
COMMIT_OPTS = {"-m": "text", "--message": "text", "-F": "file", "--file": "file"}
GH_OPTS = {"-t": "text", "--title": "text", "-b": "text", "--body": "text",
           "-F": "file", "--body-file": "file"}
BRANCH_OPTS = {"-b": "text", "-B": "text", "-c": "text", "-C": "text"}
GH_TEXT_ACTIONS = {"create", "edit", "comment", "review"}
HEREDOC_RE = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n(.*?)\n[ \t]*\2[ \t]*(?=\n|$)", re.S)


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


# ----------------------------------------------------------------------- Art. 11.9

def tokenize(command):
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|")
        lexer.whitespace_split = True
        return list(lexer)
    except ValueError:
        return command.split()


def read_text_file(path, cwd):
    full = path if os.path.isabs(path) else os.path.join(cwd or os.getcwd(), path)
    try:
        with open(full, encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError:
        return ""


def collect_option_values(tokens, start, options, cwd):
    texts = []
    k = start
    while k < len(tokens) and tokens[k] not in SEPARATORS:
        token = tokens[k]
        option, has_equals, value = token.partition("=")
        if options is COMMIT_OPTS and re.fullmatch(r"-[a-zA-Z]*m", option) and option != "-m":
            option = "-m"
        if option.startswith("-") and option in options:
            if not has_equals:
                value = tokens[k + 1] if k + 1 < len(tokens) else ""
                k += 1
            if options[option] == "file":
                if value != "-":
                    texts.append(read_text_file(value, cwd))
            else:
                texts.append(value)
        k += 1
    return texts, k


def published_texts(command, cwd):
    heredoc_bodies = [m.group(3) for m in HEREDOC_RE.finditer(command)]
    tokens = tokenize(HEREDOC_RE.sub(" \n", command))
    texts = []
    publishes = False
    i = 0
    while i < len(tokens):
        if tokens[i] == "git":
            j = i + 1
            while j < len(tokens) and tokens[j] in ("-C", "-c"):
                j += 2
            sub = tokens[j] if j < len(tokens) else ""
            if sub == "commit":
                publishes = True
                found, i = collect_option_values(tokens, j + 1, COMMIT_OPTS, cwd)
                texts += found
                continue
            if sub in ("checkout", "switch"):
                found, i = collect_option_values(tokens, j + 1, BRANCH_OPTS, cwd)
                texts += found
                continue
        if (tokens[i] == "gh" and i + 2 < len(tokens)
                and tokens[i + 1] in ("pr", "issue") and tokens[i + 2] in GH_TEXT_ACTIONS):
            publishes = True
            found, i = collect_option_values(tokens, i + 3, GH_OPTS, cwd)
            texts += found
            continue
        i += 1
    if publishes:
        texts += heredoc_bodies
    return texts


def check_no_trace(command, cwd):
    for text in published_texts(command, cwd):
        for pattern, label in TRACE_RULES:
            match = pattern.search(text)
            if match:
                block(f"rastro de IA ou do workflow no texto publicado ({label}: '{match.group(0)}'). "
                      "Commits, PRs, issues e branches do app não podem ter isso (Art. 11.9). "
                      "Reescreva o texto como uma pessoa do time escreveria.", command)


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
    check_no_trace(command, cwd)
    sys.exit(0)


if __name__ == "__main__":
    main()
