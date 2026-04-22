#!/usr/bin/env python3
import re
import sys
import subprocess
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR  = Path(__file__).parent
DOCS_DIR  = BASE_DIR / "Docs"
LOG_FILE  = DOCS_DIR / "ORCHESTRATOR_LOG.md"
DEV_PLAN  = DOCS_DIR / "DEVELOPMENT_PLAN.md"

RELEVANT_DOCS = ["SPEC_TECHNIQUE.md", "ARCHITECTURE.md", "COORDINATION.md", "EDGE.md"]

# ── Utilitaires ───────────────────────────────────────────────────────────────

def read_file(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")

def append_file(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(text + "\n")

# ── Chargement des docs ───────────────────────────────────────────────────────

def load_docs() -> dict:
    docs = {}
    if not DOCS_DIR.exists():
        return docs
    for f in sorted(DOCS_DIR.glob("*.md")):
        if f.name == "ORCHESTRATOR_LOG.md":
            continue
        docs[f.name] = f.read_text(encoding="utf-8")
    return docs

# ── Scan du projet ────────────────────────────────────────────────────────────

def scan_project() -> dict:
    def subdirs(rel: str) -> list:
        p = BASE_DIR / rel
        return [d.name for d in sorted(p.iterdir()) if d.is_dir()] if p.exists() else []

    try:
        r = subprocess.run(
            ["git", "status", "--short"],
            cwd=BASE_DIR, capture_output=True, text=True, timeout=5,
        )
        git_status = r.stdout.strip() or "propre"
    except Exception:
        git_status = "git absent"

    return {
        "core":       subdirs("core"),
        "modules":    subdirs("modules"),
        "strategies": subdirs("strategies"),
        "git_status": git_status,
    }

# ── Plan de développement ─────────────────────────────────────────────────────

def load_development_plan() -> list:
    content = read_file(DEV_PLAN)
    tasks = []
    pat_md     = re.compile(r"^\s*#+\s*(\d+(?:\.\d+)*)(?:\.?\s*[-–—:]?\s*)(.*)$")
    pat_simple = re.compile(r"^(\d+(?:\.\d+)*)(?:\.?\s*[-–—:]?\s*)(.*)$")

    for line in content.splitlines():
        s = line.strip()
        m = pat_md.match(s)
        if m:
            tasks.append({"id": m.group(1), "title": m.group(2).strip() or "Tâche", "description": ""})
            continue
        m2 = pat_simple.match(s)
        if m2:
            tasks.append({"id": m2.group(1), "title": m2.group(2).strip() or "Tâche", "description": ""})
            continue
        if tasks and s:
            tasks[-1]["description"] += s + " "

    return tasks

# ── Log ───────────────────────────────────────────────────────────────────────

def load_orchestrator_log() -> set:
    content = read_file(LOG_FILE)
    done = set()
    task_pat = re.compile(r"Tâche\s*:\s*([0-9.]+)")
    ok_pat   = re.compile(r"Résultat\s*:\s*OK")
    for block in content.strip().split("\n\n"):
        m = task_pat.search(block)
        if m and ok_pat.search(block):
            done.add(m.group(1))
    return done

def mark_task_done(task_id: str, notes: str = ""):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    append_file(LOG_FILE,
        f"[{ts}] Tâche : {task_id}\n"
        f"Résultat : OK\n"
        f"Notes : {notes}\n"
    )

def log_action(task_id: str, ia: str, files: list, result: str, notes: str = ""):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    append_file(LOG_FILE,
        f"[{ts}] Tâche : {task_id}\n"
        f"IA : {ia}\n"
        f"Fichiers : {', '.join(files)}\n"
        f"Résultat : {result}\n"
        f"Notes : {notes}\n"
    )

# ── Navigation dans le plan ───────────────────────────────────────────────────

def get_next_task() -> dict | None:
    done = load_orchestrator_log()
    for task in load_development_plan():
        if task["id"] not in done:
            return task
    return None

# ── Inférence des chemins ─────────────────────────────────────────────────────

def infer_paths(task: dict) -> list:
    text = (task["title"] + " " + task["description"]).lower()
    rules = [
        (["pipeline", "data", "indicator", "risk", "order", "safety", "execution", "reporting_engine"], "core/"),
        (["module", "mean_reversion", "timing"],                                                        "modules/"),
        (["stratégie", "strategy"],                                                                     "strategies/"),
        (["config", "yaml"],                                                                            "config/"),
        (["sandbox", "test", "validation"],                                                             "sandbox/"),
        (["report", "fiscal"],                                                                          "reports/"),
        (["readme", "architecture", "doc"],                                                             "Docs/"),
    ]
    paths = [path for keywords, path in rules if any(kw in text for kw in keywords)]
    return paths if paths else ["project/"]

# ── Assignation IA ────────────────────────────────────────────────────────────

def assign_ia(task: dict) -> str:
    top  = task["id"].split(".")[0]
    desc = (task["title"] + " " + task["description"]).lower()
    if top in ("1", "6", "7"):
        return "Claude Code"
    if any(kw in desc for kw in ["logique", "engine", "pipeline", "compute", "risk", "order"]):
        return "Claude Code"
    return "Copilot"

# ── Extraction de contexte ────────────────────────────────────────────────────

def extract_relevant_snippets(task: dict, docs: dict) -> str:
    text     = (task["title"] + " " + task["description"]).lower()
    keywords = [w for w in re.split(r"\W+", text) if len(w) > 3]
    output   = []

    for doc_name in RELEVANT_DOCS:
        if doc_name not in docs:
            continue
        lines    = docs[doc_name].splitlines()
        captured = []
        i = 0
        while i < len(lines) and len(captured) < 8:
            if any(kw in lines[i].lower() for kw in keywords):
                for bl in lines[i:i + 4]:
                    if len(captured) < 8:
                        captured.append(bl)
            i += 1
        if captured:
            output.append(f"[{doc_name}]")
            output.extend(captured)

    return "\n".join(output)

# ── Génération du prompt ──────────────────────────────────────────────────────

def generate_task_prompt(task: dict, docs: dict = None) -> str:
    if docs is None:
        docs = load_docs()

    task_id  = task["id"]
    title    = task["title"]
    desc     = task["description"].strip()
    paths    = infer_paths(task)
    ia       = assign_ia(task)
    snippets = extract_relevant_snippets(task, docs)

    lines = [f"=== TÂCHE {task_id} : {title} ===", ""]
    if desc:
        lines += [f"Description :", desc, ""]
    lines += [f"Fichiers concernés :", ", ".join(paths), ""]
    lines += [f"IA recommandée : {ia}", ""]
    if snippets:
        lines += ["Contexte extrait des docs :", snippets, ""]
    lines += [
        "Instructions :",
        "- Implémente cette tâche conformément à SPEC_TECHNIQUE.md et ARCHITECTURE.md.",
        "- Respecte les conventions : snake_case fonctions, PascalCase classes, .yaml configs.",
        "- Ne modifie pas les fichiers déjà validés sans justification explicite.",
        "- Résultat attendu : code fonctionnel, sans dépendances externes non listées.",
    ]
    return "\n".join(lines)

# ── Statut ────────────────────────────────────────────────────────────────────

def show_status():
    tasks  = load_development_plan()
    done   = load_orchestrator_log()
    n_done = sum(1 for t in tasks if t["id"] in done)
    next_t = get_next_task()
    print(f"Progression : {n_done}/{len(tasks)} tâches terminées.")
    if next_t:
        print(f"Prochaine   : {next_t['id']} — {next_t['title']}")
    else:
        print("Plan terminé.")

# ── Menu interactif ───────────────────────────────────────────────────────────

def _interactive_menu():
    while True:
        print()
        print("  1. Prochaine tâche")
        print("  2. Marquer tâche terminée")
        print("  3. Statut du projet")
        print("  4. Scanner le projet")
        print("  5. Prompt libre")
        print("  6. Quitter")
        choice = input("\n> ").strip()
        print()

        if choice == "1":
            task = get_next_task()
            if task:
                print(f"[{task['id']}] {task['title']}\n")
                print(generate_task_prompt(task))
            else:
                print("Plan terminé.")

        elif choice == "2":
            tid   = input("ID de la tâche : ").strip()
            notes = input("Notes (optionnel) : ").strip()
            mark_task_done(tid, notes)
            print(f"Tâche {tid} marquée OK.")

        elif choice == "3":
            show_status()

        elif choice == "4":
            s = scan_project()
            print(f"core      : {s['core'] or '—'}")
            print(f"modules   : {s['modules'] or '—'}")
            print(f"strategies: {s['strategies'] or '—'}")
            print(f"git       : {s['git_status']}")

        elif choice == "5":
            desc = input("Description : ").strip()
            print(generate_task_prompt({"id": "0", "title": desc, "description": ""}))

        elif choice == "6":
            break

        else:
            print("Choix invalide.")

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if not args:
        _interactive_menu()
        return

    cmd = args[0]

    if cmd == "--next":
        task = get_next_task()
        if not task:
            print("Plan terminé.")
            return
        print(f"[{task['id']}] {task['title']}\n")
        print(generate_task_prompt(task))

    elif cmd == "--done":
        if len(args) < 2:
            print("Erreur : préciser l'id de la tâche.")
            return
        mark_task_done(args[1], args[2] if len(args) > 2 else "")
        print(f"Tâche {args[1]} marquée OK.")

    elif cmd == "--status":
        show_status()

    elif cmd == "--scan":
        s = scan_project()
        print(f"core      : {s['core'] or '—'}")
        print(f"modules   : {s['modules'] or '—'}")
        print(f"strategies: {s['strategies'] or '—'}")
        print(f"git       : {s['git_status']}")

    elif cmd == "--prompt":
        if len(args) < 2:
            print("Erreur : préciser une description.")
            return
        desc = " ".join(args[1:])
        print(generate_task_prompt({"id": "0", "title": desc, "description": ""}))

    else:
        print(f"Commande inconnue : {cmd}")
        print("Usage : --next | --done <id> [notes] | --status | --scan | --prompt <desc>")


if __name__ == "__main__":
    main()
