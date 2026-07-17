REQUIRED_COLUMNS = [
    "operation_date",
    "line_id",
    "line_name",
    "process",
    "shift",
    "planned_output",
    "actual_output",
    "defect_units",
    "downtime_minutes",
    "scheduled_minutes",
    "planned_headcount",
    "present_headcount",
    "absent_employees",
    "overtime_hours",
    "regular_hours",
    "total_labor_hours",
]

NUMERIC_COLUMNS = [
    "planned_output",
    "actual_output",
    "defect_units",
    "downtime_minutes",
    "scheduled_minutes",
    "planned_headcount",
    "present_headcount",
    "absent_employees",
    "overtime_hours",
    "regular_hours",
    "total_labor_hours",
]

KPI_TARGETS = {
    "plan_attainment": {
        "label": "Plan Attainment",
        "target": 0.95,
        "direction": ">=",
    },
    "defect_rate": {
        "label": "Defect Rate",
        "target": 0.02,
        "direction": "<=",
    },
    "availability": {
        "label": "Availability",
        "target": 0.90,
        "direction": ">=",
    },
    "output_per_employee": {
        "label": "Output per Employee",
        "target": 65.0,
        "direction": ">=",
    },
    "overtime_rate": {
        "label": "Overtime Rate",
        "target": 0.08,
        "direction": "<=",
    },
    "absence_rate": {
        "label": "Absence Rate",
        "target": 0.04,
        "direction": "<=",
    },
}
