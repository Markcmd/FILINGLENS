"""Download 10-K filings from SEC EDGAR into data/raw/.

EDGAR flow (no API key needed, just a descriptive User-Agent):
1. https://data.sec.gov/submissions/CIK{cik}.json lists all of a company's
   filings as parallel arrays (form, accessionNumber, filingDate, ...).
2. Filter to form == "10-K", keep the latest N.
3. The filing's primary document lives at
   https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{primaryDocument}

Run: python -m filinglens.ingest
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import requests

from filinglens.config import COMPANIES, EDGAR_USER_AGENT, RAW_DIR

SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
ARCHIVES_URL = "https://www.sec.gov/Archives/edgar/data/{cik_short}/{accession}/{doc}"

# SEC fair-use limit is 10 requests/second; stay well under it.
REQUEST_DELAY_S = 0.2


@dataclass(frozen=True)
class Filing:
    """One 10-K filing: everything needed to download it and cite it later."""

    ticker: str
    cik: str  # zero-padded 10-digit CIK
    form: str
    accession: str  # accession number without dashes, e.g. "000032019324000123"
    filing_date: str  # YYYY-MM-DD the SEC received it
    report_date: str  # YYYY-MM-DD fiscal period end
    primary_doc: str  # filename of the main 10-K HTML document

    @property
    def fiscal_year(self) -> str:
        """Fiscal year of the report, e.g. '2024' (from the period-end date)."""
        return self.report_date[:4]

    @property
    def url(self) -> str:
        return ARCHIVES_URL.format(
            cik_short=int(self.cik),  # archives path uses the un-padded CIK
            accession=self.accession,
            doc=self.primary_doc,
        )

    @property
    def html_path(self) -> Path:
        return RAW_DIR / self.ticker / f"{self.fiscal_year}_{self.form}.htm"

    @property
    def meta_path(self) -> Path:
        return RAW_DIR / self.ticker / f"{self.fiscal_year}_{self.form}.meta.json"


def make_session() -> requests.Session:
    session = requests.Session()
    session.headers["User-Agent"] = EDGAR_USER_AGENT
    return session


def fetch_submissions(session: requests.Session, ticker: str) -> dict:
    """Fetch the full submissions index for a company."""
    cik = COMPANIES[ticker]
    resp = session.get(SUBMISSIONS_URL.format(cik=cik), timeout=30)
    resp.raise_for_status()
    return resp.json()


def select_10ks(ticker: str, submissions: dict, n: int = 3) -> list[Filing]:
    """Pick the latest n 10-K filings from a submissions index.

    Pure function (no I/O) so it's easy to unit test. The submissions JSON
    stores filings as parallel arrays under filings.recent.
    """
    recent = submissions["filings"]["recent"]
    filings = []
    for i, form in enumerate(recent["form"]):
        if form != "10-K":
            continue
        filings.append(
            Filing(
                ticker=ticker,
                cik=COMPANIES[ticker],
                form=form,
                accession=recent["accessionNumber"][i].replace("-", ""),
                filing_date=recent["filingDate"][i],
                report_date=recent["reportDate"][i],
                primary_doc=recent["primaryDocument"][i],
            )
        )
    filings.sort(key=lambda f: f.filing_date, reverse=True)
    return filings[:n]


def download_filing(session: requests.Session, filing: Filing) -> Path:
    """Download a filing's primary document; skip if already cached."""
    if filing.html_path.exists():
        return filing.html_path

    resp = session.get(filing.url, timeout=60)
    resp.raise_for_status()

    filing.html_path.parent.mkdir(parents=True, exist_ok=True)
    filing.html_path.write_bytes(resp.content)
    # Sidecar metadata: this is what lets answers cite the exact filing.
    filing.meta_path.write_text(
        json.dumps({**asdict(filing), "url": filing.url}, indent=2)
    )
    return filing.html_path


def ingest_all(n: int = 3) -> list[Path]:
    """Download the latest n 10-Ks for every company in scope."""
    session = make_session()
    paths = []
    for ticker in COMPANIES:
        submissions = fetch_submissions(session, ticker)
        time.sleep(REQUEST_DELAY_S)
        for filing in select_10ks(ticker, submissions, n=n):
            path = download_filing(session, filing)
            paths.append(path)
            print(f"{filing.ticker} {filing.form} FY{filing.fiscal_year}: {path}")
            time.sleep(REQUEST_DELAY_S)
    return paths


if __name__ == "__main__":
    ingest_all()
