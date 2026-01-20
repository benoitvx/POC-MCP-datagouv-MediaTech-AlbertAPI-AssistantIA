#!/usr/bin/env python3
"""
Script d'exploration du catalogue Mediatech
Alternative au notebook pour test rapide

Usage: 
    cd poc-datagouv
    source .venv/bin/activate
    python scripts/explore_mediatech.py
"""

import duckdb
import json
import os

# Configuration
PARQUET_GLOB = "huggingface/data_gouv_datasets_catalog_part_*.parquet"
EMB_COL = "embeddings_bge-m3"

def main():
    print("=" * 60)
    print("📊 EXPLORATION DU CATALOGUE MEDIATECH")
    print("=" * 60)
    
    # 1. Charger avec DuckDB
    print("\n🦆 Chargement avec DuckDB...")
    con = duckdb.connect()
    con.execute(f"CREATE VIEW mediatech AS SELECT * FROM read_parquet('{PARQUET_GLOB}')")
    
    # 2. Schéma
    print("\n📋 SCHÉMA (40 colonnes) :")
    print("-" * 40)
    schema = con.execute("DESCRIBE mediatech").fetchall()
    for col_name, col_type, *_ in schema:
        print(f"  {col_name:35} {col_type}")
    
    # 3. Stats de base
    count = con.execute("SELECT COUNT(*) FROM mediatech").fetchone()[0]
    nb_orgs = con.execute("SELECT COUNT(DISTINCT organization) FROM mediatech").fetchone()[0]
    print(f"\n📊 Datasets : {count:,}")
    print(f"📊 Organisations : {nb_orgs:,}")
    
    # 4. Top organisations
    print("\n🏢 TOP 10 ORGANISATIONS :")
    print("-" * 40)
    top_orgs = con.execute("""
        SELECT organization, COUNT(*) as nb
        FROM mediatech
        WHERE organization IS NOT NULL
        GROUP BY organization
        ORDER BY nb DESC
        LIMIT 10
    """).fetchall()
    for org, nb in top_orgs:
        org_display = (org[:42] + "...") if org and len(org) > 45 else (org or "N/A")
        print(f"  {org_display:45} {nb:>6}")
    
    # 5. Embeddings
    print("\n🔍 EMBEDDINGS BGE-M3 :")
    print("-" * 40)
    
    # Couverture
    cov = con.execute(f"""
        SELECT 
            COUNT(*) as total,
            COUNT("{EMB_COL}") as avec_emb
        FROM mediatech
    """).fetchone()
    print(f"  Couverture : {cov[1]:,} / {cov[0]:,} ({100*cov[1]/cov[0]:.1f}%)")
    
    # Format et dimension
    sample = con.execute(f"""
        SELECT "{EMB_COL}" FROM mediatech 
        WHERE "{EMB_COL}" IS NOT NULL 
        LIMIT 1
    """).fetchone()[0]
    
    print(f"  Format brut : string (JSON)")
    embedding = json.loads(sample)
    print(f"  Dimension : {len(embedding)}")
    print(f"  Exemple : {embedding[:3]}...")
    
    # 6. Top datasets
    print("\n🔥 TOP 5 DATASETS (par vues) :")
    print("-" * 40)
    top = con.execute("""
        SELECT title, metric_views
        FROM mediatech
        WHERE metric_views IS NOT NULL
        ORDER BY metric_views DESC
        LIMIT 5
    """).fetchall()
    for title, views in top:
        title_display = (title[:47] + "...") if title and len(title) > 50 else (title or "N/A")
        print(f"  {title_display:50} {views:>8} vues")
    
    print("\n" + "=" * 60)
    print("✅ Exploration terminée")
    print("   → Prêt pour la recherche vectorielle avec Albert API")
    print("=" * 60)

if __name__ == "__main__":
    main()
