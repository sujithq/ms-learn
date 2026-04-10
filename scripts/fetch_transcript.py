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


def fetch_xp_summary(docs_id):
    """Fetch profile XP summary from the achievements API."""
    if not docs_id:
        return None

    xp_url = f"https://learn.microsoft.com/api/achievements/xp/{docs_id}"
    try:
        xp_data = fetch_json(xp_url)
        if isinstance(xp_data, dict) and isinstance(xp_data.get("totalXp"), int):
            return xp_data
    except Exception as exc:
        print(f"Could not fetch XP summary from {xp_url}: {exc}")

    return None


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


def fetch_catalog_module_map():
    """Fetch UID->module metadata from the MS Learn catalog."""
    module_map = {}
    try:
        data = fetch_json(CATALOG_MODULES_URL)
        modules = data.get("modules", []) if isinstance(data, dict) else []
        for module in modules:
            uid = module.get("uid")
            if uid and uid not in module_map:
                module_map[uid] = module
    except Exception as exc:
        print(f"Could not fetch module catalog map from {CATALOG_MODULES_URL}: {exc}")

    print(f"Module catalog entries: {len(module_map)}")
    return module_map


def load_existing_xp_map(output_path):
    """Load existing non-zero XP values from the previous output file."""
    if not output_path.exists():
        return {}

    try:
        with open(output_path, encoding="utf-8") as f:
            existing = json.load(f)
    except Exception as exc:
        print(f"Could not read existing transcript for XP fallback: {exc}")
        return {}

    modules = existing.get("modulesCompleted", []) if isinstance(existing, dict) else []
    xp_by_uid = {}
    for module in modules:
        if not isinstance(module, dict):
            continue
        uid = module.get("uid")
        xp = module.get("xp")
        if uid and isinstance(xp, int) and xp > 0:
            xp_by_uid[uid] = xp

    print(f"Existing non-zero XP entries loaded: {len(xp_by_uid)}")
    return xp_by_uid


def extract_module_xp(module, catalog_module, existing_xp_by_uid):
    """Resolve module XP from transcript, catalog, or previous output fallback."""
    xp_keys = ("xp", "points", "rewardPoints", "experiencePoints", "earnedXp")

    for key in xp_keys:
        value = module.get(key)
        if isinstance(value, int) and value > 0:
            return value

    for key in xp_keys:
        value = catalog_module.get(key)
        if isinstance(value, int) and value > 0:
            return value

    uid = module.get("uid")
    if uid and uid in existing_xp_by_uid:
        return existing_xp_by_uid[uid]

    return 0


def enrich_completed_modules(data, module_map, existing_xp_by_uid):
    """Normalize and enrich completed modules for UI filtering and display."""
    modules = data.get("modulesCompleted")
    if not isinstance(modules, list):
        return

    enriched_count = 0
    non_zero_xp_count = 0
    for module in modules:
        if not isinstance(module, dict):
            continue

        uid = module.get("uid")
        catalog_module = module_map.get(uid, {}) if uid else {}

        # Keep UI-consumed fields populated even if transcript payload is sparse.
        module["completionDate"] = module.get("completionDate") or module.get("completedOn")
        module["duration"] = (
            module.get("duration")
            or module.get("durationInMinutes")
            or catalog_module.get("duration_in_minutes")
            or 0
        )
        module.pop("durationInMinutes", None)
        module["xp"] = extract_module_xp(module, catalog_module, existing_xp_by_uid)
        if module["xp"] > 0:
            non_zero_xp_count += 1
        module["iconUrl"] = module.get("iconUrl") or catalog_module.get("icon_url")
        module["roles"] = module.get("roles") or catalog_module.get("roles") or []
        module["levels"] = module.get("levels") or catalog_module.get("levels") or []
        module["products"] = module.get("products") or catalog_module.get("products") or []
        module["locale"] = module.get("locale") or catalog_module.get("locale")

        enriched_count += 1

    print(f"Modules enriched: {enriched_count}")
    print(f"Modules with non-zero XP: {non_zero_xp_count}")
    if enriched_count > 0 and non_zero_xp_count == 0:
        print("Warning: XP is missing from upstream data; kept as 0 where no fallback exists.")


def normalize_learning_path_durations(data):
    """Normalize learning path duration field naming to 'duration'."""
    learning_paths = data.get("learningPathsCompleted")
    if not isinstance(learning_paths, list):
        return

    for learning_path in learning_paths:
        if not isinstance(learning_path, dict):
            continue

        learning_path["duration"] = (
            learning_path.get("duration")
            or learning_path.get("durationInMinutes")
            or 0
        )
        learning_path.pop("durationInMinutes", None)


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

        # Normalize/enrich module metadata used by filters and badges.
        module_map = fetch_catalog_module_map()
        existing_xp_by_uid = load_existing_xp_map(OUTPUT_PATH)
        enrich_completed_modules(data, module_map, existing_xp_by_uid)

        # Keep duration field naming consistent across payload sections.
        normalize_learning_path_durations(data)

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

        # Add profile-level XP summary (available even when module XP is missing).
        xp_summary = fetch_xp_summary(data.get("docsId"))
        if xp_summary:
            data["totalXp"] = xp_summary.get("totalXp", 0)
            print(f"Total XP from profile endpoint: {data['totalXp']}")
        else:
            data["totalXp"] = sum(
                module.get("xp", 0)
                for module in data.get("modulesCompleted", [])
                if isinstance(module, dict)
            )
            print(f"Total XP fallback from module XP: {data['totalXp']}")

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Saved to: {OUTPUT_PATH}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
