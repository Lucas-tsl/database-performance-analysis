# 📊 Analyse de Performance des Bases de Données

Projet d'analyse et d'optimisation des performances de bases de données relationnelles (PostgreSQL) et NoSQL (MongoDB) dans le cadre du Mastère Spécialisé en Big Data.

---

---

## 🎯 TP1 : Performance des Bases de Données Relationnelles

### Objectif
Analyser et optimiser les performances d'une base de données PostgreSQL à l'aide de requêtes SQL réalistes, de plans d'exécution et de techniques d'indexation.

### Thème
Gestion d'un système de **réservation de cinéma** avec :
- Gestion des films et des séances
- Réservations de places
- Gestion des salles et des tarifs
- Analyse des ventes



### Exécution
```bash
cd tp1
docker compose up -d
# Lancer les scripts SQL dans l'ordre présent dans le dossier sql/
```

---

## 🚀 TP2 : Analyse Comparative SQL vs NoSQL

### Objectif
Mettre en place et optimiser une plateforme d'analyse de données issues d'une API publique (Binance) pour :
- Structurer efficacement les données
- Optimiser les requêtes analytiques
- Comparer les approches SQL et NoSQL
- Mesurer objectivement les gains de performance

### Thème
Analyse des **trades en temps réel** depuis l'API Binance (BTCUSDT) avec :
- Collecte de 1 000 000 de trades
- Stockage dual : PostgreSQL + MongoDB
- Optimisation avancée (index, vues matérialisées, partitioning)
- Comparaison de performance SQL vs NoSQL


### 📋 Les 4 Phases du Projet

#### **PHASE 1 : Mise en place des données** ✅
- Script Python de collecte depuis l'API Binance
- Stockage des données brutes dans MongoDB (JSON)
- Stockage structuré dans PostgreSQL (tables normalisées + partitioning)
- **Résultat** : 1 000 000 trades collectés en ~40 minutes (407 trades/sec)

#### **PHASE 2 : Diagnostic des performances SQL** ✅
- Analyse de 6 types de requêtes métier (filtres, tris, GROUP BY, JOIN)
- Utilisation de EXPLAIN (ANALYZE, BUFFERS)
- Identification des Sequential Scans et des manques d'index
- **Résultat** : Requêtes entre 48ms et 204ms sans optimisation

#### **PHASE 3 : Optimisation avancée SQL** ✅
- Création de 7 index B-tree (price, quantity, composés)
- 2 vues matérialisées (statistiques horaires et par symbole)
- ANALYZE des tables pour mise à jour des statistiques
- **Résultats** :
  - Filtre sur price : 165ms → **0.18ms** (× 920)
  - Tri sur quantity : 169ms → **0.82ms** (× 205)
  - Stats horaires : 204ms → **0.13ms** (× 1600)
  - Stats par symbole : 203ms → **0.12ms** (× 1690)

#### **PHASE 4 : Optimisation MongoDB** ✅
- Analyse AVANT optimisation (COLLSCAN)
- Création de 4 index (price, timestamp, quantity, composé)
- Analyse APRÈS optimisation (IXSCAN)
- Tests avec Aggregation Pipeline
- **Résultats** :
  - Filtre sur price : 687ms → **79ms** (× 8.6)
  - MongoDB reste **440× plus lent** que PostgreSQL optimisé

### Exécution

#### 1. Démarrer PostgreSQL
```bash
cd tp2
docker compose up -d
```

#### 2. Créer l'environnement Python
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install requests psycopg2-binary pymongo certifi
```

#### 3. Créer le schéma PostgreSQL
```bash
docker exec -i postgres_trading psql -U admin -d trading_db < sql/create-table.sql
```

#### 4. Collecter les données (Phase 1)
```bash
python python/collect_data.py
# Collecte 1M trades depuis Binance (~ 40 min)
```

#### 5. Appliquer les optimisations (Phase 3)
```bash
docker exec -i postgres_trading psql -U admin -d trading_db < sql/optimizations.sql
```

#### 6. Tester MongoDB (Phase 4)
```bash
python python/mongodb_optimization.py
```

---

## 📊 Résultats Comparatifs

### PostgreSQL vs MongoDB (après optimisation)

| Type de Requête | PostgreSQL | MongoDB | Gagnant |
|-----------------|------------|---------|---------|
| **Filtre sur prix** | 0.18 ms | 79 ms | PostgreSQL (× 440) |
| **Tri + LIMIT** | 0.82 ms | - | PostgreSQL |
| **Statistiques globales** | 0.12 ms (MV) | - | PostgreSQL || **Gain d'optimisation** | × 920 | × 8.6 | PostgreSQL |

## 🛠️ Technologies Utilisées

| Technologie | Version | Usage |
|-------------|---------|-------|
| **PostgreSQL** | 15-alpine | Base de données relationnelle |
| **MongoDB Atlas** | Cloud | Base de données NoSQL |
| **Python** | 3.13 | Scripts ETL et analyse |
| **Docker** | Latest | Conteneurisation |
| **psycopg2-binary** | 2.9.11 | Driver PostgreSQL |
| **pymongo** | 4.16.0 | Driver MongoDB |
| **requests** | 2.32.5 | Appels API Binance |
| **certifi** | 2026.1.4 | Certificats SSL MongoDB |

---

## 📖 Documentation

### TP1
- [README.md](tp1/README.md) - Vue d'ensemble du projet
- Documentation SQL dans `tp1/docs/`

### TP2
- [instruction-second-task.md](tp2/doc/instruction-second-task.md) - Consignes du projet
- [analyse-request.md](tp2/doc/analyse-request.md) - Analyse Phase 2 (diagnostic)
- [comparaison-avant-apres.md](tp2/doc/comparaison-avant-apres.md) - Résultats Phase 3 (SQL)
- [mongodb-optimisation.md](tp2/doc/mongodb-optimisation.md) - Résultats Phase 4 (NoSQL)

---

## 👨‍💻 Auteur

**Lucas**  
Mastère Spécialisé Big Data - Bordeaux Ynov Campus  
Janvier 2026

---

## 📝 Licence

Projet académique - Tous droits réservés
