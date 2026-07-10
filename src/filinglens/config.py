"""Project-wide constants and paths."""

from pathlib import Path

# Repo root (two levels up from this file: src/filinglens/config.py)
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"  # downloaded filings, as fetched from EDGAR
PARSED_DIR = DATA_DIR / "parsed"  # canonical text + section map per filing
CHUNKS_DIR = DATA_DIR / "chunks"  # citation-ready chunks (JSONL per filing)

# SEC = U.S. Securities and Exchange Commission, the agency that stores public company filings.
# CIK = Central Index Key, the SEC's unique identifier for a filing entity/company.
# Companies in scope for Phase 1: stock ticker -> SEC CIK (zero-padded to 10 digits)
COMPANIES: dict[str, str] = {
    "AAPL": "0000320193",
    "MSFT": "0000789019",
    "NVDA": "0001045810",
}

# SEC EDGAR requires a descriptive User-Agent identifying the requester.
# https://www.sec.gov/os/accessing-edgar-data
EDGAR_USER_AGENT = "FilingLens research project (lovekinball311@gmail.com)"
