import plotly.express as px


def boxplot_by_response(df, title="Cell Population Frequencies by Response"):
    """Create boxplot comparing population frequencies between responders and non-responders."""
    fig = px.box(
        df,
        x="population",
        y="percentage",
        color="response",
        title=title,
        labels={
            "percentage": "Relative Frequency (%)",
            "population": "Cell Population",
            "response": "Response",
        },
    )
    fig.update_layout(boxmode="group")
    return fig
