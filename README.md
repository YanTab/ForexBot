# ForexBot

Système de trading algorithmique institutionnel sur Forex, conçu pour fonctionner de manière autonome avec un niveau de contrôle du risque et de traçabilité de qualité professionnelle.

> **Mode actuel : Simulation** — Broker cible : Interactive Brokers (IB Gateway / TWS). Aucune activation production tant que le bot n'est pas validé.

---

## Objectif

Exploiter deux edges statistiques sur le marché Forex :

- **Mean Reversion** — retour à l'équilibre après déviation excessive (z-score, microstructure)
- **Timing institutionnel** — patterns horaires récurrents exploitables

Chaque trade est conditionné par quatre filtres obligatoires : spread, volatilité, latence, qualité d'exécution. Le système s'auto-protège, s'isole en cas d'anomalie et produit des rapports journaliers/hebdomadaires/mensuels avec conformité fiscale espagnole (AEAT).

---

## Architecture

```
ForexBot/
├── core/                    # Pipelines et engines principaux
│   ├── data_pipeline/       # Ingestion, nettoyage, validation, sync
│   ├── indicators/          # Z-score, volatilité, spread, microstructure
│   ├── risk_engine/         # Sizing, stops, limites journalières
│   ├── order_engine/        # Envoi, slippage, smart cancellation
│   ├── safety_engine/       # Isolation, watchdog, safety mode
│   └── reporting_engine/    # Rapports daily/weekly/monthly/fiscal
├── modules/                 # Modules de trading indépendants
│   ├── mean_reversion/
│   ├── timing/
│   ├── volatility/
│   ├── spread_filter/
│   ├── latency_filter/
│   ├── execution_quality/
│   └── risk_adapter/
├── strategies/              # Stratégies combinant modules
│   ├── mean_reversion_strategy/
│   └── timing_strategy/
├── broker/
│   └── interactive_brokers/ # Connecteur IB (ib_insync)
├── config/                  # Fichiers YAML globaux et par module
├── logs/                    # Trades, décisions, erreurs, système
├── sandbox/                 # Tests unitaires et validation
├── reports/                 # Rapports générés
├── updates/                 # Gestion des versions
└── security/                # Clés chiffrées, permissions
```

Flux de décision : `Data → Indicators → Filters → Modules → Strategies → Risk Engine → Order Engine → Monitoring`

---

## Prérequis

- Python 3.10+
- Interactive Brokers TWS ou IB Gateway (mode simulation ou production)
- Compte IB avec accès API activé

---

## Installation

```bash
git clone https://github.com/YanTab/ForexBot.git
cd ForexBot
pip install -r requirements.txt
```

---

## Configuration

1. Copier `.env.example` en `.env` et renseigner les paramètres IB
2. Adapter `config/global_config.yaml` (paires, horaires, limites de risque)
3. Vérifier le mode simulation : `SIMULATION_MODE=true` dans `.env`

---

## Lancement

```bash
# Voir la prochaine tâche de développement
python orchestrator.py --next

# Statut du projet
python orchestrator.py --status

# Marquer une tâche terminée
python orchestrator.py --done <id> "notes"
```

---

## Documentation de référence

| Document | Contenu |
|---|---|
| [Docs/SPEC_TECHNIQUE.md](Docs/SPEC_TECHNIQUE.md) | Spécifications techniques complètes (priorité maximale) |
| [Docs/ARCHITECTURE.md](Docs/ARCHITECTURE.md) | Schéma d'architecture détaillé |
| [Docs/DEVELOPMENT_PLAN.md](Docs/DEVELOPMENT_PLAN.md) | Plan de développement 8 phases, 40 tâches |
| [Docs/COORDINATION.md](Docs/COORDINATION.md) | Charte de travail inter-IA |
| [Docs/EDGE.md](Docs/EDGE.md) | Définition de l'edge statistique exploité |
| [Docs/ORCHESTRATOR.md](Docs/ORCHESTRATOR.md) | Rôle et règles du chef d'orchestre IA |

---

## Sécurité

- Clés API chiffrées dans `security/` (jamais en clair dans le code)
- `security/` et `.env` exclus du dépôt git
- Safety mode automatique en cas d'anomalie détectée
