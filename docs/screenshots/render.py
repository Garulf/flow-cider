"""Render the README screenshots and hero image with flow-render.

Usage (from the repo root):

    uv run --no-project --with flow-render==0.15.0 --with pillow python docs/screenshots/render.py

Each ``<shot>.json`` is a flow-render config. A result either names an image in
``icon`` (relative to this folder) or gives two colours in ``cover``, which are
drawn as stand-in album art so no real artwork ends up in the repo.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
SHOTS_DIR = ROOT / "docs" / "screenshots"
ASSETS_DIR = ROOT / ".github" / "assets"
THEMES = ("dark", "light")
HERO = {"shot": "hero", "theme": "dark", "css": ["win11-dark.css", "docs/screenshots/hero.css"]}


def cover_png(colors, out_dir: Path) -> Path:
    top, bottom = (Image.new("RGB", (1, 1), color).getpixel((0, 0)) for color in colors)
    path = out_dir / f"cover-{colors[0].lstrip('#')}-{colors[1].lstrip('#')}.png"
    if not path.exists():
        size = 128
        image = Image.new("RGB", (size, size))
        draw = ImageDraw.Draw(image)
        for y in range(size):
            mix = y / (size - 1)
            draw.line([(0, y), (size, y)], fill=tuple(round(a + (b - a) * mix) for a, b in zip(top, bottom)))
        draw.ellipse((34, 34, 94, 94), outline=(255, 255, 255), width=4)
        draw.ellipse((58, 58, 70, 70), fill=(255, 255, 255))
        image.save(path)
    return path


def flow_render(args, out_path: Path) -> None:
    with tempfile.TemporaryDirectory() as out_dir:
        subprocess.run(["flow-render", *args, "-o", out_dir], check=True, cwd=ROOT)
        (rendered,) = Path(out_dir).glob("*.png")
        shutil.move(str(rendered), out_path)
    print(f"Wrote {out_path}")


def render_config(shot: str, theme: str, css, out_path: Path, work: Path) -> None:
    config = json.loads((SHOTS_DIR / f"{shot}.json").read_text(encoding="utf-8"))
    config["icon"] = str((SHOTS_DIR / config["icon"]).resolve())
    for result in config["results"]:
        if "cover" in result:
            result["icon"] = str(cover_png(result.pop("cover"), work))
        else:
            result["icon"] = str((SHOTS_DIR / result["icon"]).resolve())
    config["css"] = css
    config_path = work / f"{shot}-{theme}.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    flow_render(["-c", str(config_path)], out_path)


def main() -> None:
    shots = sorted(path.stem for path in SHOTS_DIR.glob("*.json") if path.stem != HERO["shot"])
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for shot in shots:
            for theme in THEMES:
                render_config(shot, theme, f"win11-{theme}.css", ASSETS_DIR / f"{shot}-{theme}.png", work)
        render_config(HERO["shot"], HERO["theme"], HERO["css"], ASSETS_DIR / "hero.png", work)


if __name__ == "__main__":
    sys.exit(main())
