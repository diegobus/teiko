from scipy import stats
import pandas as pd


def compare_responders_vs_non(df):
    """
    Compare population frequencies between responders and non-responders and finds
    significant differences using Mann-Whitney U test because unsure if data is
    normally distributed. Returns DataFrame with statistical test results per population.
    """
    populations = df["population"].unique()
    results = []

    for pop in populations:
        pop_data = df[df["population"] == pop]
        responders = pop_data[pop_data["response"] == "yes"]["percentage"]
        non_responders = pop_data[pop_data["response"] == "no"]["percentage"]

        stat, pvalue = stats.mannwhitneyu(
            responders, non_responders, alternative="two-sided"
        )

        results.append(
            {
                "population": pop,
                "responder_median": responders.median(),
                "non_responder_median": non_responders.median(),
                "u_statistic": stat,
                "p_value": pvalue,
                "significant": pvalue < 0.05,
            }
        )

    return pd.DataFrame(results)
