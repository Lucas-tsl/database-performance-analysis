## Phase 1 — Mise en place de la plateforme de données

### 1. Conception de la base de données

- Concevoir le **schéma relationnel global**
- Définir les relations entre les tables :
    - `students`
    - `courses`
    - `enrollments`
    - `access_logs`
    

### 2. Modélisation et création des tables

- Créer les tables SQL :
    - `students`
    - `courses`
    - `enrollments`
    - `access_logs`
- Définir les **clés primaires** et **clés étrangères**
- Choisir et **justifier les types de données** :
    - entiers, chaînes, dates, timestamps, etc.
    - cohérence avec les usages métier

### 3. Génération des données

- Définir une **méthode de génération automatique** des données :
    - volumes réalistes (petits / moyens / grands)
- Générer les données dans chaque table

### 4. Vérifications initiales

- Vérifier :
    - la **cohérence des données** (relations, clés étrangères)
    - la **taille disque occupée**
    - le **temps de chargement** des données

## Phase 2 — Diagnostic des performances

### 1. Définition des requêtes métier

- Écrire plusieurs requêtes SQL représentatives :
    - requêtes avec **filtres simples**
    - requêtes avec **jointures**
    - requêtes avec **tri + LIMIT**

### 2. Analyse des requêtes

Pour chaque requête :

- Analyser le plan d’exécution avec :
    - `EXPLAIN`
    - `EXPLAIN ANALYZE`
    - `EXPLAIN (ANALYZE, BUFFERS)`

### 3. Interprétation des plans d’exécution

Identifier et expliquer :

- les **types de scan** :
    - Sequential Scan
    - Index Scan
    - Bitmap Scan
- les **opérations de tri**
- les **types de jointures** (Nested Loop, Hash Join, Merge Join)
- les **nœuds dominants** du plan
- les accès :
    - mémoire
    - disque

---

## Phase 3 — Optimisation et validation

### 1. Stratégie d’optimisation

- Proposer une **stratégie d’indexation** :
    - index simples
    - index composites si nécessaire
- Justifier chaque index proposé

### 3. Comparaison avant / après

Comparer :

- les **plans d’exécution**
- les **temps d’exécution**
- l’utilisation des **buffers**

### 2. Mise en œuvre des optimisations

- Créer les index SQL
- Rejouer toutes les requêtes analysées

### 4. Analyse critique

- Identifier :
    - les requêtes **améliorées**
    - celles qui **ne le sont pas**
- Expliquer les raisons (sélectivité, volume, type de jointure, etc.)
- Identifier **au moins une requête mal conçue**
    - expliquer le problème
    - proposer une version corrigée

---

## Livrables attendus

### 1. Rapport PDF

Le rapport doit contenir :

- le **schéma de la base de données**
- le **choix et la justification des types**
- la **méthode de génération des données**
- les **requêtes SQL analysées**
- les **plans d’exécution avant / après**
- l’**analyse des résultats**
- une **conclusion générale**

### 2. Script SQL

Un fichier SQL unique contenant :

- la **création des tables**
- la **génération des données**
- la **création des index**
- les **requêtes utilisées pour l’analyse**

---

Si tu veux, je peux aussi :

- transformer ce plan en **checklist à cocher**
- t’aider à rédiger directement le **plan du rapport PDF**
- proposer une **structure de script SQL propre** adaptée à PostgreSQL