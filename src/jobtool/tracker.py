from __future__ import annotations

from pathlib import Path

import pandas as pd

COLUMNS = [
    "timestamp", "company", "role", "job_link", "match_score", "matched_keywords", "missing_keywords",
    "resume_path", "cover_letter_path", "status",
]


def append_application(path: Path, row: dict) -> None:
    if path.exists():
        df = pd.read_excel(path)
    else:
        df = pd.DataFrame(columns=COLUMNS)
    df = pd.concat([df, pd.DataFrame([{col: row.get(col, "") for col in COLUMNS}])], ignore_index=True)
    df.to_excel(path, index=False)
