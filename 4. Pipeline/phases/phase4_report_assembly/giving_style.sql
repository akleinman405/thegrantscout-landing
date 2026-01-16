-- Giving Style Query
-- Returns general support vs program-specific percentage

SELECT
    foundation_ein,
    SUM(CASE
        WHEN LOWER(purpose_text) ~ '(general|operating|unrestricted)' THEN 1
        ELSE 0
    END) as general_support_count,
    SUM(CASE
        WHEN LOWER(purpose_text) ~ '(program|project|initiative|specific)' THEN 1
        ELSE 0
    END) as program_specific_count,
    COUNT(CASE WHEN purpose_text IS NOT NULL AND purpose_text != '' THEN 1 END) as classified_grants,
    CASE
        WHEN COUNT(CASE WHEN purpose_text IS NOT NULL AND purpose_text != '' THEN 1 END) > 0
        THEN SUM(CASE WHEN LOWER(purpose_text) ~ '(general|operating|unrestricted)' THEN 1 ELSE 0 END)::float /
             COUNT(CASE WHEN purpose_text IS NOT NULL AND purpose_text != '' THEN 1 END)
        ELSE 0.5
    END as general_support_pct
FROM f990_2025.fact_grants
WHERE foundation_ein = %(foundation_ein)s
GROUP BY foundation_ein;
