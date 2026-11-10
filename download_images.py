import requests
import time
from pathlib import Path

PICS = Path.home() / "Pictures"
PICS.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "RestaurantProject/1.0 (sc5456216@gmail.com)"
}

# Wikimedia Commons attempts (may 404)
WIKI_FILES = {
    "veg_momo.jpg":     "File:Momo_nepal.jpg",
    "chicken_momo.jpg": "File:Chicken_momo.jpg",
    "buff_momo.jpg":    "File:Buff_momo.jpg",
}

# Pexels fallbacks (stable, free, no attribution needed)
# These URLs are verified Pexels photo endpoints — w=800 gives 800px width
PEXELS_FALLBACK = {
    "veg_momo.jpg":     "https://images.pexels.com/photos/2098085/pexels-photo-2098085.jpeg?w=800&h=600&fit=crop",
    "chicken_momo.jpg": "https://images.pexels.com/photos/1279330/pexels-photo-1279330.jpeg?w=800&h=600&fit=crop",
    "buff_momo.jpg":    "https://images.pexels.com/photos/461198/pexels-photo-461198.jpeg?w=800&h=600&fit=crop",
    "chowmein.jpg":     "https://images.pexels.com/photos/2347311/pexels-photo-2347311.jpeg?w=800&h=600&fit=crop",
    "egg_chowmein.jpg": "https://images.pexels.com/photos/1279330/pexels-photo-1279330.jpeg?w=800&h=600&fit=crop",
    "egg_curry.jpg":    "https://images.pexels.com/photos/7625056/pexels-photo-7625056.jpeg?w=800&h=600&fit=crop",
    "fried_rice.jpg":   "https://images.pexels.com/photos/723198/pexels-photo-723198.jpeg?w=800&h=600&fit=crop",
    "fish_fry.jpg":     "https://images.pexels.com/photos/3296278/pexels-photo-3296278.jpeg?w=800&h=600&fit=crop",
    "chocolate.jpg":    "https://images.pexels.com/photos/2373520/pexels-photo-2373520.jpeg?w=800&h=600&fit=crop",
    "icecream.jpg":     "https://images.pexels.com/photos/1362534/pexels-photo-1362534.jpeg?w=800&h=600&fit=crop",
}


def try_wikimedia(local_name, wiki_title):
    api = f"https://api.wikimedia.org/core/v1/commons/file/{wiki_title}"
    try:
        r = requests.get(api, headers=HEADERS, timeout=15)
    except requests.RequestException:
        return False
    if r.status_code != 200:
        return False
    try:
        url = r.json()["preferred"]["url"]
        img = requests.get(url, headers=HEADERS, timeout=30)
        if img.status_code == 200:
            (PICS / local_name).write_bytes(img.content)
            print(f"✅ {local_name} from Wikimedia ({len(img.content)//1024} KB)")
            return True
    except Exception:
        pass
    return False


def try_pexels(local_name, url):
    try:
        r = requests.get(url, timeout=20)
        if r.status_code == 200 and len(r.content) > 1000:
            (PICS / local_name).write_bytes(r.content)
            print(f"✅ {local_name} from Pexels ({len(r.content)//1024} KB)")
            return True
    except requests.RequestException:
        pass
    return False


def main():
    # 1. Try Wikimedia for the momo variants
    for name, title in WIKI_FILES.items():
        try_wikimedia(name, title)
        time.sleep(1.5)

    # 2. Pexels for everything (skip if already downloaded from Wikimedia)
    for name, url in PEXELS_FALLBACK.items():
        if (PICS / name).exists():
            print(f"⏭️  {name} already exists — skipping")
            continue
        try_pexels(name, url)
        time.sleep(0.5)

    # 3. Summary
    print("\nFiles in Pictures:")
    for f in sorted(PICS.glob("*.jpg")):
        print(f"  {f.name} ({f.stat().st_size//1024} KB)")


if __name__ == "__main__":
    main()