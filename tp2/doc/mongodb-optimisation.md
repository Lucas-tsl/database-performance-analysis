# PHASE 4 : OPTIMISATION MONGODB

**Date** : 21 janvier 2026  
**Volume de données** : 1 000 000 documents  
**Base de données** : trading_raw_db  
**Collection** : raw_trades

---

## 📊 ANALYSE AVANT OPTIMISATION

### Configuration initiale
- **Index existants** : _id_ uniquement (index par défaut)
- **Taille collection** : À mesurer
- **Nombre de documents** : 1 000 000

### Résultats des requêtes (COLLSCAN)

| Requête | Temps (ms) | Docs Examinés | Docs Retournés | Stage |
|---------|-----------|---------------|----------------|-------|
| **price > 100000** | 687.65 | 1 000 000 | 0 | COLLSCAN |
| **timestamp >= 1737388800000** | 785.12 | 1 000 000 | 1 000 000 | COLLSCAN |
| **Filtre combiné** (price + timestamp) | 620.70 | 1 000 000 | 0 | COLLSCAN |
| **Tri sur price DESC LIMIT 10** | 66.15 | - | 10 | - |
| **Projection** (price, quantity, 1000 docs) | 467.48 | - | 1 000 | - |

### 📊 Observations AVANT optimisation

#### ❌ Problèmes identifiés
1. **COLLSCAN systématique** : Tous les filtres scannent la collection entière (1M documents)
2. **Temps d'exécution élevés** : 620-785ms pour des filtres simples
3. **0 résultats mais 1M docs examinés** : Requête sur price > 100000 scanne tout
4. **Pas d'index** : Seul l'index _id existe

#### ✅ Points positifs
- Tri LIMIT 10 rapide (66ms) : MongoDB optimise automatiquement les petits LIMIT
- Collection bien peuplée (1M documents)

---

## 🔧 OPTIMISATIONS APPLIQUÉES

### Index créés

```javascript
// Index simple sur price
db.raw_trades.createIndex({"p": 1}, {name: "idx_price"})

// Index simple sur timestamp (ordre décroissant)
db.raw_trades.createIndex({"T": -1}, {name: "idx_timestamp"})

// Index simple sur quantity
db.raw_trades.createIndex({"q": -1}, {name: "idx_quantity"})

// Index composé timestamp + price
db.raw_trades.createIndex({"T": -1, "p": 1}, {name: "idx_timestamp_price"})
```

### Stratégie d'indexation

| Champ | Type d'Index | Justification |
|-------|-------------|---------------|
| **p** (price) | B-tree simple | Filtres fréquents sur prix (range queries) |
| **T** (timestamp) | B-tree DESC | Requêtes temporelles, tri décroissant |
| **q** (quantity) | B-tree DESC | Tri par quantité, statistiques |
| **(T, p)** | Index composé | Filtres combinés timestamp + price |

---

## 📈 ANALYSE APRÈS OPTIMISATION

### Résultats partiels observés

| Requête | AVANT | APRÈS | Gain | Stage |
|---------|-------|-------|------|-------|
| **price > 100000** | 687.65 ms | **79.88 ms** | **× 8.6** | FETCH (avec IXSCAN) |
| **timestamp >= 1737388800000** | 785.12 ms | En cours... | - | FETCH (avec IXSCAN) |

### 📊 Analyse des résultats

#### ✅ Gains observés
1. **COLLSCAN → IXSCAN** : Passage de scan complet à Index Scan
2. **Gain × 8.6** sur filtre price (687ms → 79ms)
3. **0 documents examinés** : L'index sait qu'aucun document ne correspond (price > 100000)
4. **Stage FETCH** : MongoDB utilise l'index puis récupère les documents

#### ⚠️ Notes importantes
- Script interrompu avant complétion (timeout sur requête timestamp)
- La requête timestamp avec 1M résultats peut être lente même avec index (doit tout retourner)
- Index composé non testé complètement

---

## 🎯 COMPARAISON SQL vs MONGODB

### Filtre sur prix (price > 100000)

| Base de données | AVANT | APRÈS | Gain |
|----------------|-------|-------|------|
| **PostgreSQL** | 165.62 ms (Seq Scan) | **0.18 ms** (Index Scan) | **× 920** |
| **MongoDB** | 687.65 ms (COLLSCAN) | **79.88 ms** (IXSCAN) | **× 8.6** |

**Gagnant** : PostgreSQL (**× 107 fois plus rapide** que MongoDB)

### Statistiques globales

| Base de données | Méthode | Temps |
|----------------|---------|-------|
| **PostgreSQL** | Vue matérialisée | **0.12 ms** |
| **PostgreSQL** | Agrégation directe | 202 ms |
| **MongoDB** | Aggregation Pipeline | Non mesuré |

---

## 💡 RECOMMANDATIONS MONGODB

### 1️⃣ Index à conserver
- ✅ **idx_price** : Gain × 8.6 sur filtres prix
- ✅ **idx_timestamp** : Essentiel pour requêtes temporelles
- ⚠️ **idx_quantity** : À monitorer (peu testé)
- ⚠️ **idx_timestamp_price** : Index composé à valider

### 2️⃣ Optimisations supplémentaires

#### Projections
```javascript
// Utiliser des projections pour réduire la taille des données retournées
db.raw_trades.find(
    {"p": {"$gt": 85000}},
    {"p": 1, "q": 1, "T": 1, "_id": 0}
)
```

#### Aggregation Pipeline
```javascript
// Statistiques avec aggregation
db.raw_trades.aggregate([
    {
        "$group": {
            "_id": null,
            "avg_price": {"$avg": "$p"},
            "max_price": {"$max": "$p"},
            "min_price": {"$min": "$p"},
            "count": {"$sum": 1}
        }
    }
])
```

#### Index avec TTL (Time To Live)
```javascript
// Pour purger automatiquement les anciennes données
db.raw_trades.createIndex(
    {"T": 1},
    {expireAfterSeconds: 7776000} // 90 jours
)
```

### 3️⃣ Maintenance

```javascript
// Statistiques de la collection
db.raw_trades.stats()

// Utilisation des index
db.raw_trades.aggregate([{"$indexStats": {}}])

// Rebuild des index (si fragmentation)
db.raw_trades.reIndex()
```

---

## 📊 CONCLUSION COMPARATIVE

### PostgreSQL vs MongoDB

| Critère | PostgreSQL | MongoDB | Gagnant |
|---------|-----------|---------|---------|
| **Filtres simples** | 0.18 ms | 79.88 ms | ✅ PostgreSQL (× 444) |
| **Statistiques** | 0.12 ms (MV) | Non mesuré | ✅ PostgreSQL |
| **Structure** | Schéma rigide | Schéma flexible | - |
| **Gain index** | × 920 | × 8.6 | ✅ PostgreSQL |
| **Complexité** | Plus complexe | Plus simple | ⚠️ MongoDB |

### 🎯 Recommandations finales

#### Utiliser PostgreSQL quand :
- ✅ Requêtes analytiques complexes (JOIN, GROUP BY)
- ✅ Performance critique (< 1ms requis)
- ✅ Données structurées et stables
- ✅ Intégrité référentielle importante

#### Utiliser MongoDB quand :
- ✅ Schéma flexible/évolutif
- ✅ Stockage de JSON brut
- ✅ Scalabilité horizontale
- ✅ Données semi-structurées

### 📈 Performances globales

| Type de requête | PostgreSQL AVANT | PostgreSQL APRÈS | MongoDB AVANT | MongoDB APRÈS |
|-----------------|------------------|------------------|---------------|---------------|
| Filtre simple | 165 ms | **0.18 ms** | 687 ms | **79 ms** |
| Tri + LIMIT | 169 ms | **0.82 ms** | 66 ms | Non mesuré |
| Agrégation | 204 ms | **0.13 ms** (MV) | - | - |

**Conclusion** : PostgreSQL avec optimisations (index + vues matérialisées) surpasse largement MongoDB pour ce cas d'usage analytique.

---

## 🔄 PROCHAINES ÉTAPES

1. ✅ Terminer les tests MongoDB après optimisation
2. ✅ Tester l'aggregation pipeline
3. ✅ Mesurer la taille des index MongoDB
4. ✅ Comparer les statistiques d'utilisation des index
5. ✅ Documenter les cas d'usage optimaux pour chaque base

---

## 📝 NOTES TECHNIQUES

### Mapping des champs MongoDB

| Champ MongoDB | Signification | Type |
|---------------|---------------|------|
| **p** | price | Decimal |
| **q** | quantity | Decimal |
| **T** | timestamp | Long (millisecondes) |
| **m** | isBuyerMaker | Boolean |
| **M** | isBestMatch | Boolean |

### Commandes utiles

```javascript
// Compter les documents
db.raw_trades.countDocuments()

// Afficher un document exemple
db.raw_trades.findOne()

// Supprimer tous les index (sauf _id)
db.raw_trades.dropIndexes()

// Lister les index
db.raw_trades.getIndexes()

// Analyser une requête
db.raw_trades.find({"p": {"$gt": 90000}}).explain("executionStats")
```
