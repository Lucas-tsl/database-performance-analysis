Optimisation et analyse de performances PostgreSQL

## **Objectif général**

Concevoir, analyser et optimiser une base de données PostgreSQL utilisée par une **plateforme e-learning** afin de :

comprendre le fonctionnement interne du moteur PostgreSQL

analyser les plans d’exécution des requêtes

identifier les goulets d’étranglement

mettre en place une stratégie d’indexation pertinente

mesurer objectivement les gains de performance

## Contexte métier

Vous travaillez pour une **plateforme e-learning** qui gère :

des étudiants

des cours

des inscriptions

des logs de connexions

La plateforme subit :

des lenteurs sur certaines pages

des requêtes de reporting très coûteuses

une croissance rapide du volume de données

Vous êtes chargé de **diagnostiquer et corriger les problèmes de performance**.

## **Architecture attendue**

SGBD : PostgreSQL

Environnement : local ou Docker

Outil d’analyse : EXPLAIN / EXPLAIN ANALYZE

Client SQL : DBeaver / pgAdmin / psql

## Modèle de données attendu :

students

courses

enrollments

access_logs

## Volumétrie cible

Les données doivent être générées automatiquement :

| Table | Volume |
| --- | --- |
| students | 200 000 |
| courses | 1 000 |
| enrollments | 2 000 000 |
| access_logs | 5 000 000 |

## Fonctionnement attendu

La base doit permettre :

des requêtes analytiques

des jointures massives

des tris

des filtres sur dates, catégories, étudiants

**Envoyer**

Lever la main

saved