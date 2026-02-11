# -*- coding: utf-8 -*-
import os
import re
import json
import time
import random
import requests
from typing import Tuple, List, Optional
from bs4 import BeautifulSoup
from requests.exceptions import Timeout

# ================== CONFIG (đã điền key của bạn) ==================
LASTFM_API_KEY = "19f9b563fbe36aa43e7ae010f6961687"                                                     # SỬA CHỖ NÀY THÀNH CỦA MÌNH
GENIUS_API_KEY = "KSZdvEPLzk21k1PB5etSTgJdbZ4cG1e6jmobf2ZSFCMe0UjYJnpnPL1X5yzgdlg6"  
AUDD_API_KEY   = "c59df2ddd5c8e8e62d3337535755a2ed"           
SCRAPESOFT_API_KEY = "888d810b8cmsh560e2a2fa494b79p1a25bdjsn47d0bd513e7e"                                                       # SỬA CHỖ NÀY THÀNH CỦA MÌNH
OUTPUT_FILE = "songs_dedup.json"
TOP_LIMIT = 50  # số bài muốn lấy mỗi lần
SLEEP_RANGE = (0.4, 1.0)  # giãn cách request chống rate limit
UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0 Safari/537.36"
}
# ================================================================


# ------------------ Helpers ------------------
def sleep_jitter():
    time.sleep(random.uniform(*SLEEP_RANGE))


def clean_text_basic(s: str) -> str:
    s = re.sub(r"\s+", " ", s or "").strip()
    return s


def normalize_title_artist(s: str) -> str:
    """
    Bỏ (Live), [Remix], feat., ft., version... để tăng tỉ lệ match khi search Genius.
    """
    s = re.sub(r"\(.*?\)|\[.*?\]", "", s)  # remove (xxx) / [xxx]
    s = re.sub(r"\b(feat\.?|ft\.?)\b.*", "", s, flags=re.I)  # remove feat. xxx
    s = re.sub(r"(?i)\b(remix|version|edit|single|track)\b", "", s)
    s = re.sub(r"\s+", " ", s).strip(" -–—|")
    return s


def is_likely_english(text: str) -> bool:
    """
    Heuristic đơn giản: nếu phần lớn ký tự là Latin và có vài từ tiếng Anh phổ biến → coi là English.
    """
    if not text:
        return True
    sample = text[:4000]  # đủ để ước lượng
    total = len(sample)
    if total == 0:
        return True

    latin = sum(1 for ch in sample if ch.isascii())
    ratio = latin / total

    common_en = ["the", "and", "you", "love", "I ", "I'm", "don't", "yeah", "baby", "oh "]
    has_common = any(w.lower() in sample.lower() for w in common_en)

    return ratio > 0.92 or (ratio > 0.85 and has_common)


# ------------------ Last.fm ------------------
def lastfm_top_tracks_random(limit=50) -> List[Tuple[str, str]]:
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "chart.gettoptracks",
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": 50,  # mỗi trang 50 bài
        "page": random.randint(1, 100)  # random từ trang 21 đến 40 (1001–2000)
    }
    try:
        r = requests.get(url, params=params, headers=UA, timeout=25)
        r.raise_for_status()
        data = r.json()
        
        # Debug: Print the full response to see its structure
        print("Last.fm API Response:", json.dumps(data, indent=2))
        
        if "tracks" not in data or "track" not in data["tracks"]:
            raise ValueError("Unexpected API response format - 'tracks.track' not found")
            
        all_tracks = [(t["name"], t["artist"]["name"]) for t in data["tracks"]["track"]]
        
        # Nếu muốn random tiếp từ 50 bài của trang này thì vẫn giữ code này
        if len(all_tracks) < limit:
            raise ValueError(f"Only got {len(all_tracks)} tracks, need at least {limit}")
            
        return random.sample(all_tracks, limit)
    except Exception as e:
        print(f"Error in lastfm_top_tracks_random: {str(e)}")
        raise




def lastfm_track_info(artist: str, track: str) -> Tuple[List[str], str, Optional[int]]:
    """
    Lấy tags, summary (wiki) và duration (ms) từ Last.fm track.getInfo nếu có.
    """
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "track.getInfo",
        "api_key": LASTFM_API_KEY,
        "artist": artist,
        "track": track,
        "format": "json"
    }
    try:
        r = requests.get(url, params=params, headers=UA, timeout=25)
        if r.status_code != 200:
            return [], "", None
        j = r.json()
        tags = []
        summary = ""
        duration_ms = None

        try:
            tags = [t["name"] for t in j["track"].get("toptags", {}).get("tag", [])]
        except Exception:
            pass

        try:
            duration_ms = j["track"].get("duration")
            if duration_ms:
                duration_ms = int(duration_ms)  # Last.fm trả ms
        except Exception:
            duration_ms = None

        try:
            summary_html = j["track"].get("wiki", {}).get("summary", "")
            # bỏ link "Read more" và tag HTML
            summary_clean = re.sub(r"<a.*?>.*?</a>", "", summary_html)
            summary = BeautifulSoup(summary_clean, "html.parser").get_text(" ").strip()
        except Exception:
            summary = ""
        return tags, summary, duration_ms
    except Exception:
        return [], "", None




# ------------------ Genius ------------------
def genius_search_api(track: str, artist: str) -> Optional[str]:
    headers = {"Authorization": f"Bearer {GENIUS_API_KEY}", **UA}
    q = f"{track} {artist}"
    try:
        r = requests.get("https://api.genius.com/search", params={"q": q}, headers=headers, timeout=25)
        if r.status_code != 200:
            return None
        hits = r.json().get("response", {}).get("hits", [])
        if not hits:
            return None
        # ưu tiên kết quả có primary artist khớp
        for h in hits:
            res = h.get("result", {})
            pa = res.get("primary_artist", {}).get("name", "")
            title = res.get("title", "")
            if artist.lower() in pa.lower() or track.lower() in title.lower():
                return res.get("url")
        return hits[0]["result"].get("url")
    except Exception:
        return None


def genius_search_html(track: str, artist: str) -> Optional[str]:
    q = f"{track} {artist}"
    try:
        r = requests.get("https://genius.com/search", params={"q": q}, headers=UA, timeout=25)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, "html.parser")
        # các kết quả mini card / small card
        a = soup.select_one("a.mini_card, a.mini_card--small")
        return a["href"] if a and a.has_attr("href") else None
    except Exception:
        return None


def parse_genius_lyrics_from_url(url: str) -> Optional[str]:
    try:
        page = requests.get(url, headers=UA, timeout=25)
        if page.status_code != 200:
            return None
        soup = BeautifulSoup(page.text, "html.parser")
        # Lyrics mới của Genius nằm trong nhiều <div data-lyrics-container="true">
        containers = soup.find_all("div", {"data-lyrics-container": "true"})
        if containers:
            text = "\n".join([c.get_text(separator="\n") for c in containers])
            return clean_text_basic(text)
        # Fallback cấu trúc cũ
        legacy = soup.select_one("div.lyrics")
        if legacy:
            return clean_text_basic(legacy.get_text("\n"))
        return None
    except Exception:
        return None


def get_full_lyrics(track: str, artist: str) -> Optional[str]:
    # 1) Thử Genius
    url = genius_search_api(track, artist)
    if not url:
        url = genius_search_html(track, artist)
    if url:
        lyrics = parse_genius_lyrics_from_url(url)
        if lyrics:
            return lyrics

    # 2) Thử LRCLIB
    lyrics = lyrics_lrclib(track, artist)
    if lyrics:
        return lyrics

    # 3) Thử Scrapesoft (RapidAPI)
    lyrics = lyrics_scrapesoft(track, artist)
    if lyrics:
        return lyrics

    # 4) Thử AudD
    lyrics = lyrics_audd(track, artist)
    if lyrics:
        return lyrics

    return None


# ------------------ LRCLIB ------------------
def lyrics_lrclib(track: str, artist: str) -> Optional[str]:
    """
    Tìm lyrics bằng LRCLIB API (free, không cần key).
    """
    try:
        url = "https://lrclib.net/api/get"
        params = {"track_name": track, "artist_name": artist}
        r = requests.get(url, params=params, headers=UA, timeout=20)
        if r.status_code == 200:
            data = r.json()
            lyrics = data.get("plainLyrics") or data.get("syncedLyrics")
            if lyrics:
                print("   ✅ LRCLIB found lyrics")
                return clean_text_basic(lyrics)
        print("   ❌ LRCLIB: no lyrics")
    except Exception as e:
        print("   ⚠️ LRCLIB error:", e)
    return None



# ------------------ AudD ------------------
def lyrics_audd(track: str, artist: str) -> Optional[str]:
    """
    Tìm lyrics bằng AudD.io API (cần API key).
    """
    if not AUDD_API_KEY or AUDD_API_KEY == "YOUR_AUDD_API_KEY_HERE":
        return None
    try:
        q = f"{track} {artist}"
        r = requests.get(
            "https://api.audd.io/findLyrics/",
            params={"q": q, "api_token": AUDD_API_KEY},
            timeout=20
        )
        if r.status_code == 200:
            data = r.json()
            if "result" in data and data["result"]:
                print("   ✅ AudD found lyrics")
                return clean_text_basic(data["result"][0]["lyrics"])
        print("   ❌ AudD: no lyrics")
    except Exception as e:
        print("   ⚠️ AudD error:", e)
    return None


# ------------------ Scrapesoft (RapidAPI) ------------------
def lyrics_scrapesoft(track: str, artist: str) -> Optional[str]:
    """
    API từ RapidAPI: Scrapesoft Music Lyrics
    """
    if not SCRAPESOFT_API_KEY:
        return None
    try:
        url = "https://scrapesoft-music-lyrics.p.rapidapi.com/songs"
        querystring = {"track": track, "artist": artist}
        headers = {
            "x-rapidapi-key": SCRAPESOFT_API_KEY,
            "x-rapidapi-host": "scrapesoft-music-lyrics.p.rapidapi.com"
        }
        r = requests.get(url, headers=headers, params=querystring, timeout=25)
        if r.status_code == 200:
            data = r.json()
            if "lyrics" in data and data["lyrics"]:
                print("   ✅ Scrapesoft found lyrics")
                return clean_text_basic(data["lyrics"])
        print("   ❌ Scrapesoft: no lyrics")
    except Exception as e:
        print("   ⚠️ Scrapesoft error:", e)
    return None

# ------------------ LibreTranslate ------------------
def translate_to_english(text: str) -> str:
    """
    Dùng LibreTranslate dịch sang tiếng Anh (source=auto).
    Nếu lỗi → trả về bản gốc.
    """
    if not text:
        return ""
    try:
        resp = requests.post(
            "https://libretranslate.com/translate",
            data={"q": text, "source": "auto", "target": "en", "format": "text"},
            timeout=40,
        )
        if resp.status_code == 200:
            out = resp.json().get("translatedText")
            return out if out else text
        return text
    except Exception:
        return text


# ------------------ AI (rule-based) để luôn đủ 12 trường ------------------
def guess_emotion_and_context(lyrics: str, tags: List[str]) -> Tuple[str, str]:
    txt = (lyrics or "").lower()
    tset = set(x.lower() for x in (tags or []))

    emo = []
    if any(w in txt for w in ["love", "darling", "kiss", "heart"]) or "love" in tset:
        emo.append("romantic")
    if any(w in txt for w in ["sad", "lonely", "tears", "cry", "broken"]):
        emo.append("melancholic")
    if any(w in txt for w in ["dance", "party", "club", "night"]) or any(w in tset for w in ["dance", "edm", "club"]):
        emo.append("energetic")
    if any(w in txt for w in ["remember", "years", "time", "memories"]) or "nostalgia" in tset:
        emo.append("nostalgic")
    if not emo:
        emo = ["mixed"]

    ctx = []
    if any(w in tset for w in ["acoustic", "chill", "lofi"]) or any(w in txt for w in ["slow", "acoustic", "quiet"]):
        ctx.append("relaxing / late night / studying")
    if any(w in txt for w in ["dance", "party", "club", "workout"]):
        ctx.append("party / workout / night out")
    if any(w in txt for w in ["road", "drive", "highway", "mile"]):
        ctx.append("road trips / long drives")
    if not ctx:
        ctx = ["general listening"]

    return ", ".join(emo), ", ".join(ctx)


def make_summary(name: str, artist: str, tags: List[str], tempo: int, emotion: str) -> str:
    t = ", ".join(tags) if tags else "pop"
    return f"'{name}' by {artist} is a {t} track around {tempo} BPM. The song feels {emotion}."


# ------------------ Tempo/valence/danceability (không dùng Spotify) ------------------
def estimate_audio_fields(lyrics: str, tags: List[str]) -> Tuple[int, float, float]:
    """
    Ước lượng hợp lý khi không có Spotify:
    - tempo: dựa vào từ khóa trong lyrics/tags (dance → nhanh; ballad → chậm)
    - valence: dựa vào từ khóa tích cực/tiêu cực
    - danceability: gần 120 BPM & có từ khóa dance/party → cao
    """
    txt = (lyrics or "").lower()
    tset = set(x.lower() for x in (tags or []))

    tempo = 105
    if any(k in txt for k in ["dance", "party", "club", "move"]) or any(k in tset for k in ["dance", "edm", "house", "club"]):
        tempo = 120
    if any(k in txt for k in ["ballad", "slow", "lonely", "sad", "cry", "tears"]):
        tempo = 80

    pos = {"love","happy","smile","sunshine","good","fun","party","free","hope","dream","kiss","sweet","together","beautiful","win"}
    neg = {"sad","lonely","cry","tears","hurt","pain","broken","dark","hate","lose","fear","cold","empty"}
    words = re.findall(r"[a-z']+", txt)
    p = sum(1 for w in words if w in pos)
    n = sum(1 for w in words if w in neg)
    sentiment = 0.0 if (p+n)==0 else (p - n) / (p + n)  # -1..+1

    valence = max(0.0, min(1.0, 0.5 + 0.4 * sentiment))
    d1 = 1.0 - min(abs(tempo - 120.0) / 60.0, 1.0)
    danceability = max(0.0, min(1.0, 0.55 * d1 + 0.45 * (0.5 + 0.5 * abs(sentiment))))
    return int(tempo), round(valence, 3), round(danceability, 3)


# ------------------ Storage ------------------
def load_existing(filename: str) -> List[dict]:
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_all(filename: str, data: List[dict]):
    tmp_file = filename + ".tmp"
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_file, filename)  # ghi xong mới thay thế file gốc


# ------------------ Main ------------------
def main():
    # ✅ Load dữ liệu cũ từ file song.json
    existing = load_existing("songs_dedup.json")

    seen = set()
    for e in existing:
        name = e.get("name", "")
        artist = e.get("artist", "")
        # nếu artist là list thì nối lại thành chuỗi
        if isinstance(artist, list):
            artist = " & ".join(artist)
        seen.add((str(name).lower(), str(artist).lower()))

    print(f"🔹 Đang load: {len(existing)} bản ghi từ song.json")

    # Lấy top tracks
    try:
        top = lastfm_top_tracks_random(TOP_LIMIT)
    except Exception as e:
        print("❌ Failed to fetch top tracks from Last.fm:", e)
        return

    for raw_title, raw_artist in top:
        title = normalize_title_artist(raw_title)
        artist = normalize_title_artist(raw_artist)
        key = (title.lower(), artist.lower())
        if key in seen:
            print(f"⏭️ Skip (trùng): {title} — {artist}")
            continue

        print(f"🎵 Đang xử lý: {title} — {artist}")

        # 1) Last.fm: tags, summary, duration
        tags, summary, duration_ms = lastfm_track_info(artist, title)
        sleep_jitter()

        # 2) Lyrics
        lyrics = get_full_lyrics(title, artist)
        if not lyrics:
            print(f"⚠️ Không tìm thấy lyrics → bỏ qua")
            continue

        lyrics_en = lyrics
        if not is_likely_english(lyrics):
            lyrics_en = translate_to_english(lyrics)
        sleep_jitter()

        tempo, valence, danceability = estimate_audio_fields(lyrics_en, tags)
        emotion, context = guess_emotion_and_context(lyrics_en, tags)
        if not summary:
            summary = make_summary(title, artist, tags, tempo, emotion)

        item = {
            "name": title,
            "artist": artist,
            "release_date": None,
            "duration": duration_ms,
            "tempo": tempo,
            "valence": valence,
            "danceability": danceability,
            "lyrics": lyrics_en,
            "tags": tags or ["pop"],
            "summary": summary,
            "emotion": emotion,
            "context": context
        }

        existing.append(item)
        seen.add(key)
        save_all("songs_dedup.json", existing)
        print(f"   ✅ Đã thêm mới. Tổng cộng: {len(existing)}")
        sleep_jitter()

    print(f"🎯 Done. Đã lưu {len(existing)} bài vào songs_dedup.json")
# 

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print("❌ Lỗi trong main:", e)
        print("⏳ Chờ 10 giây trước khi chạy tiếp...")
        time.sleep(10)  # nghỉ 30 giây giữa các vòng

# ================== END OF FILE ==================
