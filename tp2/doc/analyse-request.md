# ANALYSE DES PERFORMANCES - PHASE 2

**Date de l'analyse** : 21 janvier 2026  
**Volume de données** : 1 000 000 trades  
**Table principale** : fact_trades (partitionnée)  
**Index existants** : trade_time, pair_id, pkey

---

## REQUÊTE 1 : Filtre temporel (Index Scan)

### Requête SQL
```sql
SELECT * FROM fact_trades 
WHERE trade_time BETWEEN '2026-01-20 15:00:00' AND '2026-01-20 16:00:00';
```

### 1. EXPLAIN (coûts estimés)
- **Type de scan** : Index Scan using trades_default_trade_time_idx
- **Coût estimé** : 236.07..47313.62
- **Lignes estimées** : 80432 rows

### 2. EXPLAIN ANALYZE (métriques réelles)
- **Temps d'exécution réel** : 48.696 ms
- **Nombre de lignes réelles** : 80432 rows
- **Nombre d'itérations** : 1 loop

### 3. EXPLAIN (ANALYZE, BUFFERS)
- **Shared Hit** : Données en cache (non spécifié dans sortie simple)
- **Shared Read** : 0 (données en cache)
- **Shared Written** : 0
- **Temp Read/Written** : 0

### 📊 Analyse
✅ **Performance EXCELLENTE**  
✅ Index sur trade_time correctement utilisé  
✅ Temps d'exécution rapide (< 50ms) pour 80k lignes  
✅ Aucune lecture disque - données en cache

---

## REQUÊTE 2 : Filtre sur prix (Sequential Scan)

### Requête SQL
```sql
SELECT * FROM fact_trades 
WHERE price > 100000 
LIMIT 10;
```

### 1. EXPLAIN (coûts estimés)
- **Type de scan** : Seq Scan on trades_default
- **Coût estimé** : 0.00..17560.69
- **Lignes estimées** : 333333 rows (sur-estimation)

### 2. EXPLAIN ANALYZE (métriques réelles)
- **Temps d'exécution réel** : 165.624 ms
- **Nombre de lignes réelles** : 0 rows (aucune valeur > 100000)
- **Lignes filtrées** : 1 000 000 rows
- **Nombre d'itérations** : 1 loop

### 3. EXPLAIN (ANALYZE, BUFFERS)
- **Shared Hit** : 10294 (données en cache)
- **Shared Read** : 0
- **Shared Written** : 0
- **Temp Read/Written** : 0

### 📊 Analyse
⚠️ **PROBLÈME MAJEUR : Aucun index sur la colonne price**  
❌ Sequential Scan complet de 1M lignes  
❌ Temps d'exécution lent (165ms) même pour un LIMIT 10  
❌ Scan de 100% de la table pour retourner 0 résultats  
✅ Données en cache (pas de lecture disque)

**Recommandation** : Créer un index sur price

---

## REQUÊTE 3 : GROUP BY avec agrégation temporelle

### Requête SQL
```sql
SELECT DATE_TRUNC('hour', trade_time) as heure,
       COUNT(*) as nb_trades,
       AVG(price) as prix_moyen,
       SUM(quantity) as volume_total
FROM fact_trades
GROUP BY DATE_TRUNC('hour', trade_time)
ORDER BY heure;
```

### 1. EXPLAIN (coûts estimés)
- **Type de scan** : Parallel Seq Scan on trades_default
- **Coût estimé** : 0.00..20813.53
- **Lignes estimées** : 417017 rows (par worker)

### 2. EXPLAIN ANALYZE (métriques réelles)
- **Temps d'exécution réel** : 204.831 ms
- **Nombre de lignes réelles** : ~333333 rows par worker (3 workers)
- **Nombre d'itérations** : 3 loops (parallélisation)

### 3. EXPLAIN (ANALYZE, BUFFERS)
- **Shared Hit** : 10310 buffers
- **Shared Read** : 0
- **Shared Written** : 0
- **Temp Read/Written** : 0

### 📊 Analyse
⚠️ **Performance MOYENNE**  
⚠️ Parallel Sequential Scan utilisé (3 workers)  
❌ Scan complet de la table nécessaire  
⚠️ Temps d'exécution ~200ms pour agrégation horaire  
✅ Parallélisation efficace (Workers Planned: 2, Workers Launched: 2)  
✅ Données en cache

**Recommandation** : Vue matérialisée pour statistiques horaires fréquentes

---

## REQUÊTE 4 : JOIN + GROUP BY (Agrégation par symbole)

### Requête SQL
```sql
SELECT p.symbol, 
       COUNT(t.trade_id) as nb_trades, 
       AVG(t.price) as avg_price
FROM fact_trades t
JOIN dim_pairs p ON t.pair_id = p.pair_id
GROUP BY p.symbol;
```

### 1. EXPLAIN (coûts estimés)
- **Type de scan** : Parallel Seq Scan + Hash Join
- **Coût estimé** : 21841.53..21971.79
- **Lignes estimées** : 490 rows (groupes)

### 2. EXPLAIN ANALYZE (métriques réelles)
- **Temps d'exécution réel** : 203.259 ms
- **Planning Time** : 7.001 ms
- **Nombre de lignes réelles** : 1 row (1 symbole : BTCUSDT)
- **Nombre d'itérations** : 3 loops (parallélisation)

### 3. EXPLAIN (ANALYZE, BUFFERS)
- **Shared Hit** : 10341 buffers
- **Shared Read** : 0
- **Shared Written** : 0
- **Planning Buffers** : shared hit=420

### 📊 Analyse
⚠️ **Performance MOYENNE**  
✅ Hash Join efficace (Hash Cond: t.pair_id = p.pair_id)  
✅ Index sur pair_id utilisé (trades_default_pair_id_idx)  
⚠️ Parallel Seq Scan sur fact_trades (Parallel Append)  
⚠️ Temps d'exécution ~203ms  
✅ Memory Usage: 49kB (Batches: 1)  
✅ Données en cache

**Note** : 1 seul symbole dans les données (BTCUSDT), donc 1 seule ligne retournée

---

## REQUÊTE 5 : TRI + LIMIT (ORDER BY quantity)

### Requête SQL
```sql
SELECT * FROM fact_trades 
ORDER BY quantity DESC 
LIMIT 10;
```

### 1. EXPLAIN (coûts estimés)
- **Type de scan** : Parallel Seq Scan + Gather Merge + Sort
- **Coût estimé** : 26572.30..26573.47
- **Lignes estimées** : 10 rows (LIMIT)

### 2. EXPLAIN ANALYZE (métriques réelles)
- **Temps d'exécution réel** : 169.311 ms
- **Planning Time** : 2.512 ms
- **Nombre de lignes réelles** : 10 rows
- **Nombre d'itérations** : 3 loops (par worker)

### 3. EXPLAIN (ANALYZE, BUFFERS)
- **Shared Hit** : 10366 buffers
- **Shared Read** : 0
- **Shared Written** : 0
- **Planning Buffers** : shared hit=265

### 📊 Analyse
⚠️ **PROBLÈME : Aucun index sur quantity**  
❌ Sequential Scan complet avant tri  
⚠️ Sort Method: top-N heapsort (Memory: 27kB par worker)  
⚠️ Temps d'exécution 169ms pour un simple TOP 10  
✅ Parallélisation efficace (3 workers)  
✅ Données en cache

**Recommandation** : Créer un index sur quantity pour éviter le scan complet

---

## REQUÊTE 6 : Statistiques globales (Agrégations complètes)

### Requête SQL
```sql
SELECT MAX(price) as max_price, 
       MIN(price) as min_price, 
       AVG(price) as avg_price, 
       STDDEV(price) as stddev_price
FROM fact_trades;
```

### 1. EXPLAIN (coûts estimés)
- **Type de scan** : Parallel Seq Scan + Partial Aggregate + Finalize Aggregate
- **Coût estimé** : 21731.11..21731.12
- **Lignes estimées** : 1 row

### 2. EXPLAIN ANALYZE (métriques réelles)
- **Temps d'exécution réel** : 202.239 ms
- **Planning Time** : 2.732 ms
- **Nombre de lignes réelles** : 1 row
- **Nombre d'itérations** : 3 loops (par worker)

### 3. EXPLAIN (ANALYZE, BUFFERS)
- **Shared Hit** : 10294 buffers
- **Shared Read** : 0
- **Shared Written** : 0
- **Planning Buffers** : shared hit=258

### 📊 Analyse
⚠️ **Performance MOYENNE pour agrégations globales**  
❌ Scan complet de la table nécessaire (1M rows)  
✅ Parallélisation efficace (Workers: 2 planned, 2 launched)  
⚠️ Temps d'exécution ~202ms  
✅ Partial Aggregate optimisé (par worker)  
✅ Données en cache

**Recommandation** : Vue matérialisée pour statistiques globales fréquemment consultées

---

## STATISTIQUES DES COLONNES (pg_stats)

| Colonne | Valeurs Distinctes | Corrélation | Analyse |
|---------|-------------------|-------------|---------|
| **price** | 46 332 | 0.631 | Forte variabilité, corrélation moyenne |
| **quantity** | 3 973 | -0.003 | Peu de corrélation physique |
| **trade_time** | ~113 000 | -0.9999 | Anti-corrélation parfaite (ordre DESC) |

### 📊 Interprétation
- **price** : 46k valeurs distinctes → index B-tree recommandé
- **quantity** : 4k valeurs distinctes → index B-tree possible
- **trade_time** : Excellente corrélation → index déjà optimal

---

## STATISTIQUES D'UTILISATION DES INDEX (pg_stat_user_indexes)

| Index | Scans | Lignes Lues | Lignes Récupérées | Taux d'Utilisation |
|-------|-------|-------------|-------------------|-------------------|
| **trades_default_trade_time_idx** | 30 | 84 451 | 84 441 | ✅ 99.99% efficace |
| **trades_default_pair_id_idx** | 3 | 1 000 000 | 74 000 | ⚠️ 7.4% efficace |
| **trades_default_pkey** | 1 000 000 | 0 | 0 | ✅ Clé primaire |

### 📊 Analyse des Index
- **trade_time_idx** : Très efficace, utilisé fréquemment
- **pair_id_idx** : Faible efficacité (7.4% de sélectivité)
- **pkey** : Utilisé pour contrainte d'unicité

---

## 🎯 SYNTHÈSE DES PROBLÈMES IDENTIFIÉS

### ❌ Problèmes critiques
1. **Aucun index sur `price`** → Sequential Scan de 165ms
2. **Aucun index sur `quantity`** → Tri nécessite scan complet (169ms)
3. **Partitioning inefficace** → 100% des données dans trades_default au lieu de partitions temporelles
4. **Pas de vues matérialisées** → Agrégations recalculées à chaque fois (~200ms)

### ⚠️ Problèmes secondaires
- Requêtes d'agrégation toutes > 200ms
- Pas d'index composites pour requêtes complexes
- Cache bien utilisé mais requêtes toujours lentes

### ✅ Points positifs
- Index sur trade_time très efficace (48ms pour 80k lignes)
- Parallélisation fonctionnelle (2 workers)
- 100% des données en cache (shared hit, no disk reads)
- Partitioning configuré (à optimiser)

---

## 💡 RECOMMANDATIONS POUR PHASE 3

### 1️⃣ Indexation (Priorité HAUTE)
```sql
-- Index simple sur price (critique)
CREATE INDEX idx_price ON fact_trades(price);

-- Index simple sur quantity
CREATE INDEX idx_quantity ON fact_trades(quantity);

-- Index composite pour requêtes temporelles + prix
CREATE INDEX idx_time_price ON fact_trades(trade_time, price);

-- Index composite pour GROUP BY fréquents
CREATE INDEX idx_time_quantity ON fact_trades(trade_time, quantity);
```

**Gain attendu** : 
- Filtre sur price : 165ms → ~10-20ms (8x plus rapide)
- Tri sur quantity : 169ms → ~15-25ms (7x plus rapide)

### 2️⃣ Vues Matérialisées (Priorité MOYENNE)
```sql
-- Vue matérialisée : statistiques horaires
CREATE MATERIALIZED VIEW mv_stats_hourly AS
SELECT DATE_TRUNC('hour', trade_time) as heure,
       COUNT(*) as nb_trades,
       AVG(price) as prix_moyen,
       SUM(quantity) as volume_total,
       MAX(price) as prix_max,
       MIN(price) as prix_min
FROM fact_trades
GROUP BY DATE_TRUNC('hour', trade_time);

CREATE INDEX idx_mv_stats_hourly ON mv_stats_hourly(heure);
```

**Gain attendu** : 
- Statistiques horaires : 204ms → ~1-5ms (40x plus rapide)

### 3️⃣ Optimisation du Partitioning (Priorité BASSE)
```sql
-- Revoir la stratégie de partitioning temporel
-- Actuellement : 100% dans trades_default
-- Objectif : Partitions mensuelles automatiques
```

**Gain attendu** : 
- Requêtes avec filtre temporel : Élimination de partitions (partition pruning)

### 4️⃣ Maintenance (Priorité CONTINUE)
```sql
-- Mise à jour des statistiques
ANALYZE fact_trades;

-- Rafraîchissement des vues matérialisées
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_stats_hourly;
```

---

## 📈 OBJECTIFS DE PERFORMANCE PHASE 3

| Type de Requête | Avant | Objectif Après | Gain |
|-----------------|-------|----------------|------|
| Filtre sur price | 165ms | < 20ms | **8x** |
| Filtre sur quantity | 169ms | < 25ms | **7x** |
| Statistiques horaires | 204ms | < 5ms | **40x** |
| JOIN + GROUP BY | 203ms | < 50ms | **4x** |

**Objectif global** : Aucune requête métier > 50ms
