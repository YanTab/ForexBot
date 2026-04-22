

# ✅ DOCUMENT 2/4 — **SCHÉMA D’ARCHITECTURE DU FRAMEWORK**

Format : **ARCHITECTURE.md**  
Objectif : donner à une IA la carte complète du système, claire, modulaire, exploitable pour coder.

---

## 🧩 **ARCHITECTURE — Framework Institutionnel**

---

## 1. **Structure générale**
```
/core
    /data_pipeline
    /indicator_pipeline
    /risk_engine
    /order_engine
    /execution_quality
    /safety_mode

/modules
    /module_X
    /module_Y
    ...

/strategies
    /strategy_X
    /strategy_Y
    ...

/config
    global_config.yaml
    /modules
    /strategies

/logs
    /daily
    /weekly
    /monthly
    /system
    /errors
    /security
    /trades
    /decisions
    /risk
    /data
    /latency
    /modules
    /strategies

/reports
    /daily
    /weekly
    /monthly
    /fiscal_ES

/updates
    /sandbox
    /versions

/security
    keys.enc
    permissions.json
```

---

## 2. **Pipelines**

### 2.1 Data Pipeline
```
raw_data → cleaning → validation → gap_filling → sync → distribution
```

### 2.2 Indicator Pipeline
```
data → compute → incremental_update → cache → distribution
```

---

## 3. **Engines**

### 3.1 Risk Engine
- risk_per_trade  
- risk_per_module  
- risk_per_strategy  
- daily_risk_limits  
- volatility_adjustments  
- execution_quality_adjustments  

### 3.2 Order Engine
- order_validation  
- order_send  
- order_status  
- partial_fills  
- rejections  
- timeouts  
- reconnections  
- smart_cancellations  

### 3.3 Execution Quality Engine
- latency  
- slippage  
- spread  
- execution anomalies  
- dynamic module deactivation  

### 3.4 Safety Mode
- triggers  
- isolation  
- freeze orders  
- protect positions  
- enhanced monitoring  

---

## 4. **Modules**
Chaque module = bloc technique indépendant.

Exemples :
```
mean_reversion/
timing/
volatility/
spread_filter/
latency_filter/
execution_quality/
risk_adapter/
```

Fonctionnalités :
- activation/désactivation dynamique  
- isolation  
- redémarrage  
- versioning  

---

## 5. **Stratégies**
Structure :
```
strategy/
    rules/
    parameters/
    modules_used/
    risk_profile/
    version/
```

Fonctionnalités :
- activation/désactivation  
- surveillance  
- dérive  
- retrait automatique  
- versioning  

---

## 6. **Gestion du temps**
- horaires fixes  
- sessions Forex  
- conditions dynamiques (spread, vol, latence)  
- news  
- fériés  

---

## 7. **Logs**
Catégories :
```
TRADE
DECISION
RISK
DATA
MODULE
STRATEGY
LATENCY
SECURITY
ERROR
SYSTEM
```

Propriétés :
- versionnés  
- archivés  
- purgés  
- séparés simu/réel  

---

## 8. **Reporting**
Dossiers :
```
/reports/daily
/reports/weekly
/reports/monthly
/reports/fiscal_ES
```

Contenu :
- performance  
- drawdown  
- coûts  
- modules  
- stratégies  
- dérive  
- stabilité  
- latence  
- sécurité  
- fiscalité ES  

---

## 9. **Configuration**
Structure :
```
global_config.yaml
modules/module_X.yaml
strategies/strategy_X.yaml
```

Fonctionnalités :
- versioning  
- validation  
- rollback  
- sandbox  

---

## 10. **Mises à jour**
Pipeline :
```
download → sandbox → validation → install → versioning → rollback
```

---

## 11. **Sécurité**
- clés chiffrées  
- fichiers protégés  
- permissions  
- détection anomalies  
- isolation  
- mode sécurité  

---

## 12. **Fiscalité Espagne**
Pipeline :
```
trades → conversions EUR → plus/minus values → frais réels → rapport AEAT → archivage annuel
```

