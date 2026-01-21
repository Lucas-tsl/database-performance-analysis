-- DIAGNOSTIC DES PERFORMANCES AVANT OPTIMISATION

-- Filtre temporel
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM fact_trades 
WHERE trade_time BETWEEN '2026-01-20 15:00:00' AND '2026-01-20 16:00:00';

-- Filtre sur prix
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM fact_trades 
WHERE price > 100000;

-- Filtre sur quantité
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM fact_trades 
WHERE quantity > 1.0;

-- Filtre combiné
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM fact_trades 
WHERE price BETWEEN 95000 AND 105000
  AND trade_time >= '2026-01-20 18:00:00';

-- TRI + LIMIT
EXPLAIN (ANALYZE, BUFFERS)
SELECT trade_id, price, quantity, trade_time
FROM fact_trades 
ORDER BY quantity DESC 
LIMIT 100;

EXPLAIN (ANALYZE, BUFFERS)
SELECT trade_id, price, quantity, trade_time
FROM fact_trades 
ORDER BY trade_time DESC 
LIMIT 1000;

EXPLAIN (ANALYZE, BUFFERS)
SELECT trade_id, price, quantity, trade_time
FROM fact_trades 
ORDER BY price DESC 
LIMIT 500;

-- GROUP BY
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
  DATE_TRUNC('hour', trade_time) as hour,
  COUNT(*) as nb_trades,
  SUM(quantity) as volume_total,
  AVG(price) as prix_moyen,
  MIN(price) as prix_min,
  MAX(price) as prix_max
FROM fact_trades
GROUP BY DATE_TRUNC('hour', trade_time)
ORDER BY hour DESC;

EXPLAIN (ANALYZE, BUFFERS)
SELECT 
  DATE_TRUNC('day', trade_time) as day,
  COUNT(*) as nb_trades,
  SUM(quantity * price::numeric) as volume_usd,
  AVG(price) as prix_moyen
FROM fact_trades
GROUP BY DATE_TRUNC('day', trade_time)
ORDER BY day DESC;

EXPLAIN (ANALYZE, BUFFERS)
SELECT 
  is_buyer_maker,
  COUNT(*) as nb_trades,
  AVG(quantity) as avg_quantity,
  AVG(price) as avg_price
FROM fact_trades
GROUP BY is_buyer_maker;

EXPLAIN (ANALYZE, BUFFERS)
SELECT 
  CASE 
    WHEN price < 95000 THEN '< 95k'
    WHEN price BETWEEN 95000 AND 100000 THEN '95k-100k'
    WHEN price BETWEEN 100000 AND 105000 THEN '100k-105k'
    ELSE '> 105k'
  END as price_range,
  COUNT(*) as nb_trades,
  AVG(quantity) as avg_quantity
FROM fact_trades
GROUP BY price_range
ORDER BY price_range;

REQUÊTES AVEC JOINTURES

EXPLAIN (ANALYZE, BUFFERS)
SELECT 
  p.symbol,
  p.base_currency,
  p.quote_currency,
  COUNT(t.trade_id) as nb_trades,
  AVG(t.price) as avg_price,
  SUM(t.quantity) as total_volume
FROM fact_trades t
JOIN dim_pairs p ON t.pair_id = p.pair_id
GROUP BY p.symbol, p.base_currency, p.quote_currency;

EXPLAIN (ANALYZE, BUFFERS)
SELECT 
  p.symbol,
  DATE_TRUNC('hour', t.trade_time) as hour,
  COUNT(*) as nb_trades,
  MIN(t.price) as low,
  MAX(t.price) as high,
  (array_agg(t.price ORDER BY t.trade_time))[1] as open,
  (array_agg(t.price ORDER BY t.trade_time DESC))[1] as close
FROM fact_trades t
JOIN dim_pairs p ON t.pair_id = p.pair_id
WHERE t.trade_time >= '2026-01-20 18:00:00'
GROUP BY p.symbol, DATE_TRUNC('hour', t.trade_time)
ORDER BY hour DESC;

REQUÊTES COMPLEXES 

EXPLAIN (ANALYZE, BUFFERS)
SELECT 
  DATE_TRUNC('hour', trade_time) as hour,
  COUNT(*) as nb_trades,
  SUM(quantity * price::numeric) as volume_usd
FROM fact_trades
GROUP BY DATE_TRUNC('hour', trade_time)
ORDER BY volume_usd DESC
LIMIT 10;

EXPLAIN (ANALYZE, BUFFERS)
SELECT 
  DATE_TRUNC('minute', trade_time) as minute,
  COUNT(*) as nb_large_trades,
  AVG(price) as avg_price,
  SUM(quantity) as total_btc
FROM fact_trades
WHERE quantity > 0.1
GROUP BY DATE_TRUNC('minute', trade_time)
HAVING COUNT(*) > 5
ORDER BY minute DESC
LIMIT 100;


STATISTIQUES GLOBALES

EXPLAIN (ANALYZE, BUFFERS)
SELECT 
  COUNT(*) as total_trades,
  MIN(trade_time) as first_trade,
  MAX(trade_time) as last_trade,
  MIN(price) as min_price,
  MAX(price) as max_price,
  AVG(price) as avg_price,
  SUM(quantity) as total_volume
FROM fact_trades;

