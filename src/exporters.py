from __future__ import annotations

from io import BytesIO

import pandas as pd

from src.metrics import (
    calculate_kpis,
    monthly_summary,
)


def dataframe_to_excel_bytes(
    dataframe: pd.DataFrame,
    sheet_name: str,
) -> bytes:
    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl",
    ) as writer:
        dataframe.to_excel(
            writer,
            index=False,
            sheet_name=sheet_name,
        )

    return output.getvalue()


def report_to_excel_bytes(
    dataframe: pd.DataFrame,
) -> bytes:
    output = BytesIO()
    kpis = calculate_kpis(
        dataframe
    )
    monthly = monthly_summary(
        dataframe
    )

    kpi_table = pd.DataFrame(
        {
            "KPI": [
                "Planned Output",
                "Actual Output",
                "Production Gap",
                "Plan Attainment",
                "Defect Rate",
                "Availability",
                "Output per Employee",
                "Overtime Rate",
                "Absence Rate",
            ],
            "Value": [
                kpis["planned_output"],
                kpis["actual_output"],
                kpis["production_gap"],
                kpis["plan_attainment"],
                kpis["defect_rate"],
                kpis["availability"],
                kpis[
                    "output_per_employee"
                ],
                kpis["overtime_rate"],
                kpis["absence_rate"],
            ],
        }
    )

    line_summary = (
        dataframe
        .groupby(
            [
                "line_id",
                "line_name",
                "process",
            ],
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
            defect_units=(
                "defect_units",
                "sum",
            ),
            downtime_minutes=(
                "downtime_minutes",
                "sum",
            ),
            overtime_hours=(
                "overtime_hours",
                "sum",
            ),
            absent_employees=(
                "absent_employees",
                "sum",
            ),
        )
    )

    with pd.ExcelWriter(
        output,
        engine="openpyxl",
    ) as writer:
        kpi_table.to_excel(
            writer,
            index=False,
            sheet_name="Executive Summary",
        )
        monthly.to_excel(
            writer,
            index=False,
            sheet_name="Monthly KPI",
        )
        line_summary.to_excel(
            writer,
            index=False,
            sheet_name="Line Performance",
        )
        dataframe.to_excel(
            writer,
            index=False,
            sheet_name="Filtered Data",
        )

    return output.getvalue()
