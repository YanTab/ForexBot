# Sandbox — Conventions et critères de validation

## Structure

```
sandbox/
    tests/
        unit/          ← tests unitaires par composant
        integration/   ← tests d'interaction entre modules
    validation/        ← scripts de validation avant mise en production
```

## Conventions

- Chaque module doit avoir au minimum un fichier `test_<module>.py` dans `tests/unit/`
- Les tests d'intégration vérifient les interactions entre engines et modules
- Couverture minimale requise : **80%** sur les blocs critiques
- Nommage : `test_<composant>.py`, fonctions `test_<comportement>()`

## Critères de validation (avant production)

| Critère | Seuil |
|---|---|
| Couverture tests unitaires | ≥ 80% |
| Tests d'intégration | Tous verts |
| Backtest cohérence | Sharpe > 0, drawdown < seuil config |
| Stabilité 72h simulation | 0 crash, 0 anomalie non gérée |
| Drift statistique | Absent sur la période de test |

## Lancement des tests

```bash
# Tous les tests
pytest sandbox/tests/ -v

# Tests unitaires uniquement
pytest sandbox/tests/unit/ -v

# Avec couverture
pytest sandbox/tests/ --cov=core --cov=modules --cov=strategies
```
