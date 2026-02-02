import streamlit as st
from src.database import get_connection
from src.queries import (
    get_summary,
    get_melanoma_pbmc_miraclib,
    get_baseline_summary_counts,
)
from src.analysis import compare_responders_vs_non
from src.visualization import boxplot_by_response

st.set_page_config(page_title="Immune Cell Analysis", layout="wide")
st.title("Teiko Technical Dashboard")
st.subheader("Immune Cell Population Analysis")

con = get_connection()

# Part 2: Summary Table
st.header("Summary Table")
summary_df = get_summary(con)
st.dataframe(summary_df, use_container_width=True)

# Part 3: Statistical Analysis
st.header("Responder vs Non-Responder Analysis")
st.subheader("Melanoma PBMC Samples (miraclib treatment)")

melanoma_df = get_melanoma_pbmc_miraclib(con)

fig = boxplot_by_response(melanoma_df)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Statistical Comparison (Mann-Whitney U)")
stats_df = compare_responders_vs_non(melanoma_df)
st.dataframe(stats_df, use_container_width=True)

significant = stats_df[stats_df["significant"]]
if not significant.empty:
    st.success(
        f"Significant differences found in: {', '.join(significant['population'].tolist())}"
    )
else:
    st.info("No significant differences found at p < 0.05")

# Part 4: Baseline Analysis
st.header("Baseline Analysis (time=0)")
st.subheader("Melanoma PBMC Samples (miraclib treatment)")

counts = get_baseline_summary_counts(con)

col1, col2, col3 = st.columns(3)

with col1:
    st.write("**Samples per Project**")
    st.dataframe(counts["samples_per_project"], use_container_width=True)

with col2:
    st.write("**Subjects by Response**")
    st.dataframe(counts["responders"], use_container_width=True)

with col3:
    st.write("**Subjects by Sex**")
    st.dataframe(counts["by_sex"], use_container_width=True)

con.close()
