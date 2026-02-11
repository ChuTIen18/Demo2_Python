import json

# Đọc file JSON
with open("songs_dedup.json", "r", encoding="utf-8") as f:
    songs = json.load(f)

def normalize(value):
    """Chuẩn hóa dữ liệu: list -> string, string -> string"""
    if isinstance(value, list):
        return ", ".join(str(v).strip().lower() for v in value)  # list -> chuỗi
    elif isinstance(value, str):
        return value.strip().lower()
    else:
        return str(value).strip().lower()

# Map (name, artist, tags) -> danh sách index
song_map = {}

for idx, song in enumerate(songs, start=1):  # index tính từ 1
    name = normalize(song.get("name", ""))
    artist = normalize(song.get("artist", ""))
    tags = normalize(song.get("tags", ""))

    key = (name, artist, tags)

    if key not in song_map:
        song_map[key] = []
    song_map[key].append(idx)

# Tìm trùng lặp theo (name + artist + tags)
duplicates = []
for (name, artist, tags), indices in song_map.items():
    if len(indices) > 1:
        first = indices[0]
        for dup in indices[1:]:
            duplicates.append(
                f"Bài {dup} trùng với bài {first}: '{name}' - {artist} [tags: {tags}]"
            )

# In kết quả
for line in duplicates:
    print(line)

print(f"\nTổng cộng: {len(duplicates)} cặp trùng lặp dựa trên (name + artist + tags).")
