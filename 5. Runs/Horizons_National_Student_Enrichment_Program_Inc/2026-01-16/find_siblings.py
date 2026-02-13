#!/usr/bin/env python3
"""
Phase 3.1: Find Siblings for Horizons National
Generates mission embedding and finds similar nonprofits using pgvector.

Usage:
    python3 find_siblings.py
"""

import psycopg2
from sentence_transformers import SentenceTransformer
import numpy as np
from datetime import datetime

# Database config
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'thegrantscout',
    'user': 'postgres',
    'password': 'kmalec21'
}

# Client info
CLIENT_EIN = '061468129'
CLIENT_NAME = 'Horizons National Student Enrichment Program Inc.'

def main():
    print(f"\n{'='*60}")
    print("Phase 3.1: Find Siblings for Horizons National")
    print(f"{'='*60}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Connect to database
    print("\n[1/5] Connecting to database...")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Get client data
    print("[2/5] Getting client mission and budget...")
    cur.execute("""
        SELECT name, mission_text, database_revenue
        FROM f990_2025.dim_clients
        WHERE ein = %s
    """, (CLIENT_EIN,))
    result = cur.fetchone()

    if not result:
        print(f"ERROR: Client {CLIENT_EIN} not found")
        return 1

    client_name, mission_text, budget = result
    budget = float(budget)  # Convert Decimal to float
    print(f"    Client: {client_name}")
    print(f"    Mission: {mission_text[:100]}...")
    print(f"    Budget: ${budget:,.0f}")

    # Calculate budget bounds
    budget_lower = int(budget * 0.2)
    budget_upper = int(budget * 5.0)
    print(f"    Budget range for siblings: ${budget_lower:,} - ${budget_upper:,}")

    # Load embedding model
    print("\n[3/5] Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Generate client embedding
    print("[4/5] Generating mission embedding...")
    client_embedding = model.encode(mission_text)
    print(f"    Embedding shape: {client_embedding.shape}")

    # Convert embedding to string format for SQL
    embedding_str = '[' + ','.join(str(float(x)) for x in client_embedding) + ']'

    # Clear existing siblings for this client
    print("\n[5/5] Finding similar nonprofits...")
    cur.execute("""
        DELETE FROM f990_2025.calc_client_siblings
        WHERE client_ein = %s
    """, (CLIENT_EIN,))

    # Find and insert siblings using pgvector (use subquery to handle duplicate EINs)
    cur.execute(f"""
        INSERT INTO f990_2025.calc_client_siblings
            (client_ein, sibling_ein, similarity, client_budget, sibling_budget, budget_ratio)
        SELECT
            %s as client_ein,
            sibling_ein,
            similarity,
            %s as client_budget,
            sibling_budget,
            ROUND((sibling_budget::numeric / %s::numeric), 2) as budget_ratio
        FROM (
            SELECT DISTINCT ON (enm.ein)
                enm.ein as sibling_ein,
                ROUND((1.0 - (enm.mission_embedding_v <=> %s::vector(384)))::NUMERIC, 4) as similarity,
                nr.total_revenue as sibling_budget
            FROM f990_2025.emb_nonprofit_missions enm
            JOIN f990_2025.nonprofit_returns nr ON enm.ein = nr.ein
            WHERE nr.total_revenue BETWEEN %s AND %s
              AND enm.ein != %s
              AND (enm.mission_embedding_v <=> %s::vector(384)) <= 0.50
            ORDER BY enm.ein, nr.tax_year DESC
        ) deduped
        ON CONFLICT (client_ein, sibling_ein) DO UPDATE SET
            similarity = EXCLUDED.similarity,
            sibling_budget = EXCLUDED.sibling_budget,
            budget_ratio = EXCLUDED.budget_ratio,
            computed_at = NOW()
    """, (CLIENT_EIN, int(budget), int(budget), embedding_str,
          budget_lower, budget_upper, CLIENT_EIN, embedding_str))

    conn.commit()

    # Get results
    cur.execute("""
        SELECT
            COUNT(*) as total_siblings,
            ROUND(AVG(similarity)::numeric, 3) as avg_similarity,
            ROUND(MIN(similarity)::numeric, 3) as min_similarity,
            ROUND(MAX(similarity)::numeric, 3) as max_similarity,
            ROUND(AVG(budget_ratio)::numeric, 2) as avg_budget_ratio
        FROM f990_2025.calc_client_siblings
        WHERE client_ein = %s
    """, (CLIENT_EIN,))
    stats = cur.fetchone()

    print(f"\n{'='*60}")
    print("RESULTS")
    print(f"{'='*60}")
    print(f"Total siblings found: {stats[0]}")
    print(f"Similarity - Avg: {stats[1]}, Min: {stats[2]}, Max: {stats[3]}")
    print(f"Average budget ratio: {stats[4]}x")

    # Show top 10 siblings
    print(f"\nTop 10 Most Similar Siblings:")
    print("-" * 60)
    cur.execute("""
        SELECT
            s.sibling_ein,
            nr.organization_name,
            nr.state,
            s.similarity,
            s.sibling_budget
        FROM f990_2025.calc_client_siblings s
        JOIN f990_2025.nonprofit_returns nr ON s.sibling_ein = nr.ein
        WHERE s.client_ein = %s
        ORDER BY s.similarity DESC
        LIMIT 10
    """, (CLIENT_EIN,))

    for row in cur.fetchall():
        ein, name, state, sim, budget = row
        budget_str = f"${budget:,.0f}" if budget else "N/A"
        print(f"  {sim:.3f} | {name[:45]:<45} | {state or 'N/A':<3} | {budget_str}")

    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    cur.close()
    conn.close()
    return 0

if __name__ == '__main__':
    exit(main())
