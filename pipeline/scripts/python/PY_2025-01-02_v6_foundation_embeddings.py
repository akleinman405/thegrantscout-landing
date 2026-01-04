#!/usr/bin/env python3
"""
PY_2025-01-02_v6_foundation_embeddings.py
Create foundation average embeddings for V6 model.

Computes the average of all grant purpose embeddings for each foundation.
This enables semantic similarity matching between clients and foundations.

Usage:
    python3 scripts/python/PY_2025-01-02_v6_foundation_embeddings.py

Output:
    Creates table: f990_2025.calc_foundation_avg_embedding
"""

import sys
import numpy as np
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from collections import defaultdict

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'thegrantscout',
    'user': 'postgres',
    'password': 'kmalec21'
}

BATCH_SIZE = 50000  # Process grants in batches
EMBEDDING_DIM = 384


def log(msg):
    """Print timestamped log message."""
    print(f"[{datetime.now():%H:%M:%S}] {msg}")


def connect_db():
    """Connect to PostgreSQL database."""
    return psycopg2.connect(**DB_CONFIG)


def create_output_table(conn):
    """Create or replace the output table."""
    log("Creating output table...")

    with conn.cursor() as cur:
        cur.execute("""
            DROP TABLE IF EXISTS f990_2025.calc_foundation_avg_embedding;

            CREATE TABLE f990_2025.calc_foundation_avg_embedding (
                foundation_ein VARCHAR(20) PRIMARY KEY,
                avg_embedding float8[],
                avg_embedding_v vector(384),
                grant_count INTEGER,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
    conn.commit()
    log("Output table created")


def get_foundation_grant_counts(conn):
    """Get count of grants with embeddings per foundation."""
    log("Counting grants per foundation...")

    with conn.cursor() as cur:
        cur.execute("""
            SELECT fg.foundation_ein, COUNT(*) as cnt
            FROM f990_2025.fact_grants fg
            JOIN f990_2025.emb_grant_purposes ge ON fg.id = ge.grant_id
            WHERE ge.purpose_embedding IS NOT NULL
              AND fg.foundation_ein IS NOT NULL
            GROUP BY fg.foundation_ein
        """)
        counts = {row[0]: row[1] for row in cur.fetchall()}

    log(f"Found {len(counts)} foundations with embeddings")
    total_grants = sum(counts.values())
    log(f"Total grants to process: {total_grants:,}")

    return counts


def compute_averages_streaming(conn):
    """Compute foundation averages using streaming to handle large data."""
    log("Computing foundation average embeddings (streaming)...")

    # Accumulators: foundation_ein -> (sum_embedding, count)
    accumulators = defaultdict(lambda: [np.zeros(EMBEDDING_DIM), 0])

    # Query grants in batches using cursor
    with conn.cursor(name='grant_cursor') as cur:
        cur.itersize = BATCH_SIZE

        cur.execute("""
            SELECT fg.foundation_ein, ge.purpose_embedding
            FROM f990_2025.fact_grants fg
            JOIN f990_2025.emb_grant_purposes ge ON fg.id = ge.grant_id
            WHERE ge.purpose_embedding IS NOT NULL
              AND fg.foundation_ein IS NOT NULL
        """)

        processed = 0
        for row in cur:
            foundation_ein = row[0]
            embedding = np.array(row[1], dtype=np.float32)

            accumulators[foundation_ein][0] += embedding
            accumulators[foundation_ein][1] += 1

            processed += 1
            if processed % 500000 == 0:
                log(f"  Processed {processed:,} grants ({len(accumulators)} foundations)")

    log(f"Finished processing {processed:,} grants")
    log(f"Computing averages for {len(accumulators)} foundations...")

    # Compute averages
    results = []
    for foundation_ein, (sum_emb, count) in accumulators.items():
        avg_emb = sum_emb / count
        # Normalize to unit vector for cosine similarity
        norm = np.linalg.norm(avg_emb)
        if norm > 0:
            avg_emb = avg_emb / norm
        results.append((foundation_ein, avg_emb.tolist(), count))

    log(f"Computed {len(results)} foundation averages")
    return results


def insert_results(conn, results):
    """Insert computed averages into database."""
    log(f"Inserting {len(results)} foundation embeddings...")

    with conn.cursor() as cur:
        # Insert in batches
        batch_size = 1000
        for i in range(0, len(results), batch_size):
            batch = results[i:i+batch_size]

            # Prepare data: (ein, embedding_array, count)
            values = [(ein, emb, count) for ein, emb, count in batch]

            execute_values(
                cur,
                """
                INSERT INTO f990_2025.calc_foundation_avg_embedding
                    (foundation_ein, avg_embedding, grant_count)
                VALUES %s
                """,
                values,
                template="(%s, %s::float8[], %s)"
            )

            if (i + batch_size) % 10000 == 0:
                log(f"  Inserted {min(i + batch_size, len(results)):,} rows")
                conn.commit()

        conn.commit()

    log("Insertion complete")


def create_vector_column(conn):
    """Convert array to pgvector for fast similarity queries."""
    log("Creating pgvector column...")

    with conn.cursor() as cur:
        cur.execute("""
            UPDATE f990_2025.calc_foundation_avg_embedding
            SET avg_embedding_v = avg_embedding::vector(384)
            WHERE avg_embedding IS NOT NULL;
        """)

        # Create index for fast similarity search
        cur.execute("""
            CREATE INDEX idx_fae_embedding
            ON f990_2025.calc_foundation_avg_embedding
            USING ivfflat (avg_embedding_v vector_cosine_ops)
            WITH (lists = 100);
        """)

        cur.execute("""
            CREATE INDEX idx_fae_ein
            ON f990_2025.calc_foundation_avg_embedding (foundation_ein);
        """)

    conn.commit()
    log("Vector column and indexes created")


def verify_results(conn):
    """Verify the results."""
    log("Verifying results...")

    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN avg_embedding_v IS NOT NULL THEN 1 ELSE 0 END) as with_vector,
                AVG(grant_count) as avg_grants,
                MIN(grant_count) as min_grants,
                MAX(grant_count) as max_grants
            FROM f990_2025.calc_foundation_avg_embedding
        """)
        row = cur.fetchone()

        log(f"Results:")
        log(f"  Total foundations: {row[0]:,}")
        log(f"  With vector: {row[1]:,}")
        log(f"  Avg grants per foundation: {row[2]:.1f}")
        log(f"  Min/Max grants: {row[3]} / {row[4]}")

        # Sample a similarity query
        cur.execute("""
            SELECT foundation_ein, grant_count
            FROM f990_2025.calc_foundation_avg_embedding
            ORDER BY grant_count DESC
            LIMIT 5
        """)
        log("Top 5 foundations by grant count:")
        for row in cur.fetchall():
            log(f"    {row[0]}: {row[1]} grants")


def main():
    """Main execution."""
    print("=" * 60)
    print("Foundation Average Embeddings Generator")
    print("=" * 60)

    start_time = datetime.now()

    log("Connecting to database...")
    conn = connect_db()

    try:
        # Create output table
        create_output_table(conn)

        # Compute averages
        results = compute_averages_streaming(conn)

        # Insert results
        insert_results(conn, results)

        # Create vector column and index
        create_vector_column(conn)

        # Verify
        verify_results(conn)

    finally:
        conn.close()

    elapsed = datetime.now() - start_time
    log(f"Total time: {elapsed}")

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)
    print(f"\nOutput table: f990_2025.calc_foundation_avg_embedding")
    print(f"Use this for semantic similarity in V6 model training")


if __name__ == '__main__':
    main()
