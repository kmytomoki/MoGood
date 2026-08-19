from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
SAMPLES_DIR = ROOT / "samples"
GROUND_TRUTH_PATH = SAMPLES_DIR / "ground_truth.json"


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        r"C:\Windows\Fonts\msgothic.ttc",
        r"C:\Windows\Fonts\meiryo.ttc",
        r"C:\Windows\Fonts\YuGothM.ttc",
        r"C:\Windows\Fonts\arial.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                pass
    return ImageFont.load_default()


def build_samples() -> list[dict[str, Any]]:
    # 実運用で見かける揺れを軽く混ぜる（税表記・単位・内容量表記）
    return [
        {"product_name": "豚こま切れ", "price_yen": 398, "quantity_value": 500, "quantity_unit": "g", "tax_included": None, "price_text": "398円"},
        {"product_name": "鶏むね肉", "price_yen": 430, "quantity_value": 480, "quantity_unit": "g", "tax_included": True, "price_text": "税込430円"},
        {"product_name": "牛乳", "price_yen": 228, "quantity_value": 1.0, "quantity_unit": "L", "tax_included": True, "price_text": "税込 228円"},
        {"product_name": "ヨーグルト", "price_yen": 178, "quantity_value": 400, "quantity_unit": "g", "tax_included": None, "price_text": "178 円"},
        {"product_name": "卵", "price_yen": 298, "quantity_value": 10, "quantity_unit": "個", "tax_included": None, "price_text": "298円"},
        {"product_name": "スライスチーズ", "price_yen": 248, "quantity_value": 8, "quantity_unit": "枚", "tax_included": False, "price_text": "税抜248円"},
        {"product_name": "豆乳", "price_yen": 178, "quantity_value": 1000, "quantity_unit": "ml", "tax_included": None, "price_text": "178JPY"},
        {"product_name": "トマト缶", "price_yen": 128, "quantity_value": 400, "quantity_unit": "g", "tax_included": None, "price_text": "128円"},
        {"product_name": "鮭フレーク", "price_yen": 258, "quantity_value": 120, "quantity_unit": "g", "tax_included": True, "price_text": "税込258円"},
        {"product_name": "ミネラルウォーター", "price_yen": 98, "quantity_value": 2.0, "quantity_unit": "L", "tax_included": None, "price_text": "98円"},
    ]


def quantity_text(v: float, unit: str) -> str:
    if float(v).is_integer():
        return f"{int(v)}{unit}"
    return f"{v}{unit}"


def draw_tag(sample: dict[str, Any], out_path: Path) -> None:
    img = Image.new("RGB", (900, 520), color=(250, 248, 241))
    draw = ImageDraw.Draw(img)

    title_font = load_font(56)
    body_font = load_font(44)
    small_font = load_font(30)

    draw.rectangle((30, 30, 870, 490), outline=(20, 20, 20), width=4)
    draw.rectangle((30, 30, 870, 100), fill=(235, 233, 226))
    draw.text((50, 44), "お買い得", fill=(30, 30, 30), font=small_font)
    draw.text((50, 130), sample["product_name"], fill=(15, 15, 15), font=title_font)
    draw.text((50, 240), f"内容量: {quantity_text(sample['quantity_value'], sample['quantity_unit'])}", fill=(20, 20, 20), font=body_font)
    draw.text((50, 330), f"価格: {sample['price_text']}", fill=(180, 20, 20), font=title_font)

    # OCR揺れ用のノイズテキスト（小さめ）
    noise = random.choice(["本日限り", "広告の品", "数量限定", "売り切れ御免"])
    draw.text((620, 450), noise, fill=(60, 60, 60), font=small_font)

    img.save(out_path)


def main() -> None:
    random.seed(42)
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    for png in SAMPLES_DIR.glob("sample_*.png"):
        png.unlink()

    samples = build_samples()
    gt: list[dict[str, Any]] = []
    for idx, sample in enumerate(samples, start=1):
        filename = f"sample_{idx:02d}.png"
        out_path = SAMPLES_DIR / filename
        draw_tag(sample, out_path)
        row = {
            "image": filename,
            "product_name": sample["product_name"],
            "price_yen": sample["price_yen"],
            "quantity_value": sample["quantity_value"],
            "quantity_unit": sample["quantity_unit"],
            "tax_included": sample["tax_included"],
        }
        gt.append(row)

    GROUND_TRUTH_PATH.write_text(json.dumps(gt, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Generated {len(gt)} samples at: {SAMPLES_DIR}")
    print(f"Ground truth: {GROUND_TRUTH_PATH}")


if __name__ == "__main__":
    main()
