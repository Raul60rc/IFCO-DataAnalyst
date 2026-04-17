"""Plotly figure builders — no aggregation, no Streamlit calls."""
import plotly.graph_objects as go
import pandas as pd

# Force black text, white background, no Streamlit template override
_BLACK = "#000000"
_WHITE = "#ffffff"
_GRID = "#cccccc"

_LAYOUT_DEFAULTS = dict(
    paper_bgcolor=_WHITE,
    plot_bgcolor=_WHITE,
    template="none",
    font=dict(color=_BLACK, size=13),
    title_font=dict(color=_BLACK, size=16),
    legend_font=dict(color=_BLACK),
)

_AXIS_DEFAULTS = dict(
    title_font=dict(color=_BLACK),
    tickfont=dict(color=_BLACK),
    gridcolor=_GRID,
)


def _threshold_color(ratio: float, threshold: float) -> str:
    if ratio >= threshold:
        return "#2d6a4f"
    elif ratio >= threshold * 0.7:
        return "#e9c46a"
    else:
        return "#e63946"


def build_donut_chart(crate_dist: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        go.Pie(
            labels=crate_dist["crate_type"],
            values=crate_dist["count"],
            hole=0.5,
            textinfo="label+value+percent",
            textfont=dict(color="#ffffff", size=14),
            marker=dict(colors=["#2d6a4f", "#e9c46a", "#264653"]),
        )
    )
    fig.update_layout(
        title="Distribution of Orders by Crate Type",
        showlegend=True,
        height=450,
        **_LAYOUT_DEFAULTS,
    )
    return fig


def build_training_bar_chart(
    owner_ratios: pd.DataFrame, threshold: float, crate_label: str
) -> go.Figure:
    sorted_df = owner_ratios.sort_values("ratio", ascending=True)
    colors = [_threshold_color(r, threshold) for r in sorted_df["ratio"]]

    fig = go.Figure(
        go.Bar(
            x=sorted_df["ratio"],
            y=sorted_df["sales_owner"],
            orientation="h",
            marker_color=colors,
            text=sorted_df["ratio"].round(1).astype(str) + "%",
            textposition="outside",
            textfont=dict(color=_BLACK),
        )
    )
    fig.add_vline(
        x=threshold, line_dash="dash", line_color=_BLACK,
        annotation_text=f"Threshold ({threshold:.0f}%)",
        annotation_position="top",
        annotation_font=dict(color=_BLACK),
    )
    fig.update_layout(
        title=f"Sales Owners — {crate_label} Ratio (Last 12 Months)",
        xaxis=dict(title=f"{crate_label} Ratio (%)", range=[0, 100], **_AXIS_DEFAULTS),
        yaxis=dict(title="", **_AXIS_DEFAULTS),
        height=max(400, len(sorted_df) * 35),
        margin=dict(l=200),
        **_LAYOUT_DEFAULTS,
    )
    return fig


def build_top_performers_chart(
    owner_counts: pd.DataFrame, crate_label: str
) -> go.Figure:
    sorted_df = owner_counts.sort_values("order_count", ascending=True)
    fig = go.Figure(
        go.Bar(
            x=sorted_df["order_count"],
            y=sorted_df["sales_owner"],
            orientation="h",
            marker_color="#2d6a4f",
            text=sorted_df["order_count"].astype(str),
            textposition="outside",
            textfont=dict(color=_BLACK),
        )
    )
    fig.update_layout(
        title=f"Top Performers — {crate_label} Orders (Total)",
        xaxis=dict(title="Number of Orders", **_AXIS_DEFAULTS),
        yaxis=dict(title="", **_AXIS_DEFAULTS),
        height=max(400, len(sorted_df) * 35),
        margin=dict(l=200),
        **_LAYOUT_DEFAULTS,
    )
    return fig


def build_bump_chart(
    rank_df: pd.DataFrame, crate_label: str, window: int
) -> go.Figure:
    fig = go.Figure()

    if rank_df.empty:
        fig.update_layout(title="Rank Chart", **_LAYOUT_DEFAULTS)
        return fig

    owners = sorted(rank_df["sales_owner"].unique())
    all_months = sorted(rank_df["month"].unique())
    max_rank = int(rank_df["rank"].max())

    color_palette = [
        "#2d6a4f", "#e76f51", "#264653", "#e9c46a", "#a8dadc",
        "#457b9d", "#f4a261", "#6a4c93", "#1982c4", "#8ac926",
        "#d62828", "#003049", "#fcbf49", "#606c38", "#283618",
    ]

    for i, owner in enumerate(owners):
        owner_data = rank_df[rank_df["sales_owner"] == owner].sort_values("month")
        color = color_palette[i % len(color_palette)]

        x_vals, y_vals, texts = [], [], []
        for m in all_months:
            row = owner_data[owner_data["month"] == m]
            if len(row) > 0:
                x_vals.append(m)
                y_vals.append(row["rank"].values[0])
                texts.append(
                    f"<b>{owner}</b><br>"
                    f"Month: {m.strftime('%b %Y')}<br>"
                    f"Rank: {int(row['rank'].values[0])}<br>"
                    f"Rolling {window}m orders: {int(row['rolling_count'].values[0])}"
                )
            else:
                x_vals.append(m)
                y_vals.append(None)
                texts.append("")

        fig.add_trace(
            go.Scatter(
                x=x_vals, y=y_vals,
                mode="lines+markers",
                name=owner,
                line=dict(color=color, width=3),
                marker=dict(size=9),
                connectgaps=False,
                hovertext=texts,
                hoverinfo="text",
            )
        )

    fig.update_layout(
        title=f"Rank Over Time — {crate_label} Sales (Rolling {window}-Month Window)",
        xaxis=dict(title="Month", tickformat="%b %Y", **_AXIS_DEFAULTS),
        yaxis=dict(
            title="Rank",
            range=[max_rank + 0.5, 0.5],
            tickvals=list(range(1, max_rank + 1)),
            ticktext=[f"{r}" for r in range(1, max_rank + 1)],
            dtick=1,
            **_AXIS_DEFAULTS,
        ),
        height=520,
        hovermode="closest",
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.25,
            xanchor="center", x=0.5,
            font=dict(color=_BLACK),
        ),
        annotations=[
            dict(
                text="Rank 1 = most orders in the rolling window",
                xref="paper", yref="paper",
                x=0.5, y=1.06, showarrow=False,
                font=dict(size=11, color=_BLACK),
            )
        ],
        **_LAYOUT_DEFAULTS,
    )
    return fig
