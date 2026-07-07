"""Smoke tests: package imports and config constants are sane."""

from filinglens import __version__
from filinglens.config import COMPANIES, EDGAR_USER_AGENT, RAW_DIR, ROOT_DIR


def test_version():
    assert __version__ == "0.1.0"


def test_companies_have_valid_ciks():
    assert set(COMPANIES) == {"AAPL", "MSFT", "NVDA"}
    for cik in COMPANIES.values():
        assert len(cik) == 10 and cik.isdigit()


def test_edgar_user_agent_has_contact():
    # SEC requires a contact address in the User-Agent
    assert "@" in EDGAR_USER_AGENT


def test_raw_dir_is_inside_repo():
    assert ROOT_DIR in RAW_DIR.parents
