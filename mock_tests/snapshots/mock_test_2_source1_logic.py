"""
MOCK TEST 2: LOGIC ROBUSTNESS TEST
Test schema behavior under dirty data
"""

import json
from datetime import datetime

# ---------- CONFIG ----------
LOG_FILE = "mock_test_2_source1_logic_result.txt"

def log(title, content=None):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(title + "\n")
        if content is not None:
            f.write(json.dumps(content, indent=2, ensure_ascii=False))
            f.write("\n\n")
    print(title)
    if content is not None:
        print(content)

# ---------- INIT LOG ----------
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write("MOCK TEST 2 – SOURCE 1 LOGIC ROBUSTNESS RESULT\n")
    f.write(f"Timestamp: {datetime.now()}\n")
    f.write("=" * 60 + "\n\n")

# ---------- CASE 1: MISSING SUMMARY ----------
item1 = {
    "name": "Test Song",
    "artist": "Artist",
    "tags": ["pop"],
    "lyrics": "I love you"
}

summary = item1.get("summary") or "AUTO SUMMARY"

log("CASE 1 — MISSING SUMMARY", {
    "input": item1,
    "output_summary": summary,
    "expected_behavior": "summary fallback is applied"
})

assert summary is not None

# ---------- CASE 2: ARTIST AS STRING ----------
artist = item1["artist"]
if isinstance(artist, str):
    artist_norm = artist
else:
    artist_norm = " & ".join(artist)

log("CASE 2 — ARTIST AS STRING", {
    "input_artist": artist,
    "normalized_artist": artist_norm,
    "expected_behavior": "artist kept as string or normalized downstream"
})

# ---------- CASE 3: DIRTY NAME ----------
dirty = "  VOY A LLeVARTE PA PR  "
clean = dirty.strip()

log("CASE 3 — DIRTY NAME", {
    "input_name": dirty,
    "clean_name": clean,
    "expected_behavior": "leading/trailing spaces removed"
})

assert clean == "VOY A LLeVARTE PA PR"

# ---------- CASE 4: EXTRA FIELD ----------
item2 = {
    "name": "Extra",
    "artist": "X",
    "unknown_field": "SHOULD BE IGNORED"
}

schema_keys = {
    "name","artist","release_date","duration","tempo",
    "valence","danceability","lyrics","tags","summary",
    "emotion","context"
}

clean_item = {k: item2.get(k) for k in schema_keys}

log("CASE 4 — EXTRA FIELD", {
    "input": item2,
    "output": clean_item,
    "expected_behavior": "unknown fields removed from schema"
})

assert "unknown_field" not in clean_item

log("ALL SOURCE 1 LOGIC TESTS PASSED")
