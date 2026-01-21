-- PHASE 3 : OPTIMISATIONS SQL

-- 1. INDEXATION
CREATE INDEX IF NOT EXISTS idx_price ON fact_trades(price);
CREATE INDEX IF NOT EXISTS idx_quantity ON fact_trades(quantity);
CREATE INDEX IF NOT EXISTS idx_time_price ON fact_trades(trade_time, price);
CREATE INDEX IF NOT EXISTS idx_time_quantity ON fact_trades(trade_time, quantity);

-- 2. VUES MATÉRIALISÉES
DROP MATERIALIZED VIEW IF EXISTS mv_stats_hourly CASCADE;

CREATE MATERIALIZED VIEW mv_stats_hourly AS
SELECT 
    DATE_TRUNC('hour', trade_time) as heure,
    COUNT(*) as nb_trades,
    AVG(price) as prix_moyen,
    SUM(quantity) as volume_total,
    MAX(price) as prix_max,
    MIN(price) as prix_min,
    STDDEV(price) as stddev_price
FROM fact_trades
GROUP BY DATE_TRUNC('hour', trade_time)
WITH DATA;

CREATE INDEX idx_mv_stats_hourly ON mv_stats_hourly(heure);

DROP MATERIALIZED VIEW IF EXISTS mv_stats_by_symbol CASCADE;

CREATE MATERIALIZED VIEW mv_stats_by_symbol AS
SELECT 
    p.symbol,
    COUNT(t.trade_id) as nb_trades,
    AVG(t.price) as prix_moyen,
    SUM(t.quantity) as volume_total,
    MAX(t.price) as prix_max,
    MIN(t.price) as prix_min
FROM fact_trades t
JOIN dim_pairs p ON t.pair_id = p.pair_id
GROUP BY p.symbol
WITH DATA;

CREATE INDEX idx_mv_stats_symbol ON mv_stats_by_symbol(symbol);

-- 3. MISE À JOUR DES STATISTIQUES
ANALYZE fact_trades;
ANALYZE dim_pairs;
ANALYZE mv_stats_hourly;
ANALYZE mv_stats_by_symbol;

-- 4. VÉRIFICATION
SELECT schemaname, tablename, indexname, indexdef
FROM pg_indexes
WHERE tablename IN ('fact_trades', 'trades_default')
ORDER BY tablename, indexname;

SELECT schemaname, tablename, indexname, pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE relname IN ('fact_trades', 'trades_default')
ORDER BY pg_relation_size(indexrelid) DESC;

SELECT schemaname, matviewname, pg_size_pretty(pg_relation_size(matviewname::regclass)) as size
FROM pg_matviews
ORDER BY matviewname;
