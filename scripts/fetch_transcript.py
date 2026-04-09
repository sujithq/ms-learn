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

CATALOG_LEARNING_PATHS_URL = "https://learn.microsoft.com/api/catalog/?locale=en-us&type=learningPaths"
CATALOG_MODULES_URL = "https://learn.microsoft.com/api/catalog/?locale=en-us&type=modules"
CATALOG_CERTIFICATIONS_URL = "https://learn.microsoft.com/api/catalog/?locale=en-us&type=certifications"
GENERIC_TROPHY_ICON_URL = "https://learn.microsoft.com/en-us/training/achievements/generic-trophy.svg"
OFFICIAL_APPLIED_SKILL_ICON_URL = (
    "https://learn.microsoft.com/en-us/media/learn/credential/badges/applied-skill.svg"
)


def fetch_json(url):
    """Fetch JSON data from a URL."""
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_transcript():
    """Fetch the transcript data from MS Learn API."""
    return fetch_json(API_URL)


def fetch_catalog_icon_map():
    """Fetch UID->icon URL mappings from the MS Learn catalog.

    Learning path UIDs are the primary source for trophies. Modules are also
    loaded as a secondary source for UIDs that might overlap or be reclassified.
    """
    icon_map = {}
    sources = [
        (CATALOG_LEARNING_PATHS_URL, "learningPaths"),
        (CATALOG_MODULES_URL, "modules"),
    ]

    for url, collection_key in sources:
        try:
            data = fetch_json(url)
            items = data.get(collection_key, []) if isinstance(data, dict) else []
            for item in items:
                uid = item.get("uid")
                icon_url = item.get("icon_url")
                if uid and icon_url and uid not in icon_map:
                    icon_map[uid] = icon_url
        except Exception as exc:
            print(f"Could not fetch catalog icon map from {url}: {exc}")

    print(f"Catalog icon map entries: {len(icon_map)}")
    return icon_map


def normalize_text(value):
    """Normalize text values for resilient catalog matching."""
    if not value:
        return ""
    # Some transcript values may contain replacement characters from encoding.
    return " ".join(value.replace("�", "").split()).strip().lower()


def fetch_certification_icon_map():
    """Fetch title->icon URL mappings for certifications from the catalog."""
    icon_map = {}
    try:
        data = fetch_json(CATALOG_CERTIFICATIONS_URL)
        items = data.get("certifications", []) if isinstance(data, dict) else []
        for item in items:
            title = normalize_text(item.get("title"))
            icon_url = item.get("icon_url")
            if title and icon_url and title not in icon_map:
                icon_map[title] = icon_url
    except Exception as exc:
        print(f"Could not fetch certification icon map from catalog: {exc}")

    print(f"Certification icon map entries: {len(icon_map)}")
    return icon_map


def enrich_certification_icons(data, certification_icon_map):
    """Populate official certification icon URLs when available."""
    certification_data = data.get("certificationData")
    if not isinstance(certification_data, dict):
        return

    updated = 0
    for key in ("activeCertifications", "historicalCertifications"):
        certs = certification_data.get(key, [])
        if not isinstance(certs, list):
            continue

        for cert in certs:
            if not isinstance(cert, dict):
                continue
            title_key = normalize_text(cert.get("name"))
            if not title_key:
                continue
            icon_url = certification_icon_map.get(title_key)
            if icon_url:
                cert["iconUrl"] = icon_url
                updated += 1

    print(f"Certification icons applied: {updated}")


def enrich_applied_skill_icons(data):
    """Populate official applied skills icon URLs."""
    applied_data = data.get("appliedSkillsData")
    if not isinstance(applied_data, dict):
        return

    skills = applied_data.get("appliedSkillsCredentials", [])
    if not isinstance(skills, list):
        return

    for skill in skills:
        if isinstance(skill, dict):
            skill["iconUrl"] = OFFICIAL_APPLIED_SKILL_ICON_URL

    print(f"Applied skill icons applied: {len(skills)}")


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


def fetch_trophy_icon_url(uid, icon_map):
    """Resolve a trophy icon URL by achievement UID.

    Uses the MS Learn catalog icon map keyed by UID. Falls back to a generic
    trophy icon when no UID match exists.
    """
    if not uid:
        return GENERIC_TROPHY_ICON_URL

    return icon_map.get(uid, GENERIC_TROPHY_ICON_URL)


def derive_trophies_from_learning_paths(learning_paths, icon_map):
    """Derive trophy data from completed learning paths as a fallback.

    Each completed learning path in MS Learn awards a trophy/badge. A trophy
    entry is created for every learning path. The script resolves icon URLs
    from each UID via the MS Learn catalog icon map.
    The 'completedOn' field from each learning path is mapped to 'earnedDate'
    on the resulting trophy object.
    """
    trophies = []
    for lp in learning_paths:
        uid = lp.get("uid", "")
        icon_url = lp.get("iconUrl") or fetch_trophy_icon_url(uid, icon_map)

        trophy = {
            "uid": uid,
            "title": lp.get("title", ""),
            "iconUrl": icon_url,
            "earnedDate": lp.get("completedOn"),
        }
        trophies.append(trophy)
    return trophies


def main():
    print(f"Fetching transcript from: {API_URL}")
    try:
        data = fetch_transcript()
        print(f"Fetched data: {data.get('totalModulesCompleted', 0)} modules completed")

        # Populate trophies from the transcript learning paths.
        learning_paths = data.get("learningPathsCompleted", [])
        icon_map = fetch_catalog_icon_map()
        print(f"Deriving {len(learning_paths)} trophies from learningPathsCompleted")
        trophies = derive_trophies_from_learning_paths(learning_paths, icon_map)
        data["trophies"] = trophies
        print(f"Total trophies: {len(trophies)}")

        # Populate official icons for certifications and applied skills.
        certification_icon_map = fetch_certification_icon_map()
        enrich_certification_icons(data, certification_icon_map)
        enrich_applied_skill_icons(data)

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Saved to: {OUTPUT_PATH}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
