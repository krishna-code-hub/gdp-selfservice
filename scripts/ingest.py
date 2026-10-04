"""Separate whole-Markdown ingestion entry point; run after installing this project."""

import sys

from gdp_support.cli import main

if __name__ == "__main__":
    raise SystemExit(main([*sys.argv[1:], "ingest"]))
