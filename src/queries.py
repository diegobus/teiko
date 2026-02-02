import pandas as pd


def get_summary(con):
    return pd.read_sql_query("SELECT * FROM summary", con)


def get_melanoma_pbmc_miraclib(con):
    """Get summary data for melanoma PBMC samples treated with miraclib, with response info."""
    return pd.read_sql_query(
        """
        SELECT 
            s.sample_id,
            s.population,
            s.percentage,
            sub.response
        FROM summary s
        JOIN sample sa ON s.sample_id = sa.sample_id
        JOIN subject sub ON sa.subject_id = sub.subject_id
        WHERE sub.condition = 'melanoma'
          AND sub.treatment = 'miraclib'
          AND sa.sample_type = 'PBMC'
        """,
        con,
    )


def get_baseline_melanoma_pbmc_miraclib(con):
    """Get baseline melanoma PBMC samples treated with miraclib."""
    return pd.read_sql_query(
        """
        SELECT 
            sa.sample_id,
            sa.subject_id,
            sub.project_id,
            sub.response,
            sub.sex
        FROM sample sa
        JOIN subject sub ON sa.subject_id = sub.subject_id
        WHERE sub.condition = 'melanoma'
          AND sub.treatment = 'miraclib'
          AND sa.sample_type = 'PBMC'
          AND sa.time_from_treatment_start = 0
        """,
        con,
    )


def get_baseline_summary_counts(con):
    """Get counts by project, response, and sex for baseline samples."""
    df = get_baseline_melanoma_pbmc_miraclib(con)
    
    samples_per_project = df.groupby("project_id").size().reset_index(name="sample_count")
    
    subjects = df.drop_duplicates(subset=["subject_id"])
    responders = subjects.groupby("response").size().reset_index(name="subject_count")
    by_sex = subjects.groupby("sex").size().reset_index(name="subject_count")
    
    return {
        "samples_per_project": samples_per_project,
        "responders": responders,
        "by_sex": by_sex,
    }
