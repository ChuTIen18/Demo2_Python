import json

# Đọc file JSON
with open("songs_details.json", "r", encoding="utf-8") as f:
    songs = json.load(f)

def normalize(value):
    """Chuẩn hóa dữ liệu để so sánh"""
    if isinstance(value, str):
        return value.strip().lower()
    return str(value).strip().lower()

# Map (name, description) -> danh sách index
song_map = {}

for idx, song in enumerate(songs, start=1):  # index bắt đầu từ 1
    name = normalize(song.get("name", ""))
    description = normalize(song.get("description", ""))
    key = (name, description)

    if key not in song_map:
        song_map[key] = []
    song_map[key].append(idx)

# Tìm trùng lặp
duplicates = []
for (name, description), indices in song_map.items():
    if len(indices) > 1:
        first = indices[0]
        for dup in indices[1:]:
            duplicates.append(
                f"Bài {dup} trùng với bài {first}: '{name}'"
            )

# In kết quả
for line in duplicates:
    print(line)

print(f"\nTổng cộng: {len(duplicates)} cặp trùng lặp dựa trên (name + description).")
