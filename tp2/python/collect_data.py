import requests
import psycopg2
import time
from pymongo import MongoClient
from datetime import datetime, timezone
import ssl
import certifi
import os

# --- CONFIGURATION ---
DB_HOST = "localhost"
DB_PORT = 5434
DB_NAME = "trading_db"
DB_USER = "admin"
DB_PASS = os.getenv("POSTGRES_PASSWORD", "your_password_here")

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://username:password@cluster.mongodb.net/")
TARGET_TRADES = 1_000_000  # Objectif : 1 Million de lignes
BATCH_SIZE = 1000          # Limite max de l'API Binance par appel

# --- CONNEXIONS ---
# 1. PostgreSQL
pg_conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASS)
pg_cursor = pg_conn.cursor()

# 2. MongoDB
mongo_client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
mongo_db = mongo_client["trading_raw_db"]
mongo_collection = mongo_db["raw_trades"]

def get_pair_id(symbol):
    """Récupère l'ID de la paire depuis PostgreSQL"""
    pg_cursor.execute("SELECT pair_id FROM dim_pairs WHERE symbol = %s", (symbol,))
    result = pg_cursor.fetchone()
    if result:
        return result[0]
    else:
        raise Exception(f"Paire {symbol} non trouvée dans dim_pairs. Exécutez le SQL d'abord.")

def run_etl():
    symbol = "BTCUSDT"
    pair_id = get_pair_id(symbol)
    
    collected_count = 0
    end_time = None 
    
    print(f"🚀 Démarrage de la collecte pour {symbol}...")
    start_global = time.time()

    while collected_count < TARGET_TRADES:
        params = {
            "symbol": symbol,
            "limit": BATCH_SIZE
        }
        if end_time:
            params["endTime"] = end_time - 1

        try:
            response = requests.get("https://api.binance.com/api/v3/trades", params=params)
            response.raise_for_status()
            trades = response.json()

            if not trades:
                print("⚠️ Plus de données disponibles. Arrêt.")
                break

            mongo_collection.insert_many(trades)

            values_list = []
            for trade in trades:
                values_list.append((
                    trade["id"],
                    pair_id,
                    float(trade["price"]),
                    float(trade["qty"]),
                    datetime.fromtimestamp(trade["time"] / 1000.0, tz=timezone.utc),
                    trade["isBuyerMaker"]
                ))

            pg_cursor.executemany(
                """
                INSERT INTO fact_trades (trade_id, pair_id, price, quantity, trade_time, is_buyer_maker)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (trade_id, trade_time) DO NOTHING
                """,
                values_list
            )
            pg_conn.commit()

            collected_count += len(trades)
            end_time = trades[-1]["time"]

            elapsed = time.time() - start_global
            rate = collected_count / elapsed if elapsed > 0 else 0
            print(f"✅ {collected_count:,} trades collectés | Vitesse: {rate:.2f} trades/sec | Dernier timestamp: {end_time}")

            time.sleep(0.1)

        except Exception as e:
            print(f"❌ Erreur : {e}")
            pg_conn.rollback()
            break

    elapsed_total = time.time() - start_global
    print(f"\n🎉 Collecte terminée : {collected_count:,} trades en {elapsed_total:.2f} secondes")
    print(f"📊 Vitesse moyenne : {collected_count / elapsed_total:.2f} trades/sec")

    pg_cursor.close()
    pg_conn.close()
    mongo_client.close()

if __name__ == "__main__":
    run_etl()
