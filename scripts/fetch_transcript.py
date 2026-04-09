#!/usr/bin/env python3
"""Fetch MS Learn transcript data and save to JSON file."""

import json
import sys
import urllib.request
from pathlib import Path

TRANSCRIPT_ID = "71pnqhwmx5xn8ww"
API_URL = f"https://learn.microsoft.com/api/profiles/transcript/share/{TRANSCRIPT_ID}?locale=en-us&isModuleAssessment=true"
OUTPUT_PATH = Path(__file__).parent.parent / "src" / "ms-learn" / "wwwroot" / "data" / "transcript.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; GitHub Actions transcript fetcher)",
    "Accept": "application/json",
}


def fetch_json(url):
    """Fetch JSON data from a URL."""
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_transcript():
    """Fetch the transcript data from MS Learn API."""
    return fetch_json(API_URL)


def fetch_trophies(username, docs_id):
    """Try to fetch trophies from the MS Learn achievements API.

    Returns a list of trophy dicts, or None if not available.
    """
    candidate_urls = [
        f"https://learn.microsoft.com/api/profiles/{docs_id}/achievements/trophies?locale=en-us&pageSize=500",
        f"https://learn.microsoft.com/api/profiles/{username}/achievements/trophies?locale=en-us&pageSize=500",
    ]
    for url in candidate_urls:
        try:
            print(f"Trying trophies endpoint: {url}")
            result = fetch_json(url)
            # Handle different possible response structures
            if isinstance(result, list):
                print(f"  Got {len(result)} trophies (array response)")
                return result
            if isinstance(result, dict):
                for key in ("trophies", "items", "value"):
                    if key in result and isinstance(result[key], list):
                        print(f"  Got {len(result[key])} trophies (field '{key}')")
                        return result[key]
        except Exception as exc:
            print(f"  Could not fetch trophies from {url}: {exc}")
    return None


def derive_trophies_from_learning_paths(learning_paths):
    """Derive trophy data from completed learning paths as a fallback.

    Each completed learning path in MS Learn awards a trophy/badge.
    """
    trophies = []
    for lp in learning_paths:
        uid = lp.get("uid", "")
        trophy = {
            "uid": uid,
            "title": lp.get("title", ""),
            "iconUrl": (
                f"https://learn.microsoft.com/training/achievements/{uid}-badge.svg"
                if uid
                else None
            ),
            "earnedDate": lp.get("completedOn"),
        }
        trophies.append(trophy)
    return trophies


def main():
    print(f"Fetching transcript from: {API_URL}")
    try:
        data = fetch_transcript()
        print(f"Fetched data: {data.get('totalModulesCompleted', 0)} modules completed")

        # Populate trophies: try the achievements API first, then fall back to
        # deriving them from the learning paths already present in the transcript.
        username = data.get("userName", "")
        docs_id = data.get("docsId", "")
        trophies = fetch_trophies(username, docs_id)
        if trophies is None:
            learning_paths = data.get("learningPathsCompleted", [])
            print(
                f"Falling back to deriving {len(learning_paths)} trophies "
                "from learningPathsCompleted"
            )
            trophies = derive_trophies_from_learning_paths(learning_paths)
        data["trophies"] = trophies
        print(f"Total trophies: {len(trophies)}")

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Saved to: {OUTPUT_PATH}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
