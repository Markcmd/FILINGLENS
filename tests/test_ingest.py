"""Unit tests for EDGAR ingest — no network, uses a fixture submissions index."""

from filinglens import ingest
from filinglens.ingest import Filing, select_10ks

# Mimics data.sec.gov/submissions/CIK....json: parallel arrays under filings.recent.
# 4 10-Ks mixed with other forms, deliberately out of order.
FAKE_SUBMISSIONS = {
    "filings": {
        "recent": {
            "form": ["10-Q", "10-K", "8-K", "10-K", "10-K", "4", "10-K"],
            "accessionNumber": [
                "0000320193-25-000001",
                "0000320193-24-000123",
                "0000320193-24-000050",
                "0000320193-22-000108",
                "0000320193-23-000106",
                "0000320193-23-000001",
                "0000320193-21-000105",
            ],
            "filingDate": [
                "2025-01-31",
                "2024-11-01",
                "2024-05-02",
                "2022-10-28",
                "2023-11-03",
                "2023-01-15",
                "2021-10-29",
            ],
            "reportDate": [
                "2024-12-28",
                "2024-09-28",
                "2024-05-01",
                "2022-09-24",
                "2023-09-30",
                "2023-01-14",
                "2021-09-25",
            ],
            "primaryDocument": [
                "aapl-q1.htm",
                "aapl-20240928.htm",
                "aapl-8k.htm",
                "aapl-20220924.htm",
                "aapl-20230930.htm",
                "form4.xml",
                "aapl-20210925.htm",
            ],
        }
    }
}


def test_select_10ks_filters_and_orders():
    filings = select_10ks("AAPL", FAKE_SUBMISSIONS, n=3)
    assert [f.form for f in filings] == ["10-K"] * 3
    # Newest first, and the 2021 10-K (4th newest) is cut off by n=3
    assert [f.fiscal_year for f in filings] == ["2024", "2023", "2022"]


def test_accession_has_no_dashes():
    filings = select_10ks("AAPL", FAKE_SUBMISSIONS, n=1)
    assert filings[0].accession == "000032019324000123"


def test_url_construction():
    filings = select_10ks("AAPL", FAKE_SUBMISSIONS, n=1)
    assert filings[0].url == (
        "https://www.sec.gov/Archives/edgar/data/320193/"
        "000032019324000123/aapl-20240928.htm"
    )


def test_paths_include_ticker_and_fiscal_year():
    f = select_10ks("AAPL", FAKE_SUBMISSIONS, n=1)[0]
    assert f.html_path.name == "2024_10-K.htm"
    assert f.html_path.parent.name == "AAPL"
    assert f.meta_path.name == "2024_10-K.meta.json"


def test_download_skips_when_cached(tmp_path, monkeypatch):
    monkeypatch.setattr(ingest, "RAW_DIR", tmp_path)
    f = Filing(
        ticker="AAPL",
        cik="0000320193",
        form="10-K",
        accession="000032019324000123",
        filing_date="2024-11-01",
        report_date="2024-09-28",
        primary_doc="aapl-20240928.htm",
    )
    f.html_path.parent.mkdir(parents=True)
    f.html_path.write_text("cached")
    # session=None: if the cache is respected, no HTTP call is ever attempted
    assert ingest.download_filing(None, f) == f.html_path
    assert f.html_path.read_text() == "cached"
