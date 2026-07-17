import pandas as pd

from src.validators import clean_and_validate


def valid_row() -> dict:
    return {
        "operation_date": "2025-01-01",
        "line_id": "L-A",
        "line_name": "Assembly Line A",
        "process": "Assembly",
        "shift": "Day",
        "planned_output": 1000,
        "actual_output": 900,
        "defect_units": 10,
        "downtime_minutes": 20,
        "scheduled_minutes": 480,
        "planned_headcount": 100,
        "present_headcount": 95,
        "absent_employees": 5,
        "overtime_hours": 10,
        "regular_hours": 760,
        "total_labor_hours": 770,
        "remarks": "Normal",
    }


def test_valid_data_is_retained():
    source = pd.DataFrame(
        [valid_row()]
    )

    cleaned, invalid, report = (
        clean_and_validate(source)
    )

    assert len(cleaned) == 1
    assert invalid.empty
    assert report["clean_rows"] == 1


def test_duplicates_and_logical_errors():
    first = valid_row()
    invalid_row = valid_row()
    invalid_row["present_headcount"] = 150

    source = pd.DataFrame(
        [
            first,
            dict(first),
            invalid_row,
        ]
    )

    cleaned, invalid, report = (
        clean_and_validate(source)
    )

    assert len(cleaned) == 1
    assert len(invalid) == 1
    assert report[
        "duplicate_rows_removed"
    ] == 1
    assert report[
        "logical_error_rows"
    ] == 1
