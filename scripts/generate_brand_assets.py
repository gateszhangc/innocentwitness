from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent.parent
ASSET_DIR = ROOT / "assets" / "brand"
BRAND_DIR = ROOT / "brand"
SKILL_FONT_DIR = Path("/Users/a1-6/.codex/skills/canvas-design/canvas-fonts")

COLORS = {
    "paper": "#f6f1e7",
    "paper_warm": "#eadfce",
    "ink": "#111111",
    "charcoal": "#23201d",
    "amber": "#a25b2e",
    "teal": "#506f73",
    "mist": "#d8d4ce",
}


def ensure_dirs():
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    BRAND_DIR.mkdir(parents=True, exist_ok=True)


def font(path_name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(SKILL_FONT_DIR / path_name), size=size)


def system_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype("/System/Library/Fonts/Hiragino Sans GB.ttc", size=size)


def blend(color: str, alpha: int) -> tuple[int, int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def draw_mark(size: int, background: str, transparent: bool = False) -> Image.Image:
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0) if transparent else COLORS[background])
    draw = ImageDraw.Draw(image)
    pad = int(size * 0.08)
    cx = cy = size // 2
    outer = [pad, pad, size - pad, size - pad]
    draw.rounded_rectangle((0, 0, size, size), radius=int(size * 0.22), fill=COLORS[background])
    draw.ellipse(outer, outline=COLORS["mist"], width=max(2, size // 60))
    draw.ellipse(
        [pad + size * 0.09, pad + size * 0.09, size - pad - size * 0.09, size - pad - size * 0.09],
        outline=blend(COLORS["teal"], 180),
        width=max(2, size // 100),
    )
    draw.arc(
        [pad + size * 0.19, pad + size * 0.12, size - pad - size * 0.04, size - pad - size * 0.18],
        start=204,
        end=22,
        fill=blend(COLORS["amber"], 255),
        width=max(4, size // 48),
    )
    draw.arc(
        [pad + size * 0.08, pad + size * 0.23, size - pad - size * 0.17, size - pad + size * 0.03],
        start=150,
        end=338,
        fill=blend(COLORS["teal"], 255),
        width=max(3, size // 58),
    )
    slit_w = int(size * 0.14)
    slit_h = int(size * 0.58)
    slit_box = [cx - slit_w // 2, cy - slit_h // 2, cx + slit_w // 2, cy + slit_h // 2]
    draw.rounded_rectangle(slit_box, radius=slit_w // 2, fill=COLORS["paper"])
    draw.rounded_rectangle(
        [slit_box[0] + size * 0.02, slit_box[1] + size * 0.08, slit_box[2] - size * 0.02, slit_box[3] - size * 0.08],
        radius=max(2, slit_w // 3),
        outline=blend(COLORS["charcoal"], 200),
        width=max(2, size // 120),
    )
    dot_r = int(size * 0.045)
    draw.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r], fill=COLORS["amber"])
    return image


def save_mark_assets():
    mark = draw_mark(1024, "ink")
    mark.save(ASSET_DIR / "logo-mark.png")

    favicon = draw_mark(256, "ink")
    favicon.save(ASSET_DIR / "favicon.png")
    favicon.save(ASSET_DIR / "favicon.ico")

    apple = draw_mark(180, "paper")
    apple.save(ASSET_DIR / "apple-touch-icon.png")


def save_wordmark():
    image = Image.new("RGBA", (1600, 420), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    mark = draw_mark(256, "ink")
    image.alpha_composite(mark, (32, 82))

    title_font = system_font(112)
    latin_font = font("BigShoulders-Regular.ttf", 66)
    note_font = font("IBMPlexMono-Regular.ttf", 28)

    draw.text((328, 78), "無垢なる証人", fill=COLORS["ink"], font=title_font)
    draw.text((336, 222), "INNOCENT WITNESS", fill=COLORS["amber"], font=latin_font)
    draw.text((340, 304), "EDITORIAL KEYWORD ARCHIVE", fill=COLORS["teal"], font=note_font)
    image.save(ASSET_DIR / "logo-wordmark.png")


def save_social_card():
    width, height = 1200, 630
    image = Image.new("RGBA", (width, height), COLORS["paper"])
    draw = ImageDraw.Draw(image)

    for index in range(0, width, 64):
        draw.line((index, 0, index, height), fill=blend(COLORS["ink"], 18), width=1)
    for index in range(0, height, 64):
        draw.line((0, index, width, index), fill=blend(COLORS["ink"], 18), width=1)

    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((730, -80, 1260, 450), fill=blend(COLORS["amber"], 42))
    glow_draw.ellipse((-120, 240, 380, 760), fill=blend(COLORS["teal"], 36))
    image = Image.alpha_composite(image, glow.filter(ImageFilter.GaussianBlur(26)))

    draw = ImageDraw.Draw(image)
    card = draw_mark(340, "ink")
    image.alpha_composite(card, (785, 142))

    draw.rounded_rectangle((70, 64, width - 70, height - 64), radius=42, outline=blend(COLORS["ink"], 90), width=2)
    draw.arc((122, 120, 1060, 670), start=192, end=348, fill=blend(COLORS["teal"], 170), width=5)
    draw.arc((274, 20, 1124, 520), start=180, end=6, fill=blend(COLORS["amber"], 160), width=4)

    title_font = system_font(96)
    subtitle_font = font("BigShoulders-Regular.ttf", 58)
    copy_font = font("InstrumentSans-Regular.ttf", 34)
    mono_font = font("IBMPlexMono-Regular.ttf", 24)

    draw.text((106, 120), "無垢なる証人", fill=COLORS["ink"], font=title_font)
    draw.text((112, 256), "INNOCENT WITNESS", fill=COLORS["amber"], font=subtitle_font)
    copy = "2019年映画と2026年ドラマ版を一枚で整理する\n非公式キーワードガイド"
    draw.multiline_text((112, 340), copy, fill=COLORS["ink"], font=copy_font, spacing=14)
    draw.text((114, 520), "2019 FILM / 2026 TV ASAHI DRAMA / EDITORIAL ARCHIVE", fill=COLORS["teal"], font=mono_font)

    image.convert("RGB").save(ASSET_DIR / "social-card.png", quality=95)


def save_philosophy():
    philosophy = """# Muted Testimony

Muted Testimony treats space like a chamber where attention gathers before language does. The composition favors measured intervals, concentric traces, and quiet asymmetry so the eye feels guided by procedure without being trapped by rigid bureaucracy. Every element should look meticulously crafted, as if it were adjusted over countless hours by someone with deep expertise in both graphic restraint and emotional timing.

The palette moves between paper warmth, courtroom charcoal, oxidized teal, and a restrained amber accent. These colors should never compete for spectacle. Instead, they create the feeling of evidence laid carefully on a table: calm, forensic, and painfully deliberate. Surfaces must feel labored over with painstaking attention, balancing institutional weight against human softness through exact tonal calibration.

Scale should carry meaning through contrast rather than decoration. Large circular structures and elongated vertical forms imply scrutiny, witnessing, and private resolve, while the smallest marks function like signals discovered only after extended viewing. This hierarchy must feel masterfully composed, the product of repeated refinements rather than spontaneous gesture.

Typography, when present, is sparse and treated as material. Words are not explanatory paragraphs; they are inscriptions, labels, or fragments that sit inside the structure with the same seriousness as line and shape. The final work should appear meticulously crafted at every edge, as though each letter spacing and baseline were resolved by a designer operating at the top of the field.

The overall object should feel like an artifact from an imagined archive: reverent, exacting, and quietly severe. Nothing should look casual. Craftsmanship has to be visible in the discipline of the margins, the patience of repeated geometry, and the sense that the piece could withstand prolonged scrutiny because it was built with master-level execution and relentless care.
"""
    (BRAND_DIR / "muted-testimony-philosophy.md").write_text(philosophy, encoding="utf-8")


def main():
    ensure_dirs()
    save_mark_assets()
    save_wordmark()
    save_social_card()
    save_philosophy()


if __name__ == "__main__":
    main()
