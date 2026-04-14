"""
Iris — This or That aesthetic preference game
Fetches image pairs from Unsplash and builds a structured aesthetic profile.
"""

import os
import json
import requests

UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")

VENDOR_CATEGORIES = [
    "Venue",
    "Photography",
    "Music & entertainment",
    "Florals",
    "Food & catering",
    "Hair & makeup",
    "Cake & desserts",
    "Invitations & stationery",
    "Transportation",
]

# ── Image pair definitions ─────────────────────────────────────────────────────
# priority_keys: which vendor category selections trigger this this-or-that category

CATEGORIES = [
    {
        "name": "venue",
        "label": "Venue Style",
        "instruction": "Pick the setting that feels more like you.",
        "priority_keys": ["Venue"],
        "pairs": [
            {
                "a": {"query": "outdoor garden wedding ceremony flowers", "label": "Outdoor & Natural"},
                "b": {"query": "indoor ballroom wedding elegant chandelier", "label": "Indoor & Grand"},
            },
            {
                "a": {"query": "rustic barn wedding reception warm lights", "label": "Rustic & Warm"},
                "b": {"query": "modern minimalist wedding venue clean white", "label": "Modern & Clean"},
            },
            {
                "a": {"query": "intimate courtyard wedding string lights", "label": "Intimate & Cozy"},
                "b": {"query": "luxury estate wedding garden formal", "label": "Luxurious & Formal"},
            },
        ],
    },
    {
        "name": "photography",
        "label": "Photography Style",
        "instruction": "Pick the photo style that speaks to you.",
        "priority_keys": ["Photography"],
        "pairs": [
            {
                "a": {"query": "moody dark editorial wedding photography film", "label": "Moody & Editorial"},
                "b": {"query": "bright airy light wedding photography natural", "label": "Bright & Airy"},
            },
            {
                "a": {"query": "candid documentary wedding photography genuine", "label": "Candid & Real"},
                "b": {"query": "classic posed elegant wedding portrait couple", "label": "Classic & Posed"},
            },
        ],
    },
    {
        "name": "florals",
        "label": "Floral Style",
        "instruction": "Pick the floral vibe that fits your vision.",
        "priority_keys": ["Florals"],
        "pairs": [
            {
                "a": {"query": "lush garden wedding florals greenery organic", "label": "Lush & Wild"},
                "b": {"query": "minimal modern wedding flowers white clean", "label": "Minimal & Modern"},
            },
            {
                "a": {"query": "wildflower wedding bouquet romantic loose", "label": "Wildflower & Romantic"},
                "b": {"query": "structured rose wedding bouquet classic formal", "label": "Classic & Structured"},
            },
        ],
    },
    {
        "name": "reception",
        "label": "Reception Vibe",
        "instruction": "Pick the atmosphere you want your guests to feel.",
        "priority_keys": ["Music & entertainment", "Food & catering"],
        "pairs": [
            {
                "a": {"query": "outdoor wedding reception garden party tables", "label": "Garden Party"},
                "b": {"query": "wedding reception candlelit dinner tables elegant", "label": "Candlelit Dinner"},
            },
            {
                "a": {"query": "wedding dance floor party celebration guests", "label": "High Energy Party"},
                "b": {"query": "wedding reception intimate dinner conversation", "label": "Intimate Gathering"},
            },
        ],
    },
    {
        "name": "hair_makeup",
        "label": "Hair & Makeup Vibe",
        "instruction": "Pick the bridal look that feels like you.",
        "priority_keys": ["Hair & makeup"],
        "pairs": [
            {
                "a": {"query": "natural glowing bridal makeup soft romantic", "label": "Natural & Glowing"},
                "b": {"query": "bold glamorous bridal makeup dramatic", "label": "Bold & Glamorous"},
            },
            {
                "a": {"query": "loose boho bridal hair updo flowers", "label": "Loose & Bohemian"},
                "b": {"query": "sleek elegant bridal updo classic polished", "label": "Sleek & Polished"},
            },
        ],
    },
]


def get_filtered_categories(priorities: list, delegated: list) -> list:
    """Return only categories where at least one priority_key is in priorities
    and none are in delegated."""
    result = []
    for cat in CATEGORIES:
        keys = cat["priority_keys"]
        is_priority = any(k in priorities for k in keys)
        is_delegated = any(k in delegated for k in keys)
        if is_priority and not is_delegated:
            result.append(cat)
    # Always include venue and photography as fallback if nothing selected
    if not result:
        result = [c for c in CATEGORIES if c["name"] in ("venue", "photography")]
    return result


# ── Unsplash fetch ─────────────────────────────────────────────────────────────

def fetch_image_url(query: str) -> str:
    try:
        response = requests.get(
            "https://api.unsplash.com/photos/random",
            params={"query": query, "orientation": "landscape", "content_filter": "high"},
            headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"},
            timeout=5,
        )
        data = response.json()
        return data["urls"]["regular"]
    except Exception:
        return f"https://placehold.co/600x400/f8f4f0/9B7AB8?text={query.split()[0].title()}"


def preload_images(session_state, filtered_categories: list) -> None:
    if "tot_images" in session_state:
        return
    images = {}
    for cat in filtered_categories:
        for pair_i, pair in enumerate(cat["pairs"]):
            key_a = f"{cat['name']}_{pair_i}_a"
            key_b = f"{cat['name']}_{pair_i}_b"
            images[key_a] = fetch_image_url(pair["a"]["query"])
            images[key_b] = fetch_image_url(pair["b"]["query"])
    session_state["tot_images"] = images


# ── Preference extraction ──────────────────────────────────────────────────────

def build_extraction_prompt(selections: list) -> str:
    lines = []
    for s in selections:
        lines.append(
            f"Category: {s['category']} | Chose: \"{s['chosen_label']}\" over \"{s['rejected_label']}\""
        )
    choices_text = "\n".join(lines)
    return f"""Based on these aesthetic choices made during a wedding style quiz, extract a preference profile.

Choices made:
{choices_text}

Return ONLY valid JSON with this structure:
{{
  "venue": {{
    "setting": "indoor or outdoor preference",
    "formality": "formal / semi-formal / relaxed",
    "vibe": "2-3 word description"
  }},
  "photography": {{
    "style": "editorial / documentary / classic / etc",
    "mood": "moody / bright / warm / etc",
    "approach": "candid / posed / mix"
  }},
  "florals": {{
    "density": "lush / minimal / structured",
    "style": "wild / classic / modern / romantic",
    "palette_direction": "colorful / white / greenery / etc"
  }},
  "reception": {{
    "energy": "high energy / intimate / elegant / etc",
    "atmosphere": "2-3 word description"
  }},
  "hair_makeup": {{
    "makeup": "natural / bold / classic",
    "hair": "loose / updo / bohemian / sleek"
  }},
  "overall_vibe": "One sentence describing their complete aesthetic"
}}

Only include keys for categories that appear in the choices. Omit the rest."""
