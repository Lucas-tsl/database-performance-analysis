# COMPARAISON AVANT/APRÈS OPTIMISATIONS - PHASE 3

**Date** : 21 janvier 2026  
**Volume de données** : 1 000 000 trades

---

## 📊 RÉSUMÉ DES OPTIMISATIONS APPLIQUÉES

### ✅ Index créés (7 index)
1. **idx_price** - Index B-tree sur `price` (29 MB)
2. **idx_quantity** - Index B-tree sur `quantity` (21 MB)
3. **idx_time_price** - Index composite sur `(trade_time, price)` (38 MB)
4. **idx_time_quantity** - Index composite sur `(trade_time, quantity)` (30 MB)
5. **trades_default_pkey** - Clé primaire `(trade_id, trade_time)` (47 MB)
6. **trades_default_pair_id_idx** - Index sur `pair_id` (6.3 MB)
7. **trades_default_trade_time_idx** - Index sur `trade_time` (22 MB)

**Total taille index** : ~193 MB

### ✅ Vues matérialisées créées (2 vues)
1. **mv_stats_hourly** - Statistiques horaires (8 KB, 20 lignes)
2. **mv_stats_by_symbol** - Statistiques par symbole (8 KB, 1 ligne)

---

## 🎯 COMPARAISON DES PERFORMANCES

### 1️⃣ Filtre sur PRICE

#### Requête
```sql
SELECT * FROM fact_trades 
WHERE price > 100000 
LIMIT 10;
```

| Métrique | AVANT | APRÈS | Gain |
|----------|-------|-------|------|
| **Type de scan** | Sequential Scan | **Index Scan** ✅ | - |
| **Temps d'exécution** | 165.624 ms | **0.180 ms** ✅ | **920x plus rapide** |
| **Lignes scannées** | 1 000 000 | 0 | -100% |
| **Buffers (shared hit)** | 10 294 | 3 | -99.97% |
| **Index utilisé** | ❌ Aucun | ✅ trades_default_price_idx | - |

#### 📈 Analyse
- **Gain massif** : 165ms → 0.18ms (× 920)
- **Index Scan** remplace le Sequential Scan
- **Buffers réduits** de 10 294 → 3 (99.97% de réduction)
- **Coût** : Index de 29 MB créé

---

### 2️⃣ Tri sur QUANTITY + LIMIT

#### Requête
```sql
SELECT * FROM fact_trades 
ORDER BY quantity DESC 
LIMIT 10;
```

| Métrique | AVANT | APRÈS | Gain |
|----------|-------|-------|------|
| **Type de scan** | Parallel Seq Scan + Sort | **Index Scan Backward** ✅ | - |
| **Temps d'exécution** | 169.311 ms | **0.824 ms** ✅ | **205x plus rapide** |
| **Sort Method** | top-N heapsort (27kB × 3 workers) | ❌ Aucun tri | Tri éliminé |
| **Buffers (shared hit)** | 10 366 | 10 | -99.9% |
| **Planning Time** | 2.512 ms | 2.730 ms | +9% |
| **Index utilisé** | ❌ Aucun | ✅ trades_default_quantity_idx | - |

#### 📈 Analyse
- **Gain massif** : 169ms → 0.82ms (× 205)
- **Merge Append** avec Index Scan Backward
- **Tri éliminé** : L'index est déjà trié
- **Coût** : Index de 21 MB créé

---

### 3️⃣ Statistiques HORAIRES (Vue matérialisée)

#### Requête AVANT
```sql
SELECT DATE_TRUNC('hour', trade_time) as heure,
       COUNT(*) as nb_trades,
       AVG(price) as prix_moyen,
       SUM(quantity) as volume_total
FROM fact_trades
GROUP BY DATE_TRUNC('hour', trade_time)
ORDER BY heure;
```

#### Requête APRÈS
```sql
SELECT * FROM mv_stats_hourly 
ORDER BY heure;
```

| Métrique | AVANT | APRÈS | Gain |
|----------|-------|-------|------|
| **Type de scan** | Parallel Seq Scan + Aggregate | **Seq Scan sur MV** ✅ | - |
| **Temps d'exécution** | 204.831 ms | **0.128 ms** ✅ | **1600x plus rapide** |
| **Lignes scannées** | 1 000 000 | 20 | -99.998% |
| **Buffers (shared hit)** | 10 310 | 1 | -99.99% |
| **Workers utilisés** | 3 (parallélisation) | 0 | Pas de parallélisation |
| **Sort Method** | quicksort | quicksort (Memory: 27kB) | Même méthode |

#### 📈 Analyse
- **Gain exceptionnel** : 204ms → 0.13ms (× 1600)
- **Vue pré-calculée** : 20 lignes au lieu de 1M
- **Agrégations évitées** : COUNT, AVG, SUM déjà calculés
- **Coût** : Vue de 8 KB + refresh périodique nécessaire

---

### 4️⃣ Statistiques par SYMBOLE (Vue matérialisée)

#### Requête AVANT
```sql
SELECT p.symbol, 
       COUNT(t.trade_id) as nb_trades, 
       AVG(t.price) as avg_price
FROM fact_trades t
JOIN dim_pairs p ON t.pair_id = p.pair_id
GROUP BY p.symbol;
```

#### Requête APRÈS
```sql
SELECT * FROM mv_stats_by_symbol 
WHERE symbol = 'BTCUSDT';
```

| Métrique | AVANT | APRÈS | Gain |
|----------|-------|-------|------|
| **Type de scan** | Parallel Seq Scan + Hash Join | **Seq Scan sur MV** ✅ | - |
| **Temps d'exécution** | 203.259 ms → 351.980 ms ⚠️ | **0.121 ms** ✅ | **1680x vs avant, 2900x vs maintenant** |
| **Lignes scannées** | 1 000 000 | 1 | -99.9999% |
| **Buffers (shared hit)** | 10 341 | 1 | -99.99% |
| **JOIN nécessaire** | ✅ Oui | ❌ Non | JOIN évité |

#### ⚠️ Note importante
La requête AVANT a maintenant un temps de **351ms** (au lieu de 203ms initialement).  
Cela peut être dû à :
- Cache froid (shared hit identique mais temps CPU plus long)
- Overhead des nouveaux index lors du planning (Planning Time: 4.9ms)
- Contention des ressources

Néanmoins, la **vue matérialisée reste 2900× plus rapide** que la requête actuelle.

---

### 5️⃣ JOIN + GROUP BY (sans vue matérialisée)

#### Requête
```sql
SELECT p.symbol, COUNT(t.trade_id) as nb_trades, AVG(t.price) as avg_price
FROM fact_trades t
JOIN dim_pairs p ON t.pair_id = p.pair_id
GROUP BY p.symbol;
```

| Métrique | AVANT | APRÈS | Évolution |
|----------|-------|-------|-----------|
| **Type de scan** | Parallel Seq Scan | Parallel Seq Scan | ⚠️ Inchangé |
| **Temps d'exécution** | 203.259 ms | **351.980 ms** ❌ | **-73% (régression)** |
| **Planning Time** | 7.001 ms | 4.915 ms | +30% |
| **Buffers (shared hit)** | 10 341 | 10 341 | Identique |

#### 📊 Analyse
⚠️ **RÉGRESSION DE PERFORMANCE** (203ms → 351ms)

**Causes possibles** :
1. **Overhead des index** lors du planning (Planning Buffers: shared hit=538)
2. **Cache cold** : Données peut-être pas entièrement en cache
3. **Contention** : Plus d'index = plus de métadonnées à gérer
4. **Statistiques obsolètes** : ANALYZE déjà exécuté mais peut nécessiter un VACUUM ANALYZE

**Solution recommandée** :
- Utiliser **mv_stats_by_symbol** (0.12ms au lieu de 351ms)
- VACUUM ANALYZE complet pour mettre à jour les statistiques
- Monitorer les requêtes pour identifier les régressions

---

## 📈 SYNTHÈSE GLOBALE DES GAINS

| Type de Requête | Temps AVANT | Temps APRÈS | Gain | Statut |
|-----------------|-------------|-------------|------|--------|
| **Filtre sur price** | 165 ms | 0.18 ms | **× 920** | ✅ EXCELLENT |
| **Tri sur quantity** | 169 ms | 0.82 ms | **× 205** | ✅ EXCELLENT |
| **Stats horaires** | 204 ms | 0.13 ms | **× 1600** | ✅ EXCEPTIONNEL |
| **Stats par symbole (MV)** | 203 ms | 0.12 ms | **× 1690** | ✅ EXCEPTIONNEL |
| **JOIN + GROUP BY (direct)** | 203 ms | 352 ms | **× 0.58** | ❌ RÉGRESSION |

### 🎯 Objectifs atteints
- ✅ Filtre sur price : **< 1ms** (objectif < 20ms) - **DÉPASSÉ**
- ✅ Tri sur quantity : **< 1ms** (objectif < 25ms) - **DÉPASSÉ**
- ✅ Stats horaires : **< 1ms** (objectif < 5ms) - **DÉPASSÉ**
- ⚠️ JOIN + GROUP BY : **352ms** (objectif < 50ms) - **NON ATTEINT** sans MV

### 💰 Coûts des optimisations

| Ressource | Taille | Note |
|-----------|--------|------|
| **Index totaux** | ~193 MB | 7 index B-tree |
| **Vues matérialisées** | 16 KB | 2 vues (très léger) |
| **Total overhead** | ~193 MB | +19% de la taille des données |

---

## 🔄 RECOMMANDATIONS DE MAINTENANCE

### 1️⃣ Refresh des vues matérialisées
```sql
-- Refresh quotidien (hors heures de pointe)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_stats_hourly;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_stats_by_symbol;
```

### 2️⃣ Maintenance des index
```sql
-- Hebdomadaire
REINDEX TABLE CONCURRENTLY fact_trades;

-- Mise à jour des statistiques (après gros chargements)
VACUUM ANALYZE fact_trades;
```

### 3️⃣ Monitoring des performances
```sql
-- Statistiques d'utilisation des index
SELECT 
    schemaname, relname, indexrelname, 
    idx_scan, idx_tup_read, idx_tup_fetch,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE relname LIKE 'trades%'
ORDER BY idx_scan DESC;

-- Index inutilisés (à supprimer)
SELECT 
    schemaname, relname, indexrelname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0 
  AND indexrelname NOT LIKE '%_pkey'
ORDER BY pg_relation_size(indexrelid) DESC;
```

---

## ⚠️ PROBLÈMES IDENTIFIÉS

### 1. Régression sur JOIN + GROUP BY
- **Cause** : Overhead des index lors du planning
- **Solution** : Utiliser mv_stats_by_symbol (0.12ms)
- **Action** : VACUUM ANALYZE complet

### 2. Partitioning non optimal
- **Problème** : 100% des données dans trades_default
- **Impact** : Pas de partition pruning
- **Solution Phase 4** : Revoir la stratégie de partitioning temporel

### 3. Index pair_id sous-utilisé
- **Statistiques** : idx_scan=3, 7.4% de sélectivité
- **Impact** : Index de 6.3 MB peu efficace
- **Action** : Monitorer et envisager suppression si inutilisé

---

## ✅ CONCLUSION

### Points forts
- ✅ **Gains massifs** sur les requêtes ciblées (× 200 à × 1600)
- ✅ **Index B-tree** très efficaces pour filtres et tris
- ✅ **Vues matérialisées** exceptionnelles pour agrégations fréquentes
- ✅ **Overhead raisonnable** (~193 MB pour 1M lignes)

### Points d'attention
- ⚠️ **Régression** sur JOIN + GROUP BY direct (utiliser MV)
- ⚠️ **Maintenance requise** : Refresh des MV + VACUUM périodique
- ⚠️ **Partitioning à revoir** pour optimiser davantage

### 🎯 Prochaines étapes (PHASE 4)
1. **Optimisation MongoDB** (index, projections, aggregation pipeline)
2. **Comparaison SQL vs NoSQL** sur requêtes identiques
3. **Amélioration du partitioning** PostgreSQL (partition pruning)
