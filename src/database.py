import pandas as pd
import sqlite3 as sql


def get_connection(db_path="immune.db"):
    con = sql.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON;")
    return con


def init_schema(con):
    cur = con.cursor()
    cur.executescript(
        """
        DROP TABLE IF EXISTS summary;
        DROP TABLE IF EXISTS sample;
        DROP TABLE IF EXISTS subject;

        CREATE TABLE subject (
            subject_id TEXT PRIMARY KEY,
            project_id TEXT,
            condition TEXT,
            age INTEGER,
            sex TEXT,
            treatment TEXT,
            response TEXT
        );
                      
        CREATE TABLE sample (
            sample_id TEXT PRIMARY KEY,
            subject_id TEXT NOT NULL,
            sample_type TEXT,
            time_from_treatment_start INTEGER,
            b_cell INTEGER,
            cd8_t_cell INTEGER,
            cd4_t_cell INTEGER,
            nk_cell INTEGER,
            monocyte INTEGER,
            FOREIGN KEY (subject_id) REFERENCES subject(subject_id)
        );

        CREATE INDEX idx_sample_subject_type ON sample(subject_id, sample_type);
        CREATE INDEX idx_sample_type_time_subject ON sample(sample_type, time_from_treatment_start, subject_id);
        CREATE INDEX idx_subject_cohort ON subject(condition, treatment, response);
    """
    )
    con.commit()


def load_data(con, csv_path="cell-count.csv"):
    immune_df = pd.read_csv(csv_path)

    subjects = (
        immune_df[
            ["subject", "project", "condition", "age", "sex", "treatment", "response"]
        ]
        .drop_duplicates()
        .rename(columns={"subject": "subject_id", "project": "project_id"})
    )
    subjects.to_sql("subject", con, if_exists="append", index=False)

    samples = immune_df[
        [
            "sample",
            "subject",
            "sample_type",
            "time_from_treatment_start",
            "b_cell",
            "cd8_t_cell",
            "cd4_t_cell",
            "nk_cell",
            "monocyte",
        ]
    ].rename(columns={"sample": "sample_id", "subject": "subject_id"})
    samples.to_sql("sample", con, if_exists="append", index=False)

    con.commit()


def build_summary_table(con):
    samples_df = pd.read_sql_query(
        """
        SELECT
            sample_id,
            b_cell,
            cd8_t_cell,
            cd4_t_cell,
            nk_cell,
            monocyte
        FROM sample;
    """,
        con,
    )

    cell_cols = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]
    samples_df["total_count"] = samples_df[cell_cols].sum(axis=1)

    new_df = samples_df.melt(
        id_vars=["sample_id", "total_count"],
        value_vars=cell_cols,
        var_name="population",
        value_name="count",
    )
    new_df["percentage"] = new_df["count"] / new_df["total_count"] * 100

    cur = con.cursor()
    cur.executescript(
        """
        DROP TABLE IF EXISTS summary;
        CREATE TABLE summary (
            sample_id TEXT NOT NULL,
            population TEXT NOT NULL,
            total_count INTEGER NOT NULL,
            count INTEGER NOT NULL,
            percentage REAL NOT NULL,
            PRIMARY KEY (sample_id, population),
            FOREIGN KEY (sample_id) REFERENCES sample(sample_id)
        );

        CREATE INDEX idx_summary_population ON summary(population);
    """
    )

    result = new_df[["sample_id", "total_count", "population", "count", "percentage"]]
    result.to_sql("summary", con, if_exists="append", index=False)
    con.commit()


def init_database(db_path="immune.db", csv_path="data/cell-count.csv"):
    con = get_connection(db_path)
    init_schema(con)
    load_data(con, csv_path)
    build_summary_table(con)
    con.close()


if __name__ == "__main__":
    init_database()
