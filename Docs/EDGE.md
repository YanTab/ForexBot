EDGE.md — Définition de l’Edge du Système
Ce document définit l’Edge institutionnel exploité par le framework.
Il sert de référence pour les modules, stratégies, tests, validations et mises à jour.

1. Objectif de l’Edge
Définir l’avantage statistique exploité par le bot, basé sur :

comportements récurrents du marché

inefficiences mesurables

patterns temporels

retour à la moyenne

conditions de marché filtrées

L’Edge doit être quantifiable, testable, stable, reproductible.

2. Composants de l’Edge
2.1 Mean Reversion (Retour à la moyenne)
Hypothèse :  
Le prix tend à revenir vers une valeur d’équilibre après un écart excessif.

Conditions d’activation :

volatilité modérée

spread faible

absence de news majeures

latence stable

pas de tendance forte

Signaux :

écart au z‑score

distance à la moyenne mobile

excès de micro‑structure

retour de liquidité

Sorties :

take profit court

stop loss serré

invalidation si volatilité augmente

2.2 Timing (Patterns horaires institutionnels)
Hypothèse :  
Certaines heures présentent des comportements récurrents exploitables.

Exemples :

rebonds post‑ouverture

stabilisation post‑volatilité

micro‑inefficiences en creux de liquidité

patterns de spread

Conditions d’activation :

heure dans la liste des fenêtres validées

spread dans les limites

volatilité compatible

absence d’événements macro

Sorties :

entrée uniquement dans les fenêtres horaires validées

taille ajustée selon la volatilité

3. Filtres obligatoires
3.1 Spread Filter
interdit les trades si spread > seuil

seuil dynamique selon volatilité

3.2 Volatility Filter
interdit les trades si volatilité > seuil

seuil dépend de la stratégie

3.3 Latency Filter
interdit les trades si latence > seuil

protège contre les mauvaises exécutions

3.4 Execution Quality Filter
interdit les trades si slippage > seuil

surveille la qualité d’exécution en temps réel

4. Conditions d’invalidation de l’Edge
L’Edge est considéré comme non exploitable si :

volatilité extrême

spread anormal

latence instable

news majeures

dérive statistique détectée

drawdown anormal

perte de cohérence des signaux

Dans ces cas, le bot :

désactive les modules concernés

réduit le risque

peut activer le mode sécurité

5. Mesure de l’Edge
5.1 Indicateurs de performance
expectancy

profit factor

win rate

drawdown

Sharpe / Sortino

coût moyen (spread + slippage)

5.2 Indicateurs de stabilité
dérive des signaux

dérive des modules

dérive des stratégies

cohérence des patterns horaires

5.3 Indicateurs de robustesse
performance par volatilité

performance par spread

performance par heure

performance par jour de la semaine

6. Validation de l’Edge
6.1 Backtests
2+ années minimum

conditions variées

spread réel simulé

slippage simulé

6.2 Forward tests
3+ mois minimum

comparaison backtest / forward

6.3 Sandbox
validation des modules

validation des stratégies

validation des filtres

7. Mises à jour de l’Edge
Toute modification de l’Edge doit :

passer par la sandbox

être testée

être versionnée

être documentée

être validée par le Chef d’Orchestre IA

8. Résumé opérationnel
L’Edge exploité par le bot repose sur :

Mean Reversion dans des conditions contrôlées

Timing institutionnel basé sur des patterns horaires

Filtres stricts (spread, volatilité, latence, qualité d’exécution)

Gestion du risque dynamique

Validation continue (stabilité, dérive, robustesse)

Cet Edge est simple, robuste, institutionnel, et adapté au Forex.