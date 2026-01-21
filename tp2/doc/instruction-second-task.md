Analyse comparative SQL/NoSQL - Optimisation de performances

## **Objectif général**

Mettre en place et optimiser une plateforme d'analyse de données issues d'une API publique réelle afin de :

structurer efficacement les données

optimiser les requêtes analytiques

comparer les approches SQL et NoSQL

mesurer objectivement les gains de performance

## **PHASE 1 — Mise en place des données (SQL + MongoDB)**

### Objectif

Construire une base exploitable et volumineuse.

### Tâches

Écrire un script Python de collecte depuis une API publique

Stocker :

les données brutes dans MongoDB

les données structurées dans PostgreSQL

Concevoir le modèle SQL (table de mesures + tables de dimensions)

Justifier les choix de :

types de données

clés

structure

### Volumétrie cible

| Type de données | Volume |
| --- | --- |
| Mesures | 500 000 à 1 000 000 |

### Métriques à mesurer

temps d'ingestion

taille occupée sur disque

## **PHASE 2 — Diagnostic des performances (SQL)**

### Requêtes métier à définir

filtres

tris + LIMIT

GROUP BY

jointures

### Outils d'analyse

EXPLAIN

EXPLAIN ANALYZE

EXPLAIN (ANALYZE, BUFFERS)

## **PHASE 3 — Optimisation avancée (SQL)**

### Techniques à mettre en place

un partitionnement temporel

une vue matérialisée

une stratégie d'indexation

### Comparaisons objectifs

les plans d'exécution avant / après

les temps d'exécution

l'utilisation des buffers

## **PHASE 4 — Optimisation MongoDB**

### Tâches

Identifier les requêtes critiques

Mesurer les performances avec explain("executionStats")

Mettre en place :

des index simples

des index composés

des projections

### Comparaisons

COLLSCAN vs IXSCAN

documents examinés

temps d'exécution
