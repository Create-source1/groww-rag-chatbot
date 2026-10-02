"""Fetch the 5 official HDFC scheme pages from Groww and save them as markdown in documents/."""
import re
import requests
from bs4 import BeautifulSoup

PAGES = {
    "hdfc_large_cap_fund.md": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    "hdfc_equity_flexi_cap_fund.md": "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
    "hdfc_elss_tax_saver_fund.md": "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
    "hdfc_small_cap_fund.md": "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    "hdfc_balanced_advantage_fund.md": "https://groww.in/mutual-funds/hdfc-balanced-advantage-fund-direct-growth",
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# Sections of the page we care about for FAQ answering
KEY_PATTERNS = re.compile(
    r"expense ratio|exit load|minimum|sip|lumpsum|riskometer|benchmark|risk|launched|aum|nav|"
    r"fund manager|objective|category|tax|stamp duty|lock.?in|statement|benchmark|category",
    re.IGNORECASE,
)


def extract_text(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Grab the main content area
    main = soup.find("main") or soup.body
    lines = []
    for el in main.find_all(["h1", "h2", "h3", "h4", "p", "li", "td", "th", "span", "div"]):
        text = el.get_text(" ", strip=True)
        if text and len(text) < 200:
            lines.append(text)
    # Deduplicate while preserving order
    seen, unique = set(), []
    for line in lines:
        if line not in seen:
            seen.add(line)
            unique.append(line)
    text = "\n".join(unique)

    # Trim leading nav junk: keep from the fund <h1> (e.g. "HDFC Large Cap Fund Direct Growth")
    m = re.search(r"^HDFC .*Direct.*$", text, re.MULTILINE)
    if m:
        text = text[m.start():]

    # Trim footer/noise after the main content
    for end_marker in ["© 2016", "\nGROWW\n", "Home\n>", "Home >"]:
        idx = text.find(end_marker)
        if idx != -1:
            text = text[:idx]
            break

    return text


def main():
    import os
    os.makedirs("documents", exist_ok=True)
    for filename, url in PAGES.items():
        print(f"Fetching {url} ...")
        text = extract_text(url)
        # URL is intentionally not embedded in the text (it pollutes retrieval);
        # it stays as the file's source metadata instead.
        with open(f"documents/{filename}", "w", encoding="utf-8") as f:
            f.write(text)
        print(f"  saved documents/{filename} ({len(text)} chars)")


if __name__ == "__main__":
    main()
