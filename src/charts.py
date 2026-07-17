from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.metrics import monthly_summary


def output_trend_chart(
    dataframe: pd.DataFrame,
) -> go.Figure:
    summary = monthly_summary(
        dataframe
    )

    chart_data = summary.melt(
        id_vars="month",
        value_vars=[
            "planned_output",
            "actual_output",
        ],
        var_name="Metric",
        value_name="Output",
    )

    return px.line(
        chart_data,
        x="month",
        y="Output",
        color="Metric",
        markers=True,
        title="Monthly Planned vs Actual Output",
    )


def plan_attainment_chart(
    dataframe: pd.DataFrame,
) -> go.Figure:
    summary = monthly_summary(
        dataframe
    )

    return px.line(
        summary,
        x="month",
        y="plan_attainment",
        markers=True,
        title="Monthly Plan Attainment",
        labels={
            "plan_attainment": (
                "Plan Attainment"
            ),
            "month": "Month",
        },
    )


def line_performance_chart(
    dataframe: pd.DataFrame,
) -> go.Figure:
    chart_data = (
        dataframe
        .groupby(
            ["line_name"],
            as_index=False,
        )
        .agg(
            planned_output=(
                "planned_output",
                "sum",
            ),
            actual_output=(
                "actual_output",
                "sum",
            ),
        )
        .melt(
            id_vars="line_name",
            value_vars=[
                "planned_output",
                "actual_output",
            ],
            var_name="Metric",
            value_name="Output",
        )
    )

    return px.bar(
        chart_data,
        x="line_name",
        y="Output",
        color="Metric",
        barmode="group",
        title="Output by Production Line",
    )


def defect_by_line_chart(
    dataframe: pd.DataFrame,
) -> go.Figure:
    grouped = (
        dataframe
        .groupby(
            "line_name",
            as_index=False,
        )
        .agg(
            defect_units=(
                "defect_units",
                "sum",
            ),
            actual_output=(
                "actual_output",
                "sum",
            ),
        )
    )

    grouped["defect_rate"] = (
        grouped["defect_units"]
        / grouped["actual_output"]
    )

    return px.bar(
        grouped,
        x="line_name",
        y="defect_rate",
        title="Defect Rate by Production Line",
        labels={
            "line_name": "Production Line",
            "defect_rate": "Defect Rate",
        },
    )


def workforce_chart(
    dataframe: pd.DataFrame,
) -> go.Figure:
    work = dataframe.copy()
    work["month"] = (
        work["operation_date"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    summary = (
        work
        .groupby(
            "month",
            as_index=False,
        )
        .agg(
            planned_headcount=(
                "planned_headcount",
                "sum",
            ),
            absent_employees=(
                "absent_employees",
                "sum",
            ),
            overtime_hours=(
                "overtime_hours",
                "sum",
            ),
        )
    )

    return px.line(
        summary,
        x="month",
        y=[
            "absent_employees",
            "overtime_hours",
        ],
        markers=True,
        title="Monthly Absence and Overtime Trend",
    )
