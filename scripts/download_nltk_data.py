"""One-shot setup script: fetches the NLTK corpora sentiment scoring needs.

Run once after installing dependencies (also invoked by the Dockerfile
during image build so containers start with the lexicon already
cached):

    python scripts/download_nltk_data.py
"""
from __future__ import annotations

import nltk


def main() -> None:
    for resource in ("vader_lexicon", "punkt", "punkt_tab"):
        try:
            nltk.download(resource, quiet=True)
            print(f"downloaded: {resource}")
        except Exception as exc:  # noqa: BLE001
            print(f"skipped {resource}: {exc}")


if __name__ == "__main__":
    main()
