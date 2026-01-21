import requests
import psycopg2
import time
from pymongo import MongoClient
from datetime import datetime, timezone

# --- CONFIGURATION ---
DB_HOST = "localhost"
DB_PORT = 5434
DB_NAME = "trading_db"
DB_USER = "postgres"
DB_PASS = "testtrading" # <--- METTRE TON MOT DE PASSE ICI

MONGO_URI = "mongodb+srv://lucas:<db_password>@api-mongodb.pdhadgj.mongodb.net/?appName=API-MongoDB"
TARGET_TRADES = 1_000_000  # Objectif : 1 Million de lignes
BATCH_SIZE = 1000          # Limite max de l'API Binance par appel

# --- CONNEXIONS ---
# 1. PostgreSQL
pg_conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASS)
pg_cursor = pg_conn.cursor()

# 2. MongoDB
mongo_client = MongoClient(MONGO_URI)
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
    # On commence par "maintenant" et on recule dans le temps
    end_time = None 
    
    print(f"🚀 Démarrage de la collecte pour {symbol}...")
    start_global = time.time()

    while collected_count < TARGET_TRADES:
        try:
            # 1. API CALL (Binance)
            url = "https://api.binance.com/api/v3/aggTrades"
            params = {"symbol": symbol, "limit": BATCH_SIZE}
            if end_time:
                params["endTime"] = end_time

            response = requests.get(url, params=params)
            data = response.json()

            if not data:
                print("Plus de données disponibles.")
                break

            # 2. STOCKAGE MONGODB (Données brutes)
            # On insère tout le bloc JSON tel quel
            if data:
                mongo_collection.insert_many(data)

            # 3. TRANSFORMATION & STOCKAGE POSTGRESQL
            pg_values = []
            for trade in data:
                # Mapping des champs Binance
                t_id = trade['a']           # Aggregate Trade ID
                price = trade['p']          # Price
                qty = trade['q']            # Quantity
                # Conversion Timestamp ms -> DateTime avec Timezone
                t_time = datetime.fromtimestamp(trade['T'] / 1000, tz=timezone.utc)
                is_maker = trade['m']       # Was the buyer the maker?
                
                pg_values.append((t_id, pair_id, price, qty, t_time, is_maker))

            # Insertion Bulk (beaucoup plus rapide que insert one-by-one)
            args_str = ','.join(pg_cursor.mogrify("(%s,%s,%s,%s,%s,%s)", x).decode('utf-8') for x in pg_values)
            pg_cursor.execute("INSERT INTO fact_trades (trade_id, pair_id, price, quantity, trade_time, is_buyer_maker) VALUES " + args_str + " ON CONFLICT DO NOTHING")
            pg_conn.commit()

            # Mise à jour des compteurs
            collected_count += len(data)
            
            # Pour la prochaine boucle, on prend le timestamp du plus vieux trade récupéré - 1ms
            end_time = data[0]['T'] - 1 

            print(f"✅ {collected_count}/{TARGET_TRADES} trades collectés. (Dernier: {t_time})")
            
            # Petit sleep pour être gentil avec l'API (évite le ban IP)
            time.sleep(0.1)

        except Exception as e:
            print(f"❌ Erreur : {e}")
            time.sleep(5) # Pause en cas d'erreur réseau

    duration = time.time() - start_global
    print(f"\n🎉 Terminé ! {collected_count} trades insérés en {duration:.2f} secondes.")
    print(f"Vitesse moyenne : {collected_count/duration:.0f} trades/sec")

    # Fermeture
    pg_cursor.close()
    pg_conn.close()
    mongo_client.close()

if __name__ == "__main__":
    run_etl()