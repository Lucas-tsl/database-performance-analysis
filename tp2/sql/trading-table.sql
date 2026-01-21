
CREATE TABLE dim_pairs (
    pair_id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL, -- ex: 'BTCUSDT'
    base_asset VARCHAR(10) NOT NULL,    -- ex: 'BTC'
    quote_asset VARCHAR(10) NOT NULL    -- ex: 'USDT'
);

CREATE TABLE fact_trades (
    trade_id BIGINT NOT NULL,           -- ID venant de Binance (très grand nombre)
    pair_id INT NOT NULL,
    price DECIMAL(20, 8) NOT NULL,      -- Précision financière
    quantity DECIMAL(20, 8) NOT NULL,
    trade_time TIMESTAMPTZ NOT NULL,    -- Avec TimeZone
    is_buyer_maker BOOLEAN,             -- Indique si l'acheteur a initié l'ordre
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Contrainte de clé primaire composite pour le partitionnement
    PRIMARY KEY (trade_id, trade_time),
    
    -- Clé étrangère
    CONSTRAINT fk_pair
      FOREIGN KEY(pair_id) 
      REFERENCES dim_pairs(pair_id)
) PARTITION BY RANGE (trade_time);

CREATE TABLE trades_default PARTITION OF fact_trades DEFAULT;

-- On crée quelques partitions mensuelles spécifiques (Optionnel pour l'instant, mais bonne pratique)
-- Exemple : Partition pour Janvier 2024
CREATE TABLE trades_y2024m01 PARTITION OF fact_trades
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE INDEX idx_trades_pair ON fact_trades(pair_id);
-- On indexe le temps car ce sera le critère de filtre principal
CREATE INDEX idx_trades_time ON fact_trades(trade_time);

INSERT INTO dim_pairs (symbol, base_asset, quote_asset) 
VALUES ('BTCUSDT', 'BTC', 'USDT')
ON CONFLICT (symbol) DO NOTHING;