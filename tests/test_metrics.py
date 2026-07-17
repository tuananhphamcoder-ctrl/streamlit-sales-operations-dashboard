import pandas as pd
import pytest

from src.metrics import calculate_kpis


def test_calculate_kpis():
    source = pd.DataFrame(
        {
            "planned_output": [100, 100],
            "actual_output": [90, 95],
            "defect_units": [2, 1],
            "downtime_minutes": [20, 10],
            "scheduled_minutes": [480, 480],
            "planned_headcount": [10, 10],
            "present_headcount": [9, 10],
            "absent_employees": [1, 0],
            "overtime_hours": [4, 2],
            "total_labor_hours": [76, 82],
        }
    )

    result = calculate_kpis(
        source
    )

    assert result[
        "plan_attainment"
    ] == pytest.approx(185 / 200)

    assert result[
        "defect_rate"
    ] == pytest.approx(3 / 185)

    assert result[
        "absence_rate"
    ] == pytest.approx(1 / 20)
