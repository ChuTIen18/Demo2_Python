import json

file_path = "songs_dedup.json"

with open(file_path, "r", encoding="utf-8") as f:
    songs = json.load(f)

print(f" Tổng số bài hát trong file: {len(songs)}")

print("\nDanh sách bài hát:")
for idx, song in enumerate(songs, start=1):
    name = song.get("name", "Không rõ tên")
    artist = song.get("artist", "Không rõ tác giả")
    print(f"{idx}. {name} - {artist}")
