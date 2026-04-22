# DEVELOPMENT_PLAN.md — ForexBot Framework

Plan de développement complet, découpé en étapes et sous-étapes compatibles avec `orchestrator.py`.
Chaque tâche est numérotée pour que l'orchestrateur puisse avancer étape par étape.

---

## 1. Initialisation du projet

### 1.1 Créer la structure des dossiers

Créer l'arborescence complète depuis `d:/ForexBot/` :

- `core/` — pipelines et engines principaux
- `modules/` — modules de trading indépendants
- `strategies/` — stratégies combinant modules et filtres
- `config/` — fichiers de configuration YAML globaux et par module
- `logs/` — journaux système, trades, erreurs, décisions
- `sandbox/` — tests unitaires et validation hors production
- `updates/` — gestion des versions et changelogs
- `reports/` — rapports daily/weekly/monthly/fiscal
- `Docs/` — documentation de référence

### 1.2 Créer README.md

Fichier d'entrée du projet, doit contenir :

- Description du projet (objectif, périmètre, broker cible)
- Architecture générale résumée en une page
- Instructions de lancement et de configuration de base
- Références vers `Docs/ARCHITECTURE.md` et `Docs/SPEC_TECHNIQUE.md`

### 1.3 Vérifier et compléter ARCHITECTURE.md

Valider que `Docs/ARCHITECTURE.md` est complet et à jour :

- Structure complète des dossiers
- Schéma des engines (`data_pipeline`, `risk_engine`, `order_engine`, `safety_engine`)
- Liste des modules actifs et des stratégies prévues
- Flux de données simplifié entre composants

### 1.4 Initialiser la gestion des versions

Dans `updates/` :

- Créer `updates/versions/` — historique des versions par module et stratégie
- Créer `updates/changelog.md` — log des changements significatifs
- Créer `version.txt` dans chaque module et stratégie (format : `X.Y.Z`)

### 1.5 Initialiser le sandbox

Dans `sandbox/` :

- Créer `sandbox/tests/` — tests unitaires par composant
- Créer `sandbox/validation/` — scripts de validation avant mise en production
- Créer `sandbox/README.md` — conventions de test et critères de validation

---

## 2. Core — Infrastructure du framework

### 2.1 Créer core/data_pipeline/

Pipeline de données brutes depuis le broker :

- `ingestion.py` — connexion broker, réception du flux temps réel
- `cleaning.py` — détection et suppression des outliers et valeurs nulles
- `validation.py` — contrôle de cohérence (timestamps, spreads, gaps)
- `normalisation.py` — normalisation des prix et volumes, synchronisation multi-instruments
- `config.yaml` — paramètres du pipeline (tolérance gaps, seuils de validation)

### 2.2 Créer core/indicators/

Pipeline de calcul des indicateurs :

- `zscore.py` — calcul z-score glissant (window paramétrable)
- `volatility.py` — ATR, Garman-Klass, volatilité réalisée
- `spread.py` — spread instantané, spread moyen glissant, seuil dynamique
- `microstructure.py` — order flow, déséquilibre bid/ask, latence broker
- `cache.py` — cache LRU des indicateurs calculés (évite les recalculs)

### 2.3 Créer core/risk_engine/

Moteur de gestion du risque :

- `sizing.py` — calcul de la taille de position (% capital, ATR-based)
- `stop.py` — stop loss fixe et trailing stop, invalidation de niveau
- `invalidation.py` — logique d'invalidation du trade (volatilité, spread, temps)
- `risk_tiers.py` — niveaux de risque (conservateur / normal / agressif)
- `config.yaml` — paramètres de risque (risk/trade, risk/module, drawdown max)

### 2.4 Créer core/order_engine/

Moteur d'exécution des ordres :

- `market_order.py` — envoi d'ordre marché avec contrôle du slippage
- `limit_order.py` — gestion des ordres limite, expiration, remplissage partiel
- `slippage_control.py` — détection et rejet si slippage dépasse le seuil
- `spread_control.py` — blocage de l'exécution si spread dépasse le seuil dynamique
- `config.yaml` — seuils de slippage et de spread acceptables

### 2.5 Créer core/safety_engine/

Moteur de sécurité et protection du capital :

- `safety_mode.py` — activation du mode sécurité (arrêt des nouvelles positions)
- `isolation.py` — isolation d'un module défaillant sans arrêter les autres
- `restart.py` — redémarrage automatique d'un module après échec
- `watchdog.py` — surveillance continue des modules actifs
- `config.yaml` — seuils de déclenchement du mode sécurité

### 2.6 Créer core/reporting_engine/

Moteur de reporting automatique :

- `daily_report.py` — rapport journalier (P&L, nb trades, anomalies)
- `weekly_report.py` — rapport hebdomadaire (dérive, stabilité, cohérence)
- `monthly_report.py` — rapport mensuel (ratios de performance, archivage)
- `fiscal_report.py` — rapport fiscal Espagne (plus-values, modèle 720)
- `config.yaml` — paramètres de reporting (devises, exercice fiscal, destinataires)

---

## 3. Modules — Mean Reversion & Timing

### 3.1 Créer modules/mean_reversion/

Structure du module mean reversion :

- `__init__.py`
- `module.py` — classe principale `MeanReversionModule`
- `config.yaml` — paramètres (fenêtre z-score, seuils entrée/sortie)
- `health.py` — surveillance de l'état du module (anomalies, freeze, latence)
- `version.txt` — version courante du module

### 3.2 Implémenter logique mean_reversion

Logique de trading du module :

- `compute_signals()` — calcul du z-score, identification des zones extrêmes
- `compute_entry()` — conditions d'entrée (z-score, spread, volatilité, timing)
- `compute_exit()` — conditions de sortie (retour à la moyenne, stop, temps max)

### 3.3 Créer modules/timing/

Structure du module timing :

- `__init__.py`
- `module.py` — classe principale `TimingModule`
- `config.yaml` — fenêtres horaires autorisées, marchés cibles
- `health.py` — surveillance de l'état du module
- `version.txt` — version courante du module

### 3.4 Implémenter logique timing

Logique de filtrage temporel :

- Fenêtres horaires autorisées (Londres, New York, chevauchements)
- Filtres spread/volatilité par session
- Signaux horaires (momentum de début de session, ranges d'ouverture)

---

## 4. Stratégies

### 4.1 Créer strategies/mean_reversion_strategy/

Structure de la stratégie :

- `rules.py` — règles d'entrée et de sortie
- `parameters.yaml` — paramètres de la stratégie
- `modules_used.yaml` — liste des modules requis (`mean_reversion`, `timing`)

### 4.2 Implémenter stratégie mean_reversion

Implémentation complète de la stratégie :

- Agrégation des signaux depuis les modules
- Application des filtres (spread, volatilité, timing)
- Adaptation du risque via `risk_engine` (sizing, stops)
- Envoi des ordres via `order_engine`

### 4.3 Créer strategies/timing_strategy/

Structure de la stratégie :

- `rules.py` — règles d'entrée et de sortie
- `parameters.yaml` — paramètres de la stratégie
- `modules_used.yaml` — liste des modules requis (`timing`)

### 4.4 Implémenter stratégie timing

Implémentation complète de la stratégie :

- Signaux horaires et momentum de session
- Filtres spread et volatilité par session
- Adaptation du risque via `risk_engine`
- Envoi des ordres via `order_engine`

---

## 5. Filtres & Conditions globales

### 5.1 Spread Filter

Filtre spread dynamique global :

- Calcul du seuil dynamique (moyenne mobile + écart-type)
- Invalidation automatique si spread dépasse le seuil
- Événements loggués dans `logs/risk/`

### 5.2 Volatility Filter

Filtre volatilité dynamique global :

- Calcul ATR glissant sur fenêtre paramétrable
- Invalidation si volatilité sort de la plage normale
- Passage en mode sécurité si dépassement critique

### 5.3 Latency Filter

Filtre de latence broker :

- Mesure du round-trip broker (ping)
- Seuil d'invalidation configurable (ex. > 200 ms)
- Log des épisodes de latence élevée dans `logs/latency/`

### 5.4 Execution Quality Filter

Filtre de qualité d'exécution :

- Mesure du slippage moyen sur les N derniers trades
- Dégradation automatique si slippage dépasse le seuil
- Rapport d'exécution exporté dans `reports/`

---

## 6. Sandbox & Validation

### 6.1 Sandbox modules

Tests des modules individuels :

- Tests unitaires sur `compute_signals()`, `compute_entry()`, `compute_exit()`
- Tests d'intégration avec `data_pipeline` simulé
- Couverture minimale cible : 80 % des chemins critiques

### 6.2 Sandbox stratégies

Validation des stratégies :

- Cohérence des signaux sur données historiques (backtest léger)
- Cohérence des filtres (spread, volatilité, timing)
- Cohérence avec le `risk_engine` (sizing, stops)

### 6.3 Sandbox engines

Validation des engines core :

- `risk_engine` — vérification sizing et stops sur cas limites
- `order_engine` — simulation d'envoi d'ordres, rejet sur slippage
- `safety_engine` — déclenchement et désactivation du mode sécurité

---

## 7. Reporting & Fiscalité

### 7.1 Daily Report

Rapport journalier automatique :

- P&L du jour, nombre de trades, win rate
- Anomalies détectées (spreads aberrants, latence élevée)
- État de santé des modules actifs
- Export : `reports/daily/YYYY-MM-DD.md`

### 7.2 Weekly Report

Rapport hebdomadaire :

- Dérive des paramètres (z-score moyen, spreads, volatilité)
- Stabilité des modules (freezes, redémarrages, uptime)
- Cohérence des performances avec les attentes définies
- Export : `reports/weekly/YYYY-WXX.md`

### 7.3 Monthly Report

Rapport mensuel et fiscal :

- Ratios de performance (Sharpe, Sortino, max drawdown)
- Fiscalité Espagne : calcul des plus-values, déclaration modèle 720
- Archivage complet des logs du mois
- Export : `reports/monthly/YYYY-MM.md` + `reports/fiscal_ES/YYYY-MM.pdf`

---

## 8. Mise en production

### 8.1 Tests finaux

Validation pré-production :

- Stress test sur données simulées haute fréquence
- Test de dérive sur 30 jours de données historiques
- Test de stabilité (uptime 72 h en mode paper trading)

### 8.2 Activation du mode production

Passage en production réelle :

- Activation des logs complets (`logs/trades/`, `logs/decisions/`, `logs/risk/`)
- Activation du reporting automatique (daily, weekly, monthly)
- Vérification des accès broker et des permissions API
- Activation du `safety_engine` et du `watchdog`

### 8.3 Archivage versionné

Clôture de la version 1.0 :

- Tag de version finale dans `updates/versions/`
- Mise à jour de `updates/changelog.md`
- Documentation complète finalisée dans `Docs/`
- Archivage de la configuration de production dans `config/`
