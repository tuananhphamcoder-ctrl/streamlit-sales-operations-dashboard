from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

import pandas as pd


def load_uploaded_dataframe(
    uploaded_file: BinaryIO,
) -> pd.DataFrame:
    filename = getattr(
        uploaded_file,
        "name",
        "",
    )
    suffix = Path(filename).suffix.lower()

    if suffix == ".csv":
        try:
            return pd.read_csv(uploaded_file)
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            return pd.read_csv(
                uploaded_file,
                encoding="latin-1",
            )

    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(
            uploaded_file,
            sheet_name=0,
        )

    raise ValueError(
        "Unsupported file type. "
        "Upload CSV, XLSX, or XLS."
    )
