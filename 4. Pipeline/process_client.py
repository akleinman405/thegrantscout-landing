#!/usr/bin/env python3
"""
Process a single client through Phases 1-3 of the foundation matching pipeline.
Usage: python3 process_client.py --ein 123456789
"""

import psycopg2
import argparse
import numpy as np
from datetime import datetime
from sentence_transformers import SentenceTransformer

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'thegrantscout',
    'user': 'postgres',
    'password': 'kmalec21'
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ein', required=True, help='Client EIN')
    args = parser.parse_args()
    client_ein = args.ein

    print(f"\n{'='*60}")
    print(f"Processing Client: {client_ein}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Get client info
    cur.execute("""
        SELECT id, name, ein, state, mission_text, database_revenue,
               matching_grant_keywords, target_grant_purpose
        FROM f990_2025.dim_clients WHERE ein = %s
    """, (client_ein,))
    client = cur.fetchone()

    if not client:
        print(f"ERROR: Client {client_ein} not found")
        return 1

    client_id, name, ein, state, mission, revenue, keywords, target_purpose = client
    print(f"Client: {name}")
    print(f"State: {state}, Revenue: ${revenue:,.0f}")

    if not mission:
        print("ERROR: No mission text")
        return 1
    if not revenue:
        print("ERROR: No database_revenue")
        return 1

    # Load embedding model
    print("\n[1] Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Phase 3.1: Find siblings
    print("\n[2] Finding siblings...")
    budget_lower = int(float(revenue) * 0.2)
    budget_upper = int(float(revenue) * 5.0)
    print(f"    Budget range: ${budget_lower:,} - ${budget_upper:,}")

    mission_embedding = model.encode(mission)
    embedding_str = '[' + ','.join(str(float(x)) for x in mission_embedding) + ']'

    # Clear existing data
    cur.execute("DELETE FROM f990_2025.calc_client_foundation_scores WHERE client_ein = %s", (ein,))
    cur.execute("DELETE FROM f990_2025.calc_client_sibling_grants WHERE client_ein = %s", (ein,))
    cur.execute("DELETE FROM f990_2025.calc_client_siblings WHERE client_ein = %s", (ein,))
    conn.commit()

    # Find siblings
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
        ORDER BY similarity DESC
        LIMIT 500
        ON CONFLICT (client_ein, sibling_ein) DO NOTHING
    """, (ein, int(revenue), int(revenue), embedding_str,
          budget_lower, budget_upper, ein, embedding_str))
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM f990_2025.calc_client_siblings WHERE client_ein = %s", (ein,))
    sibling_count = cur.fetchone()[0]
    print(f"    Found {sibling_count} siblings")

    if sibling_count == 0:
        print("WARNING: No siblings found - trying lower threshold...")
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
                  AND (enm.mission_embedding_v <=> %s::vector(384)) <= 0.55
                ORDER BY enm.ein, nr.tax_year DESC
                LIMIT 100
            ) deduped
            ON CONFLICT (client_ein, sibling_ein) DO NOTHING
        """, (ein, int(revenue), int(revenue), embedding_str,
              budget_lower, budget_upper, ein, embedding_str))
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM f990_2025.calc_client_siblings WHERE client_ein = %s", (ein,))
        sibling_count = cur.fetchone()[0]
        print(f"    Found {sibling_count} siblings with relaxed threshold")

    # Phase 3.2.1: Populate sibling grants
    print("\n[3] Populating sibling grants...")
    cur.execute("""
        INSERT INTO f990_2025.calc_client_sibling_grants
            (client_ein, foundation_ein, sibling_ein, grant_id, amount, tax_year,
             recipient_state, purpose_text, is_first_grant, purpose_quality)
        SELECT
            %s as client_ein,
            fg.foundation_ein,
            fg.recipient_ein as sibling_ein,
            fg.id as grant_id,
            fg.amount,
            fg.tax_year,
            LEFT(fg.recipient_state, 2) as recipient_state,
            fg.purpose_text,
            (fg.tax_year = (
                SELECT MIN(fg2.tax_year)
                FROM f990_2025.fact_grants fg2
                WHERE fg2.foundation_ein = fg.foundation_ein
                AND fg2.recipient_ein = fg.recipient_ein
            )) as is_first_grant,
            CASE
                WHEN fg.purpose_text IS NULL THEN 'NULL'
                WHEN TRIM(fg.purpose_text) = '' THEN 'EMPTY'
                WHEN LENGTH(TRIM(fg.purpose_text)) < 10 THEN 'SHORT'
                ELSE 'VALID'
            END as purpose_quality
        FROM f990_2025.fact_grants fg
        WHERE fg.recipient_ein IN (
            SELECT sibling_ein FROM f990_2025.calc_client_siblings
            WHERE client_ein = %s
        )
    """, (ein, ein))
    conn.commit()

    cur.execute("""
        SELECT COUNT(*), COUNT(DISTINCT foundation_ein),
               COUNT(*) FILTER (WHERE purpose_quality = 'VALID')
        FROM f990_2025.calc_client_sibling_grants WHERE client_ein = %s
    """, (ein,))
    grant_count, foundation_count, valid_count = cur.fetchone()
    print(f"    Grants: {grant_count}, Foundations: {foundation_count}, Valid purpose: {valid_count}")

    # Phase 3.2.2: Semantic similarity
    if target_purpose and valid_count > 0:
        print("\n[4] Computing semantic similarity...")
        target_embedding = model.encode(target_purpose)

        cur.execute("""
            SELECT grant_id, purpose_text FROM f990_2025.calc_client_sibling_grants
            WHERE client_ein = %s AND purpose_quality = 'VALID' AND semantic_similarity IS NULL
        """, (ein,))
        grants = cur.fetchall()

        batch_size = 100
        for i in range(0, len(grants), batch_size):
            batch = grants[i:i+batch_size]
            for grant_id, purpose_text in batch:
                try:
                    purpose_embedding = model.encode(purpose_text)
                    similarity = np.dot(target_embedding, purpose_embedding) / (
                        np.linalg.norm(target_embedding) * np.linalg.norm(purpose_embedding)
                    )
                    cur.execute("""
                        UPDATE f990_2025.calc_client_sibling_grants
                        SET semantic_similarity = %s
                        WHERE client_ein = %s AND grant_id = %s
                    """, (float(round(similarity, 3)), ein, grant_id))
                except:
                    pass
            conn.commit()
            if i % 500 == 0 and i > 0:
                print(f"    Processed {i}/{len(grants)} grants")
        print(f"    Processed {len(grants)} grants for semantic similarity")

    # Phase 3.2.3: Keyword matching
    if keywords:
        print("\n[5] Updating keyword matches...")
        def make_keyword_pattern(kw):
            pattern = kw.replace(' ', r'\s+')
            return f"purpose_text ~* '\\y{pattern}\\y'"
        keyword_conditions = " OR ".join([make_keyword_pattern(kw) for kw in keywords])
        cur.execute(f"""
            UPDATE f990_2025.calc_client_sibling_grants
            SET keyword_match = ({keyword_conditions})
            WHERE client_ein = %s AND purpose_quality = 'VALID'
        """, (ein,))
        cur.execute("""
            UPDATE f990_2025.calc_client_sibling_grants
            SET keyword_match = FALSE
            WHERE client_ein = %s AND purpose_quality != 'VALID'
        """, (ein,))
        conn.commit()

    # Phase 3.2.4: Target grant flags
    print("\n[6] Setting target grant flags...")
    cur.execute("""
        UPDATE f990_2025.calc_client_sibling_grants
        SET
            is_target_grant = CASE
                WHEN keyword_match = TRUE THEN TRUE
                WHEN semantic_similarity IS NULL THEN NULL
                WHEN semantic_similarity >= 0.55 THEN TRUE
                ELSE FALSE
            END,
            target_grant_reason = CASE
                WHEN keyword_match = TRUE AND COALESCE(semantic_similarity, 0) >= 0.55 THEN 'BOTH'
                WHEN keyword_match = TRUE THEN 'KEYWORD'
                WHEN semantic_similarity >= 0.55 THEN 'SEMANTIC'
                ELSE NULL
            END
        WHERE client_ein = %s
    """, (ein,))
    conn.commit()

    # Phase 3.3: Foundation scores
    print("\n[7] Aggregating foundation scores...")
    cur.execute(f"""
        INSERT INTO f990_2025.calc_client_foundation_scores
            (client_ein, client_name, foundation_ein, foundation_name, foundation_state,
             foundation_total_assets, siblings_funded, grants_to_siblings,
             total_amount_to_siblings, median_grant_size_to_siblings,
             target_grants_to_siblings, target_first_grants, unknown_target_count,
             client_state, geo_grants_to_siblings, target_geo_grants, gold_standard_grants,
             most_recent_grant_year, most_recent_target_year, lasso_score)
        SELECT
            %s as client_ein,
            %s as client_name,
            csg.foundation_ein,
            df.name as foundation_name,
            LEFT(df.state, 2) as foundation_state,
            pr.total_assets_eoy_amt as foundation_total_assets,
            COUNT(DISTINCT csg.sibling_ein) as siblings_funded,
            COUNT(*) as grants_to_siblings,
            SUM(csg.amount) as total_amount_to_siblings,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY csg.amount) as median_grant_size_to_siblings,
            COUNT(*) FILTER (WHERE csg.is_target_grant = TRUE) as target_grants_to_siblings,
            COUNT(*) FILTER (WHERE csg.is_target_grant = TRUE AND csg.is_first_grant = TRUE) as target_first_grants,
            COUNT(*) FILTER (WHERE csg.is_target_grant IS NULL) as unknown_target_count,
            %s as client_state,
            COUNT(*) FILTER (WHERE csg.recipient_state = %s) as geo_grants_to_siblings,
            COUNT(*) FILTER (WHERE csg.is_target_grant = TRUE AND csg.recipient_state = %s) as target_geo_grants,
            COUNT(*) FILTER (WHERE csg.is_target_grant = TRUE AND csg.is_first_grant = TRUE AND csg.recipient_state = %s) as gold_standard_grants,
            MAX(csg.tax_year) as most_recent_grant_year,
            MAX(csg.tax_year) FILTER (WHERE csg.is_target_grant = TRUE) as most_recent_target_year,
            NULL::numeric as lasso_score
        FROM f990_2025.calc_client_sibling_grants csg
        JOIN f990_2025.dim_foundations df ON csg.foundation_ein = df.ein
        LEFT JOIN LATERAL (
            SELECT total_assets_eoy_amt
            FROM f990_2025.pf_returns
            WHERE ein = csg.foundation_ein
            ORDER BY tax_year DESC
            LIMIT 1
        ) pr ON TRUE
        WHERE csg.client_ein = %s
        GROUP BY csg.foundation_ein, df.name, LEFT(df.state, 2), pr.total_assets_eoy_amt
    """, (ein, name, state, state, state, state, ein))
    conn.commit()

    # Phase 3.4: Enrichment
    print("\n[8] Enriching foundations...")
    cur.execute("""
        UPDATE f990_2025.calc_client_foundation_scores cfs
        SET
            open_to_applicants = (
                SELECT COALESCE(NOT pr.only_contri_to_preselected_ind, TRUE)
                FROM f990_2025.pf_returns pr
                WHERE pr.ein = cfs.foundation_ein
                ORDER BY pr.tax_year DESC
                LIMIT 1
            ),
            geo_eligible = TRUE,
            client_eligible = CASE
                WHEN cfs.target_grants_to_siblings > 0 THEN TRUE
                ELSE NULL
            END
        WHERE cfs.client_ein = %s
    """, (ein,))
    conn.commit()

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    cur.execute("""
        SELECT
            COUNT(*) as foundations,
            COUNT(*) FILTER (WHERE target_grants_to_siblings > 0) as with_targets,
            COUNT(*) FILTER (WHERE open_to_applicants = TRUE) as open,
            COUNT(*) FILTER (WHERE target_grants_to_siblings > 0 AND open_to_applicants = TRUE) as open_with_targets
        FROM f990_2025.calc_client_foundation_scores WHERE client_ein = %s
    """, (ein,))
    stats = cur.fetchone()

    cur.execute("""
        SELECT COUNT(*) FILTER (WHERE is_target_grant = TRUE)
        FROM f990_2025.calc_client_sibling_grants WHERE client_ein = %s
    """, (ein,))
    target_grants = cur.fetchone()[0]

    print(f"Siblings: {sibling_count}")
    print(f"Grants: {grant_count}")
    print(f"Target Grants: {target_grants}")
    print(f"Foundations: {stats[0]}")
    print(f"  With Target Grants: {stats[1]}")
    print(f"  Open to Applications: {stats[2]}")
    print(f"  Open + Target: {stats[3]}")
    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    cur.close()
    conn.close()
    return 0

if __name__ == '__main__':
    exit(main())
