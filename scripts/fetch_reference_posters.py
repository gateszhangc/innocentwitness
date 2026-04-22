from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "assets" / "posters"
POSTERS = [
    {
        "name": "movie-poster.webp",
        "url": "https://klockworx.com/wp-content/uploads/2022/10/InnocentWitness_poster.jpg",
        "width": 880,
    },
    {
        "name": "drama-poster.webp",
        "url": "https://www.tv-asahi.co.jp/mukunarushonin/OG.jpg",
        "width": 880,
    },
]


def fetch_image(url: str) -> Image.Image:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=20) as response:
        return Image.open(BytesIO(response.read())).convert("RGB")


def resize(image: Image.Image, width: int) -> Image.Image:
    ratio = width / image.width
    height = round(image.height * ratio)
    return image.resize((width, height), Image.Resampling.LANCZOS)


def main():
    TARGET.mkdir(parents=True, exist_ok=True)
    for item in POSTERS:
        image = fetch_image(item["url"])
        image = resize(image, item["width"])
        image.save(TARGET / item["name"], format="WEBP", quality=82, method=6)


if __name__ == "__main__":
    main()
