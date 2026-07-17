from __future__ import annotations

import re

import pandas as pd

from src.config import (
    NUMERIC_COLUMNS,
    REQUIRED_COLUMNS,
)


def normalize_column_name(
    column: object,
) -> str:
    text = str(column).strip().lower()
    text = re.sub(
        r"[^a-z0-9]+",
        "_",
        text,
    )
    return text.strip("_")


def normalize_columns(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    result = dataframe.copy()
    result.columns = [
        normalize_column_name(column)
        for column in result.columns
    ]
    return result


def clean_and_validate(
    dataframe: pd.DataFrame,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    dict,
]:
    original = normalize_columns(
        dataframe
    )

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in original.columns
    ]

    report = {
        "original_rows": len(original),
        "missing_required_columns": missing_columns,
        "empty_rows_removed": 0,
        "duplicate_rows_removed": 0,
        "invalid_date_rows": 0,
        "invalid_numeric_rows": 0,
        "logical_error_rows": 0,
        "invalid_rows": 0,
        "clean_rows": 0,
    }

    if missing_columns:
        return original, pd.DataFrame(), report

    work = original.copy()

    before_empty = len(work)
    work = work.dropna(
        how="all"
    ).copy()
    report["empty_rows_removed"] = (
        before_empty - len(work)
    )

    duplicate_mask = work.duplicated(
        keep="first"
    )
    report["duplicate_rows_removed"] = int(
        duplicate_mask.sum()
    )
    work = work.loc[
        ~duplicate_mask
    ].copy()

    for column in [
        "line_id",
        "line_name",
        "process",
        "shift",
        "remarks",
    ]:
        if column in work.columns:
            work[column] = (
                work[column]
                .astype("string")
                .str.strip()
            )

    raw_dates = work[
        "operation_date"
    ].copy()
    work["operation_date"] = pd.to_datetime(
        work["operation_date"],
        errors="coerce",
    )
    invalid_date_mask = (
        raw_dates.notna()
        & work["operation_date"].isna()
    )
    report["invalid_date_rows"] = int(
        invalid_date_mask.sum()
    )

    invalid_numeric_mask = pd.Series(
        False,
        index=work.index,
    )

    for column in NUMERIC_COLUMNS:
        original_numeric = work[
            column
        ].copy()

        work[column] = pd.to_numeric(
            work[column],
            errors="coerce",
        )

        invalid_numeric_mask = (
            invalid_numeric_mask
            | (
                original_numeric.notna()
                & work[column].isna()
            )
        )

    report["invalid_numeric_rows"] = int(
        invalid_numeric_mask.sum()
    )

    missing_required_mask = work[
        REQUIRED_COLUMNS
    ].isna().any(axis=1)

    invalid_category_mask = (
        ~work["shift"].isin(
            ["Day", "Night"]
        )
        | ~work["process"].isin(
            [
                "Assembly",
                "Testing",
                "Packaging",
            ]
        )
    )

    logical_error_mask = (
        (work["planned_output"] <= 0)
        | (work["actual_output"] < 0)
        | (
            work["actual_output"]
            > work["planned_output"] * 1.50
        )
        | (work["defect_units"] < 0)
        | (
            work["defect_units"]
            > work["actual_output"]
        )
        | (work["downtime_minutes"] < 0)
        | (
            work["downtime_minutes"]
            > work["scheduled_minutes"]
        )
        | (work["scheduled_minutes"] <= 0)
        | (work["planned_headcount"] <= 0)
        | (work["present_headcount"] < 0)
        | (
            work["present_headcount"]
            > work["planned_headcount"]
        )
        | (work["absent_employees"] < 0)
        | (
            work["present_headcount"]
            + work["absent_employees"]
            != work["planned_headcount"]
        )
        | (work["overtime_hours"] < 0)
        | (work["regular_hours"] < 0)
        | (work["total_labor_hours"] <= 0)
        | (
            work["total_labor_hours"]
            < work["regular_hours"]
        )
        | invalid_category_mask
    ).fillna(True)

    report["logical_error_rows"] = int(
        logical_error_mask.sum()
    )

    invalid_mask = (
        invalid_date_mask
        | invalid_numeric_mask
        | missing_required_mask
        | logical_error_mask
    )

    invalid_records = work.loc[
        invalid_mask
    ].copy()

    issue_types = []
    for index in invalid_records.index:
        issues = []

        if invalid_date_mask.loc[index]:
            issues.append(
                "invalid_date"
            )
        if invalid_numeric_mask.loc[index]:
            issues.append(
                "invalid_numeric"
            )
        if missing_required_mask.loc[index]:
            issues.append(
                "missing_required_value"
            )
        if logical_error_mask.loc[index]:
            issues.append(
                "logical_error"
            )

        issue_types.append(
            "; ".join(issues)
        )

    invalid_records[
        "issue_type"
    ] = issue_types

    cleaned = work.loc[
        ~invalid_mask
    ].copy()

    cleaned = add_kpi_columns(
        cleaned
    )

    report["invalid_rows"] = len(
        invalid_records
    )
    report["clean_rows"] = len(
        cleaned
    )

    return (
        cleaned.reset_index(drop=True),
        invalid_records.reset_index(drop=True),
        report,
    )


def add_kpi_columns(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    result = dataframe.copy()

    result["plan_attainment"] = (
        result["actual_output"]
        / result["planned_output"]
    )

    result["defect_rate"] = (
        result["defect_units"]
        / result["actual_output"]
    ).fillna(0)

    result["availability"] = (
        1
        - result["downtime_minutes"]
        / result["scheduled_minutes"]
    )

    result["output_per_employee"] = (
        result["actual_output"]
        / result["present_headcount"]
    )

    result["overtime_rate"] = (
        result["overtime_hours"]
        / result["total_labor_hours"]
    )

    result["absence_rate"] = (
        result["absent_employees"]
        / result["planned_headcount"]
    )

    return result
