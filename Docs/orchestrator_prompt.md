# orchestrator_prompt.md — Spécification unifiée

> **Cible :** Claude Code (chef d'orchestre principal)  
> **Objectif :** Générer `orchestrator.py`, outil CLI qui pilote le développement du projet ForexBot étape par étape, en produisant des prompts prêts à coller dans une IA de code.

---

## Contexte projet

Structure réelle du projet :

```
d:/ForexBot/
├── orchestrator.py          ← ce script
├── Docs/
│   ├── ARCHITECTURE.md
│   ├── COORDINATION.md
│   ├── DEVELOPMENT_PLAN.md
│   ├── EDGE.md
│   ├── ORCHESTRATOR.md
│   ├── SPEC_TECHNIQUE.md
│   └── ORCHESTRATOR_LOG.md  ← généré automatiquement
├── core/                    ← pipelines, engines
├── modules/                 ← mean_reversion, timing, ...
├── strategies/              ← stratégies de trading
├── config/
├── logs/
├── sandbox/
└── reports/
```

Priorité de référence en cas de conflit : `SPEC_TECHNIQUE.md` > `ARCHITECTURE.md` > `DEVELOPMENT_PLAN.md`.

Rôles des IA :
- **Claude Code** — blocs complexes, refactoring, cohérence globale, logique métier, templates, structures, fichiers de config
- **Copilot** — complétion locale, fonctions courtes, continuité dans un fichier

---

## Spécification de orchestrator.py

### Constantes

```python
BASE_DIR  = Path(__file__).parent        # d:/ForexBot/
DOCS_DIR  = BASE_DIR / "Docs"
LOG_FILE  = DOCS_DIR / "ORCHESTRATOR_LOG.md"
DEV_PLAN  = DOCS_DIR / "DEVELOPMENT_PLAN.md"
```

---

### 1. `load_docs() -> dict[str, str]`

Lit tous les fichiers `.md` présents dans `DOCS_DIR` (sauf `ORCHESTRATOR_LOG.md`).  
Retourne `{nom_fichier: contenu}`.

---

### 2. `scan_project() -> dict`

Retourne un état synthétique du projet :

```python
{
  "modules":    [str],   # sous-dossiers de modules/
  "strategies": [str],   # sous-dossiers de strategies/
  "core":       [str],   # sous-dossiers de core/
  "git_status": str,     # sortie de `git status --short` ou "git absent"
}
```

Utilise uniquement `os`, `pathlib`, `subprocess`.

---

### 3. `load_development_plan() -> list[dict]`

Parse `DEVELOPMENT_PLAN.md` et extrait toutes les tâches numérotées.

Formats reconnus sur une même ligne :
- `2.1 Titre` (liste simple)
- `## 2.1 Titre` (titre Markdown)

Structure retournée pour chaque tâche :
```python
{"id": "2.1", "title": "Créer core/data_pipeline/", "description": "ingestion cleaning validation normalisation"}
```

Les lignes non numérotées qui suivent une tâche s'ajoutent à sa `description`.

---

### 4. `load_orchestrator_log() -> set[str]`

Lit `ORCHESTRATOR_LOG.md` si présent.  
Retourne l'ensemble des `task_id` marqués `Résultat : OK`.

Pattern de détection : `r"Tâche\s*:\s*([0-9.]+)"` combiné à `r"Résultat\s*:\s*OK"` sur le bloc suivant.

---

### 5. `mark_task_done(task_id: str, notes: str = "")`

Ajoute dans `ORCHESTRATOR_LOG.md` :

```
[YYYY-MM-DD HH:MM] Tâche : <task_id>
Résultat : OK
Notes : <notes>

```

Pas de confirmation utilisateur. Crée le fichier si absent.

---

### 6. `get_next_task() -> dict | None`

Retourne la première tâche de `load_development_plan()` dont l'`id` n'est pas dans `load_orchestrator_log()`.  
Retourne `None` si toutes les tâches sont terminées.

---

### 7. `infer_paths(task: dict) -> list[str]`

Déduit les chemins probables à partir du `title` et de la `description` de la tâche.

Table de correspondance (plusieurs règles peuvent s'appliquer) :

| Mot-clé détecté               | Chemin retourné         |
|-------------------------------|-------------------------|
| `pipeline`, `data`, `indicator` | `core/`               |
| `risk`, `order`, `safety`, `execution`, `reporting` | `core/` |
| `module`, `mean_reversion`, `timing` | `modules/`        |
| `stratégie`, `strategy`       | `strategies/`           |
| `config`, `yaml`              | `config/`               |
| `sandbox`, `test`, `validation` | `sandbox/`            |
| `report`, `fiscal`            | `reports/`              |
| `readme`, `architecture`, `doc` | `Docs/`               |

Si aucun mot-clé ne correspond : retourner `["project/"]`.

---

### 8. `assign_ia(task: dict) -> str`

Retourne l'IA recommandée selon le type de tâche :

| Condition                                      | IA          |
|------------------------------------------------|-------------|
| `id` commence par `1` (init, structure)        | `Claude Code` |
| `id` commence par `6` (sandbox/tests)          | `Claude Code` |
| `id` commence par `7` (reporting)              | `Claude Code` |
| `description` contient `logique`, `engine`, `pipeline`, `compute` | `Claude Code` |
| sinon                                          | `Copilot`   |

---

### 9. `extract_relevant_snippets(task: dict, docs: dict) -> str`

Extrait des extraits courts (≤ 8 lignes par document) pertinents pour la tâche.

Algorithme :
1. Construire une liste de mots-clés depuis `task["title"]` + `task["description"]` (mots > 3 lettres, lowercase).
2. Pour chaque doc dans `["SPEC_TECHNIQUE.md", "ARCHITECTURE.md", "COORDINATION.md", "EDGE.md"]` :
   - Parcourir les lignes.
   - Dès qu'une ligne contient un mot-clé, capturer cette ligne + les 3 suivantes.
   - Limiter à 8 lignes par doc.
   - Si aucune correspondance, ignorer le doc.
3. Retourner le tout formaté :
   ```
   [SPEC_TECHNIQUE.md]
   <lignes>
   [ARCHITECTURE.md]
   <lignes>
   ```

---

### 10. `generate_task_prompt(task: dict, docs: dict) -> str`

Génère un prompt court et autonome, prêt à coller dans une IA.

Format exact à respecter :

```
=== TÂCHE {id} : {title} ===

Description :
{description}

Fichiers concernés :
{chemins déduits par infer_paths()}

IA recommandée : {assign_ia()}

Contexte extrait des docs :
{extract_relevant_snippets()}

Instructions :
- Implémente cette tâche conformément à SPEC_TECHNIQUE.md et ARCHITECTURE.md.
- Respecte les conventions : snake_case fonctions, PascalCase classes, .yaml configs.
- Ne modifie pas les fichiers déjà validés sans justification explicite.
- Résultat attendu : code fonctionnel, sans dépendances externes non listées.
```

---

### 11. `log_action(task_id, ia, files, result, notes="")`

Ajoute dans `ORCHESTRATOR_LOG.md` :

```
[YYYY-MM-DD HH:MM] Tâche : <task_id>
IA : <ia>
Fichiers : <files séparés par virgule>
Résultat : <OK | À corriger>
Notes : <notes>

```

---

### 12. `main()`

#### Mode CLI (arguments)

| Commande                        | Comportement                                                                 |
|---------------------------------|------------------------------------------------------------------------------|
| `--next`                        | Affiche l'id + titre de la prochaine tâche, puis le prompt complet           |
| `--done <id>`                   | Appelle `mark_task_done(id)`, affiche `Tâche <id> marquée OK.`              |
| `--done <id> "<notes>"`         | Idem avec notes                                                              |
| `--status`                      | Affiche nb tâches terminées / total, et la prochaine tâche                  |
| `--scan`                        | Affiche le résultat de `scan_project()`                                     |
| `--prompt "<description libre>"`| Génère un prompt ad hoc depuis une description textuelle (mode libre)       |

#### Mode interactif (aucun argument)

Menu :
```
1. Prochaine tâche (--next)
2. Marquer tâche terminée (--done)
3. Statut du projet (--status)
4. Scanner le projet (--scan)
5. Prompt libre
6. Quitter
```

Chaque option appelle la fonction correspondante et affiche le résultat.  
Pas de boucle infinie : après chaque action, retourner au menu.

---

## Contraintes absolues

- Standard library uniquement : `os`, `pathlib`, `re`, `sys`, `subprocess`, `datetime`, `textwrap`
- Compatible Python 3.10+
- Sorties console courtes, lisibles, sans verbosité inutile
- Le prompt généré ne doit jamais inclure un document complet — uniquement des extraits (≤ 8 lignes par doc)
- Le script ne demande jamais de confirmation pour les actions de log ou de marquage
- Code sans commentaires verbeux — noms explicites suffisent

---

## Livrable attendu

Un seul fichier `orchestrator.py`, complet, fonctionnel, couvrant toutes les fonctions ci-dessus.  
Lançable immédiatement avec `python orchestrator.py --next`.
