from jobtool.tracker import append_application
import pandas as pd


def test_append_application(tmp_path):
    p = tmp_path / "apps.xlsx"
    append_application(p, {"company": "Acme", "role": "Analyst"})
    append_application(p, {"company": "Beta", "role": "Intern"})
    df = pd.read_excel(p)
    assert len(df) == 2
    assert list(df["company"]) == ["Acme", "Beta"]
