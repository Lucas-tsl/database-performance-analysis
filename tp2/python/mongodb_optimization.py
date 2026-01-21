"""
PHASE 4 : OPTIMISATION MONGODB
Analyse et optimisation des performances MongoDB
"""

import time
import certifi
import os
from pymongo import MongoClient
from datetime import datetime

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://username:password@cluster.mongodb.net/")
DB_NAME = "trading_raw_db"
COLLECTION_NAME = "raw_trades"

def connect_mongodb():
    """Connexion à MongoDB Atlas"""
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    return client, db, collection

def print_separator(title):
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80 + "\n")

def count_documents(collection):
    """Compte le nombre de documents"""
    print_separator("NOMBRE DE DOCUMENTS")
    count = collection.count_documents({})
    print(f"Total documents: {count:,}")
    return count

def test_query_performance(collection, query, description, use_explain=True):
    """Test de performance d'une requête avec explain"""
    print(f"\n--- {description} ---")
    print(f"Requête: {query}")
    
    start = time.time()
    if use_explain:
        explain = collection.find(query).explain()
        execution_time = (time.time() - start) * 1000
        
        exec_stats = explain.get('executionStats', {})
        print(f"\nRésultats:")
        print(f"  - Temps d'exécution: {execution_time:.2f} ms")
        print(f"  - Documents examinés: {exec_stats.get('totalDocsExamined', 0):,}")
        print(f"  - Documents retournés: {exec_stats.get('nReturned', 0):,}")
        print(f"  - Stage: {exec_stats.get('executionStages', {}).get('stage', 'N/A')}")
        
        return {
            'description': description,
            'execution_time_ms': execution_time,
            'docs_examined': exec_stats.get('totalDocsExamined', 0),
            'docs_returned': exec_stats.get('nReturned', 0),
            'stage': exec_stats.get('executionStages', {}).get('stage', 'N/A')
        }
    else:
        result = list(collection.find(query).limit(10))
        execution_time = (time.time() - start) * 1000
        print(f"  - Temps d'exécution: {execution_time:.2f} ms")
        print(f"  - Documents retournés: {len(result)}")
        return {
            'description': description,
            'execution_time_ms': execution_time,
            'docs_returned': len(result)
        }

def analyze_before_optimization(collection):
    """Analyse des performances AVANT optimisation"""
    print_separator("PHASE 4.1 : ANALYSE AVANT OPTIMISATION")
    
    results = []
    
    results.append(test_query_performance(
        collection,
        {"p": {"$gt": 100000}},
        "Filtre sur price > 100000"
    ))
    
    results.append(test_query_performance(
        collection,
        {"T": {"$gte": 1737388800000}},
        "Filtre sur timestamp >= 1737388800000"
    ))
    
    results.append(test_query_performance(
        collection,
        {"p": {"$gte": 85000, "$lte": 95000}, "T": {"$gte": 1737388800000}},
        "Filtre combiné (price BETWEEN 85000-95000 AND timestamp >= 1737388800000)"
    ))
    
    results.append(test_query_performance(
        collection,
        {},
        "Tri sur price DESC LIMIT 10 (sans index)",
        use_explain=False
    ))
    
    print("\n--- Projection sur price et quantity ---")
    start = time.time()
    result = list(collection.find({}, {"p": 1, "q": 1, "_id": 0}).limit(1000))
    execution_time = (time.time() - start) * 1000
    print(f"  - Temps d'exécution: {execution_time:.2f} ms")
    print(f"  - Documents retournés: {len(result)}")
    
    return results

def create_indexes(collection):
    """Création des index MongoDB"""
    print_separator("PHASE 4.2 : CRÉATION DES INDEX")
    
    print("Création de l'index sur 'p' (price)...")
    collection.create_index([("p", 1)], name="idx_price")
    print("✓ Index idx_price créé")
    
    print("\nCréation de l'index sur 'T' (timestamp)...")
    collection.create_index([("T", -1)], name="idx_timestamp")
    print("✓ Index idx_timestamp créé")
    
    print("\nCréation de l'index sur 'q' (quantity)...")
    collection.create_index([("q", -1)], name="idx_quantity")
    print("✓ Index idx_quantity créé")
    
    print("\nCréation de l'index composé sur ('T', 'p')...")
    collection.create_index([("T", -1), ("p", 1)], name="idx_timestamp_price")
    print("✓ Index idx_timestamp_price créé")
    
    print("\n✅ Tous les index ont été créés")

def list_indexes(collection):
    """Liste tous les index"""
    print_separator("LISTE DES INDEX")
    indexes = collection.list_indexes()
    for idx in indexes:
        print(f"  - {idx['name']}: {idx['key']}")

def analyze_after_optimization(collection):
    """Analyse des performances APRÈS optimisation"""
    print_separator("PHASE 4.3 : ANALYSE APRÈS OPTIMISATION")
    
    results = []
    
    results.append(test_query_performance(
        collection,
        {"p": {"$gt": 100000}},
        "Filtre sur price > 100000 (avec index)"
    ))
    
    results.append(test_query_performance(
        collection,
        {"T": {"$gte": 1737388800000}},
        "Filtre sur timestamp >= 1737388800000 (avec index)"
    ))
    
    results.append(test_query_performance(
        collection,
        {"p": {"$gte": 85000, "$lte": 95000}, "T": {"$gte": 1737388800000}},
        "Filtre combiné (avec index composé)"
    ))
    
    print("\n--- Tri sur price DESC LIMIT 10 (avec index) ---")
    start = time.time()
    result = list(collection.find({}).sort("p", -1).limit(10))
    execution_time = (time.time() - start) * 1000
    print(f"  - Temps d'exécution: {execution_time:.2f} ms")
    print(f"  - Documents retournés: {len(result)}")
    
    print("\n--- Projection avec index (price et quantity) ---")
    start = time.time()
    result = list(collection.find({}, {"p": 1, "q": 1, "_id": 0}).limit(1000))
    execution_time = (time.time() - start) * 1000
    print(f"  - Temps d'exécution: {execution_time:.2f} ms")
    print(f"  - Documents retournés: {len(result)}")
    
    return results

def aggregation_pipeline(collection):
    """Tests avec Aggregation Pipeline"""
    print_separator("PHASE 4.4 : AGGREGATION PIPELINE")
    
    print("--- Statistiques globales (AVG, MIN, MAX, SUM) ---")
    start = time.time()
    pipeline = [
        {
            "$group": {
                "_id": None,
                "avg_price": {"$avg": "$p"},
                "min_price": {"$min": "$p"},
                "max_price": {"$max": "$p"},
                "total_quantity": {"$sum": "$q"},
                "count": {"$sum": 1}
            }
        }
    ]
    result = list(collection.aggregate(pipeline))
    execution_time = (time.time() - start) * 1000
    print(f"  - Temps d'exécution: {execution_time:.2f} ms")
    print(f"  - Résultat: {result}")
    
    print("\n--- Statistiques par tranche de prix ---")
    start = time.time()
    pipeline = [
        {
            "$bucket": {
                "groupBy": "$p",
                "boundaries": [85000, 87000, 89000, 91000, 93000, 95000],
                "default": "Autre",
                "output": {
                    "count": {"$sum": 1},
                    "avg_quantity": {"$avg": "$q"}
                }
            }
        }
    ]
    result = list(collection.aggregate(pipeline))
    execution_time = (time.time() - start) * 1000
    print(f"  - Temps d'exécution: {execution_time:.2f} ms")
    print(f"  - Résultat: {result}")

def index_stats(db, collection):
    """Statistiques d'utilisation des index"""
    print_separator("STATISTIQUES DES INDEX")
    
    stats = db.command("collStats", COLLECTION_NAME)
    print(f"Taille de la collection: {stats.get('size', 0) / 1024 / 1024:.2f} MB")
    print(f"Nombre de documents: {stats.get('count', 0):,}")
    print(f"Taille moyenne des documents: {stats.get('avgObjSize', 0):.2f} bytes")
    
    if 'indexSizes' in stats:
        print("\nTaille des index:")
        for idx_name, size in stats['indexSizes'].items():
            print(f"  - {idx_name}: {size / 1024:.2f} KB")

def drop_indexes(collection):
    """Suppression de tous les index (sauf _id)"""
    print_separator("SUPPRESSION DES INDEX")
    collection.drop_indexes()
    print("✓ Tous les index ont été supprimés (sauf _id)")

def main():
    """Fonction principale"""
    print("="*80)
    print(" PHASE 4 : OPTIMISATION MONGODB")
    print(" Analyse et optimisation des performances")
    print("="*80)
    
    client, db, collection = connect_mongodb()
    
    try:
        count_documents(collection)
        drop_indexes(collection)
        results_before = analyze_before_optimization(collection)
        create_indexes(collection)
        list_indexes(collection)
        results_after = analyze_after_optimization(collection)
        aggregation_pipeline(collection)
        index_stats(db, collection)
        
        print_separator("OPTIMISATION MONGODB TERMINÉE")
        print("✅ Tous les tests ont été exécutés avec succès")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()
        print("\n✓ Connexion MongoDB fermée")

if __name__ == "__main__":
    main()
