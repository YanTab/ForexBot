# ✅ **COORDINATION.md — Document de coordination inter‑IA**

Ce document définit **comment GitHub Copilot et Claude Code doivent travailler ensemble**, se relayer, se comprendre et maintenir la cohérence du projet.

Il sert de **charte de travail** pour toutes les IA impliquées dans le développement.

---

# 1. **Rôles des IA**

## 1.1 GitHub Copilot (VS Code)
**Rôle :**
- Compléter le code localement  
- Générer des fonctions cohérentes avec les fichiers existants  
- Maintenir la continuité dans un fichier en cours  
- Proposer des corrections rapides  

**Ne doit pas :**
- Redéfinir l’architecture  
- Réécrire des modules entiers sans demande explicite  
- Modifier la logique métier  

---

## 1.2 Claude Code
**Rôle :**
- Générer des blocs complexes  
- Refactoriser proprement  
- Vérifier la cohérence globale  
- Produire du code structuré et documenté  
- Résoudre les problèmes logiques  
- Générer les structures, templates et scripts répétitifs  
- Produire les fichiers de configuration et initialisation  

**Ne doit pas :**
- Modifier la structure du projet sans justification  
- Réécrire des fichiers déjà validés sans raison  

---

# 2. **Normes de code**

## 2.1 Conventions
```
snake_case pour les fonctions
PascalCase pour les classes
kebab-case pour les fichiers
.yaml pour les configs
```

## 2.2 Structure des modules
```
module/
    __init__.py
    config.yaml
    module.py
    health.py
    version.txt
```

## 2.3 Structure des stratégies
```
strategy/
    rules.py
    parameters.yaml
    modules_used.yaml
    version.txt
```

## 2.4 Structure des tests
```
tests/
    unit/
    integration/
    sandbox/
```

---

# 3. **Règles de continuité inter‑IA**

## 3.1 Avant d’écrire du code
Chaque IA doit :
- lire le fichier en cours  
- lire les TODO  
- lire les NOTES  
- lire la version du module/stratégie  

## 3.2 Après avoir écrit du code
Chaque IA doit :
- ajouter un commentaire `# NOTE: écrit par <IA>`  
- ajouter un `# TODO:` si une autre IA doit compléter  
- ne jamais effacer les commentaires existants  

## 3.3 Reprise du travail
Si une IA reprend un fichier :
- elle doit respecter la structure existante  
- elle ne doit pas réécrire ce qui fonctionne  
- elle doit suivre les normes de ce document  

---

# 4. **Règles de communication dans le code**

## 4.1 Commentaires standardisés
```
# NOTE: contexte ou décision
# TODO: tâche à faire
# FIX: bug identifié
# REVIEW: demander validation
```

## 4.2 Documentation minimale
Chaque fonction doit avoir :
```
description
inputs
outputs
exceptions
```

---

# 5. **Règles de validation**

## 5.1 Tests obligatoires
Chaque ajout doit être accompagné :
- d’un test unitaire  
- d’un test d’intégration si nécessaire  

## 5.2 Sandbox
Les modules critiques doivent passer par :
- sandbox de mise à jour  
- sandbox de cohérence  

## 5.3 Validation logique
Claude Code est prioritaire pour :
- vérifier la cohérence  
- valider les interactions entre modules  

---

# 6. **Règles de sécurité**

## 6.1 Interdictions
- ne jamais afficher les clés API  
- ne jamais logguer les secrets  
- ne jamais écrire les clés dans le code  

## 6.2 Respect du mode sécurité
Toute IA doit :
- préserver les triggers  
- ne pas modifier les protections  
- ne pas désactiver les isolations  

---

# 7. **Règles de versioning**

## 7.1 Incrémentation
Chaque modification majeure → incrémenter `version.txt`.

## 7.2 Changelog
Chaque IA doit ajouter :
```
date
IA utilisée
fichiers modifiés
raison
```

## 7.3 Archivage
Les versions précédentes doivent être conservées dans :
```
/updates/versions/
```

---

# 8. **Règles de fallback (qui fait quoi si blocage)**

## 8.1 Si Copilot bloque
→ Claude Code reprend.

## 8.2 Si Claude Code bloque
→ L'utilisateur clarifie la tâche, puis Claude Code reprend.

## 8.3 Si une IA ne comprend pas
→ elle doit écrire :
```
# REVIEW: clarification nécessaire
```

---

# 9. **Règles de cohérence avec les documents de référence**

Chaque IA doit respecter :
- SYNTHÈSE.md  
- ARCHITECTURE.md  
- DEVELOPMENT_PLAN.md  
- SPEC_TECHNIQUE.md  
- COORDINATION.md (ce document)  

En cas de conflit → **SPEC_TECHNIQUE.md est prioritaire**.

