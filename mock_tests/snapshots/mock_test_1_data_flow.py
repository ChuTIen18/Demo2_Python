"""
MOCK TEST 1: DATA FLOW TEST
Simulate full data transformation without calling APIs
"""

import json
from datetime import datetime

# ---------- CONFIG ----------
LOG_FILE = "mock_test_1_data_flow_result.txt"

def log(msg, obj=None):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
        if obj is not None:
            f.write(json.dumps(obj, indent=2, ensure_ascii=False))
            f.write("\n\n")
    print(msg)
    if obj is not None:
        print(obj)

# ---------- INIT LOG ----------
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write("MOCK TEST 1 – DATA FLOW TEST RESULT\n")
    f.write(f"Timestamp: {datetime.now()}\n")
    f.write("=" * 60 + "\n\n")

# ---------- STEP 1: RAW API SNAPSHOT ----------
raw_api = {
    "name": "Hello",
    "artist": "Adele",
    "tags": ["pop", "soul"],
    "duration": 295000,
    "lyrics": "Hello, it's me. I was wondering...",
    "wiki": {
        "summary": "A song by Adele from the album 25."
    }
}

log("STEP 1 — RAW API SNAPSHOT", raw_api)

# ---------- STEP 2: AFTER LAST.FM + GENIUS ----------
tags = raw_api.get("tags", [])
summary = raw_api.get("wiki", {}).get("summary", "")
lyrics = raw_api.get("lyrics", "")

log("STEP 2 — EXTRACTED FIELDS", {
    "tags": tags,
    "summary": summary,
    "lyrics": lyrics
})

# ---------- STEP 3: ESTIMATE AUDIO FIELDS ----------
tempo = 80
valence = 0.35
danceability = 0.42

log("STEP 3 — AUDIO FEATURES", {
    "tempo": tempo,
    "valence": valence,
    "danceability": danceability
})

# ---------- STEP 4: EMOTION + CONTEXT ----------
emotion = "melancholic"
context = "relaxing / late night / studying"

log("STEP 4 — EMOTION & CONTEXT", {
    "emotion": emotion,
    "context": context
})

# ---------- STEP 5: FINAL SCHEMA (songs_dedup.json) ----------
song_dedup = {
    "name": raw_api["name"],
    "artist": raw_api["artist"],
    "release_date": None,
    "duration": raw_api["duration"],
    "tempo": tempo,
    "valence": valence,
    "danceability": danceability,
    "lyrics": lyrics,
    "tags": tags,
    "summary": summary,
    "emotion": emotion,
    "context": context
}

log("STEP 5 — FINAL METADATA (songs_dedup.json)", song_dedup)

# ---------- STEP 6: DESCRIPTION GENERATION ----------
description = (
    f"{song_dedup['summary']} "
    f"The song has a {emotion} feeling and fits {context}."
)

song_details = {
    "name": song_dedup["name"],
    "description": description
}

log("STEP 6 — DESCRIPTION (songs_details.json)", song_details)

log("MOCK TEST 1 COMPLETED SUCCESSFULLY")
