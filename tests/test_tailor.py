from jobtool.tailor import extract_keywords, score_match


def test_extract_keywords_gets_data_terms():
    kws = extract_keywords("We need a Data Analyst with Python, SQL, Excel, dashboards, and Tableau.")
    assert "python" in kws
    assert "sql" in kws
    assert "excel" in kws


def test_score_match():
    matched, missing, score = score_match("Python and Excel projects", ["python", "sql", "excel"])
    assert matched == ["python", "excel"]
    assert missing == ["sql"]
    assert score == 67
