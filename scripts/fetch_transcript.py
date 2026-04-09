#!/usr/bin/env python3
"""Fetch MS Learn transcript data and save to JSON file."""

import json
import sys
import urllib.request
from pathlib import Path

TRANSCRIPT_ID = "71pnqhwmx5xn8ww"
API_URL = f"https://learn.microsoft.com/api/profiles/transcript/share/{TRANSCRIPT_ID}?locale=en-us&isModuleAssessment=true"
OUTPUT_PATH = Path(__file__).parent.parent / "src" / "ms-learn" / "wwwroot" / "data" / "transcript.json"


def fetch_transcript():
    """Fetch the transcript data from MS Learn API."""
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; GitHub Actions transcript fetcher)",
        "Accept": "application/json",
    }
    req = urllib.request.Request(API_URL, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data


def main():
    print(f"Fetching transcript from: {API_URL}")
    try:
        data = fetch_transcript()
        print(f"Fetched data: {data.get('totalModulesCompleted', 0)} modules completed")

        # Log all top-level keys to help debug what's available
        print(f"Available keys in response: {', '.join(data.keys())}")

        # Check for trophies specifically
        if 'trophies' in data:
            trophies_count = len(data['trophies']) if isinstance(data['trophies'], list) else 0
            print(f"Trophies found: {trophies_count}")
        else:
            print("Warning: No 'trophies' field in API response")
            # Add empty trophies array if not present to match the model
            data['trophies'] = []
            print("Added empty 'trophies' array to match model structure")

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Saved to: {OUTPUT_PATH}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
