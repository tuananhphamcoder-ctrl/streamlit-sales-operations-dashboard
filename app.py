from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.charts import (
    defect_by_line_chart,
    line_performance_chart,
    output_trend_chart,
    plan_attainment_chart,
    workforce_chart,
)
from src.config import KPI_TARGETS
from src.data_loader import (
    load_uploaded_dataframe,
)
from src.exporters import (
    dataframe_to_excel_bytes,
    report_to_excel_bytes,
)
from src.metrics import calculate_kpis
from src.validators import (
    clean_and_validate,
)


st.set_page_config(
    page_title=(
        "Sales & Operations Dashboard"
    ),
    page_icon="🏭",
    layout="wide",
)


def status_label(
    value: float,
    target: float,
    direction: str,
) -> str:
    if direction == ">=":
        return (
            "On target"
            if value >= target
            else "Needs attention"
        )

    return (
        "On target"
        if value <= target
        else "Needs attention"
    )


def render_kpi_cards(
    dataframe: pd.DataFrame,
) -> None:
    kpis = calculate_kpis(
        dataframe
    )

    first_row = st.columns(3)
    second_row = st.columns(3)

    card_definitions = [
        (
            first_row[0],
            "Plan Attainment",
            kpis["plan_attainment"],
            "plan_attainment",
            "{:.1%}",
        ),
        (
            first_row[1],
            "Defect Rate",
            kpis["defect_rate"],
            "defect_rate",
            "{:.2%}",
        ),
        (
            first_row[2],
            "Availability",
            kpis["availability"],
            "availability",
            "{:.1%}",
        ),
        (
            second_row[0],
            "Output per Employee",
            kpis[
                "output_per_employee"
            ],
            "output_per_employee",
            "{:,.1f}",
        ),
        (
            second_row[1],
            "Overtime Rate",
            kpis["overtime_rate"],
            "overtime_rate",
            "{:.2%}",
        ),
        (
            second_row[2],
            "Absence Rate",
            kpis["absence_rate"],
            "absence_rate",
            "{:.2%}",
        ),
    ]

    for (
        column,
        label,
        value,
        target_key,
        format_string,
    ) in card_definitions:
        target_config = KPI_TARGETS[
            target_key
        ]

        status = status_label(
            value=value,
            target=target_config["target"],
            direction=target_config[
                "direction"
            ],
        )

        column.metric(
            label=label,
            value=format_string.format(
                value
            ),
            delta=status,
            delta_color=(
                "normal"
                if status == "On target"
                else "inverse"
            ),
        )


st.title(
    "Factory Sales & Operations Dashboard"
)
st.caption(
    "Upload CSV or Excel operations data, "
    "validate data quality, analyze production "
    "and workforce KPIs, and download results."
)

with st.sidebar:
    st.header("1. Choose data")

    source = st.radio(
        "Data source",
        [
            "Use clean sample data",
            "Use messy sample data",
            "Upload my file",
        ],
    )

    uploaded_file = None

    if source == "Upload my file":
        uploaded_file = st.file_uploader(
            "Upload CSV or Excel",
            type=[
                "csv",
                "xlsx",
                "xls",
            ],
        )

    st.header("2. Dashboard filters")

try:
    if source == "Use clean sample data":
        raw_dataframe = pd.read_csv(
            "data/sample_factory_operations.csv"
        )
        source_name = (
            "sample_factory_operations.csv"
        )

    elif source == "Use messy sample data":
        raw_dataframe = pd.read_csv(
            "data/messy_factory_operations.csv"
        )
        source_name = (
            "messy_factory_operations.csv"
        )

    elif uploaded_file is not None:
        raw_dataframe = (
            load_uploaded_dataframe(
                uploaded_file
            )
        )
        source_name = uploaded_file.name

    else:
        st.info(
            "Upload a CSV or Excel file "
            "to begin."
        )
        st.stop()

except Exception as error:
    st.error(
        f"Could not read the selected file: {error}"
    )
    st.stop()

st.success(
    f"Loaded **{source_name}** — "
    f"{len(raw_dataframe):,} rows × "
    f"{len(raw_dataframe.columns):,} columns"
)

with st.expander(
    "Preview original data",
    expanded=False,
):
    st.dataframe(
        raw_dataframe.head(100),
        use_container_width=True,
    )

(
    cleaned_dataframe,
    invalid_records,
    quality_report,
) = clean_and_validate(
    raw_dataframe
)

if quality_report[
    "missing_required_columns"
]:
    missing = ", ".join(
        quality_report[
            "missing_required_columns"
        ]
    )

    st.error(
        "The file is missing required columns: "
        f"**{missing}**"
    )
    st.stop()

tab_quality, tab_dashboard, tab_data = (
    st.tabs(
        [
            "Data quality",
            "Operations dashboard",
            "Cleaned data",
        ]
    )
)

with tab_quality:
    st.subheader(
        "Data-quality summary"
    )

    columns = st.columns(6)

    columns[0].metric(
        "Original rows",
        f"{quality_report['original_rows']:,}",
    )
    columns[1].metric(
        "Duplicates removed",
        f"{quality_report['duplicate_rows_removed']:,}",
    )
    columns[2].metric(
        "Invalid dates",
        f"{quality_report['invalid_date_rows']:,}",
    )
    columns[3].metric(
        "Invalid numeric rows",
        f"{quality_report['invalid_numeric_rows']:,}",
    )
    columns[4].metric(
        "Logical errors",
        f"{quality_report['logical_error_rows']:,}",
    )
    columns[5].metric(
        "Clean rows",
        f"{quality_report['clean_rows']:,}",
    )

    if invalid_records.empty:
        st.success(
            "No invalid records were found."
        )
    else:
        st.warning(
            f"{len(invalid_records):,} records "
            "require review."
        )

        st.dataframe(
            invalid_records,
            use_container_width=True,
            height=420,
        )

        st.download_button(
            "Download invalid records CSV",
            data=invalid_records.to_csv(
                index=False
            ).encode("utf-8-sig"),
            file_name=(
                "invalid_operations_records.csv"
            ),
            mime="text/csv",
        )

with tab_dashboard:
    if cleaned_dataframe.empty:
        st.warning(
            "No valid rows remain after cleaning."
        )
        st.stop()

    minimum_date = (
        cleaned_dataframe[
            "operation_date"
        ]
        .min()
        .date()
    )
    maximum_date = (
        cleaned_dataframe[
            "operation_date"
        ]
        .max()
        .date()
    )

    date_range = st.sidebar.date_input(
        "Operation date",
        value=(
            minimum_date,
            maximum_date,
        ),
        min_value=minimum_date,
        max_value=maximum_date,
    )

    line_names = sorted(
        cleaned_dataframe[
            "line_name"
        ]
        .dropna()
        .unique()
        .tolist()
    )
    shifts = sorted(
        cleaned_dataframe[
            "shift"
        ]
        .dropna()
        .unique()
        .tolist()
    )
    processes = sorted(
        cleaned_dataframe[
            "process"
        ]
        .dropna()
        .unique()
        .tolist()
    )

    selected_lines = (
        st.sidebar.multiselect(
            "Production line",
            line_names,
            default=line_names,
        )
    )
    selected_shifts = (
        st.sidebar.multiselect(
            "Shift",
            shifts,
            default=shifts,
        )
    )
    selected_processes = (
        st.sidebar.multiselect(
            "Process",
            processes,
            default=processes,
        )
    )

    filtered = cleaned_dataframe.copy()

    if (
        isinstance(date_range, tuple)
        and len(date_range) == 2
    ):
        start_date, end_date = (
            date_range
        )

        filtered = filtered[
            filtered[
                "operation_date"
            ]
            .dt.date
            .between(
                start_date,
                end_date,
            )
        ]

    filtered = filtered[
        filtered["line_name"].isin(
            selected_lines
        )
        & filtered["shift"].isin(
            selected_shifts
        )
        & filtered["process"].isin(
            selected_processes
        )
    ]

    if filtered.empty:
        st.warning(
            "No records match the selected filters."
        )
    else:
        render_kpi_cards(
            filtered
        )

        kpis = calculate_kpis(
            filtered
        )

        detail_columns = st.columns(3)
        detail_columns[0].metric(
            "Planned Output",
            f"{kpis['planned_output']:,.0f}",
        )
        detail_columns[1].metric(
            "Actual Output",
            f"{kpis['actual_output']:,.0f}",
        )
        detail_columns[2].metric(
            "Production Gap",
            f"{kpis['production_gap']:,.0f}",
        )

        chart_1, chart_2 = st.columns(2)

        with chart_1:
            st.plotly_chart(
                output_trend_chart(
                    filtered
                ),
                use_container_width=True,
            )

        with chart_2:
            st.plotly_chart(
                plan_attainment_chart(
                    filtered
                ),
                use_container_width=True,
            )

        chart_3, chart_4 = st.columns(2)

        with chart_3:
            st.plotly_chart(
                line_performance_chart(
                    filtered
                ),
                use_container_width=True,
            )

        with chart_4:
            st.plotly_chart(
                defect_by_line_chart(
                    filtered
                ),
                use_container_width=True,
            )

        st.plotly_chart(
            workforce_chart(
                filtered
            ),
            use_container_width=True,
        )

        download_1, download_2 = (
            st.columns(2)
        )

        download_1.download_button(
            "Download filtered data",
            data=(
                dataframe_to_excel_bytes(
                    filtered,
                    "Filtered Data",
                )
            ),
            file_name=(
                "filtered_operations_data.xlsx"
            ),
            mime=(
                "application/vnd."
                "openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            use_container_width=True,
        )

        download_2.download_button(
            "Download KPI report",
            data=report_to_excel_bytes(
                filtered
            ),
            file_name=(
                "operations_kpi_report.xlsx"
            ),
            mime=(
                "application/vnd."
                "openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            use_container_width=True,
        )

with tab_data:
    st.subheader(
        "Cleaned and validated data"
    )

    st.dataframe(
        cleaned_dataframe,
        use_container_width=True,
        height=520,
    )

    csv_column, excel_column = (
        st.columns(2)
    )

    csv_column.download_button(
        "Download cleaned CSV",
        data=cleaned_dataframe.to_csv(
            index=False
        ).encode("utf-8-sig"),
        file_name=(
            "cleaned_operations_data.csv"
        ),
        mime="text/csv",
        use_container_width=True,
    )

    excel_column.download_button(
        "Download cleaned Excel",
        data=dataframe_to_excel_bytes(
            cleaned_dataframe,
            "Cleaned Data",
        ),
        file_name=(
            "cleaned_operations_data.xlsx"
        ),
        mime=(
            "application/vnd."
            "openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        use_container_width=True,
    )
