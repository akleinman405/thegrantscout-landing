#!/usr/bin/env python3
"""
V3 Pipeline: Generate Semantic Similarity for Sibling Grants

Calculates cosine similarity between each grant's purpose_text and the client's
target_grant_purpose, then updates the calc_client_sibling_grants table.

Usage:
    cd "/Users/aleckleinman/Documents/TheGrantScout/4. Pipeline"
    python3 phases/phase3_2_sibling_grants/generate_semantic_similarity.py --ein 462730379

Requirements:
    pip3 install sentence-transformers psycopg2-binary python-dotenv numpy

Date: 2026-01-13
"""

import os
import argparse
import psycopg2
from sentence_transformers import SentenceTransformer
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_db_config():
    """Get database configuration from environment variables."""
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_NAME', 'thegrantscout'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', os.getenv('PGPASSWORD', ''))
    }


def main():
    parser = argparse.ArgumentParser(description='Generate semantic similarity for sibling grants')
    parser.add_argument('--ein', required=True, help='Client EIN (e.g., 462730379)')
    parser.add_argument('--batch-size', type=int, default=50, help='Batch size for processing')
    args = parser.parse_args()

    client_ein = args.ein
    batch_size = args.batch_size

    print(f"\n{'='*60}")
    print("V3 Pipeline: Generate Semantic Similarity")
    print(f"{'='*60}")
    print(f"Client EIN: {client_ein}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Connect to database
    print("\n[1/5] Connecting to database...")
    db_config = get_db_config()

    if not db_config['password']:
        print("ERROR: No database password found. Set DB_PASSWORD in .env file.")
        return 1

    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    # Load embedding model
    print("[2/5] Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Get client target grant purpose
    print("[3/5] Getting client target grant purpose...")
    cur.execute("""
        SELECT target_grant_purpose, name
        FROM f990_2025.dim_clients
        WHERE ein = %s
    """, (client_ein,))
    result = cur.fetchone()

    if not result or not result[0]:
        print(f"ERROR: Could not find target_grant_purpose for client {client_ein} in dim_clients")
        print("       Run Phase 2, Step 2.5 to create the target grant purpose first.")
        return 1

    target_grant_purpose = result[0]
    client_name = result[1]
    print(f"    Client: {client_name}")
    print(f"    Target grant purpose: {target_grant_purpose}")

    # Generate client embedding
    print("\n[4/5] Generating target grant purpose embedding...")
    client_embedding = model.encode(target_grant_purpose)
    print(f"    Embedding shape: {client_embedding.shape}")

    # Get all grants with VALID purpose text that need processing
    print("\n[5/5] Processing grants...")
    cur.execute("""
        SELECT grant_id, purpose_text
        FROM f990_2025.calc_client_sibling_grants
        WHERE client_ein = %s
        AND purpose_quality = 'VALID'
        AND semantic_similarity IS NULL
    """, (client_ein,))
    grants = cur.fetchall()

    print(f"    Found {len(grants)} grants to process")

    if len(grants) == 0:
        print("    No grants need processing (already done or none with VALID purpose)")
        return 0

    # Process grants in batches
    updated = 0
    errors = 0

    for i in range(0, len(grants), batch_size):
        batch = grants[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(grants) + batch_size - 1) // batch_size

        print(f"    Processing batch {batch_num}/{total_batches}...")

        for grant_id, purpose_text in batch:
            try:
                # Generate embedding for grant purpose
                purpose_embedding = model.encode(purpose_text)

                # Calculate cosine similarity
                similarity = np.dot(client_embedding, purpose_embedding) / (
                    np.linalg.norm(client_embedding) * np.linalg.norm(purpose_embedding)
                )

                # Update database
                cur.execute("""
                    UPDATE f990_2025.calc_client_sibling_grants
                    SET semantic_similarity = %s
                    WHERE client_ein = %s AND grant_id = %s
                """, (float(round(similarity, 3)), client_ein, grant_id))

                updated += 1

            except Exception as e:
                print(f"    Error processing grant {grant_id}: {e}")
                errors += 1

        # Commit each batch
        conn.commit()

    # Final summary
    print(f"\n{'='*60}")
    print("COMPLETE")
    print(f"{'='*60}")
    print(f"Grants processed: {updated}")
    print(f"Errors: {errors}")

    # Show distribution
    cur.execute("""
        SELECT
            COUNT(*) FILTER (WHERE semantic_similarity >= 0.55) as high_similarity,
            COUNT(*) FILTER (WHERE semantic_similarity >= 0.40 AND semantic_similarity < 0.55) as medium_similarity,
            COUNT(*) FILTER (WHERE semantic_similarity < 0.40) as low_similarity,
            ROUND(AVG(semantic_similarity)::NUMERIC, 3) as avg_similarity,
            ROUND(MIN(semantic_similarity)::NUMERIC, 3) as min_similarity,
            ROUND(MAX(semantic_similarity)::NUMERIC, 3) as max_similarity
        FROM f990_2025.calc_client_sibling_grants
        WHERE client_ein = %s AND semantic_similarity IS NOT NULL
    """, (client_ein,))
    stats = cur.fetchone()

    print(f"\nSimilarity Distribution:")
    print(f"  High (>=0.55):      {stats[0]} grants (will be marked as target)")
    print(f"  Medium (0.40-0.55): {stats[1]} grants")
    print(f"  Low (<0.40):        {stats[2]} grants")
    print(f"\n  Average: {stats[3]}")
    print(f"  Min: {stats[4]}")
    print(f"  Max: {stats[5]}")

    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    cur.close()
    conn.close()
    return 0


if __name__ == '__main__':
    exit(main())
