from __future__ import annotations

import pandas as pd


def calculate_kpis(
    dataframe: pd.DataFrame,
) -> dict[str, float]:
    planned_output = float(
        dataframe["planned_output"].sum()
    )
    actual_output = float(
        dataframe["actual_output"].sum()
    )
    defect_units = float(
        dataframe["defect_units"].sum()
    )
    downtime_minutes = float(
        dataframe["downtime_minutes"].sum()
    )
    scheduled_minutes = float(
        dataframe["scheduled_minutes"].sum()
    )
    present_headcount = float(
        dataframe["present_headcount"].sum()
    )
    planned_headcount = float(
        dataframe["planned_headcount"].sum()
    )
    absent_employees = float(
        dataframe["absent_employees"].sum()
    )
    overtime_hours = float(
        dataframe["overtime_hours"].sum()
    )
    total_labor_hours = float(
        dataframe["total_labor_hours"].sum()
    )

    return {
        "planned_output": planned_output,
        "actual_output": actual_output,
        "production_gap": (
            actual_output
            - planned_output
        ),
        "plan_attainment": (
            actual_output / planned_output
            if planned_output
            else 0
        ),
        "defect_rate": (
            defect_units / actual_output
            if actual_output
            else 0
        ),
        "availability": (
            1
            - downtime_minutes
            / scheduled_minutes
            if scheduled_minutes
            else 0
        ),
        "output_per_employee": (
            actual_output / present_headcount
            if present_headcount
            else 0
        ),
        "overtime_rate": (
            overtime_hours
            / total_labor_hours
            if total_labor_hours
            else 0
        ),
        "absence_rate": (
            absent_employees
            / planned_headcount
            if planned_headcount
            else 0
        ),
    }


def monthly_summary(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    work = dataframe.copy()
    work["month"] = (
        work["operation_date"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    rows = []

    for month, group in work.groupby(
        "month"
    ):
        rows.append(
            {
                "month": month,
                **calculate_kpis(group),
            }
        )

    return pd.DataFrame(rows)
