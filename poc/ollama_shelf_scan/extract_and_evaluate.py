from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from schema import ShelfTagExtraction
from unit_price import compute_unit_price

try:
    from ollama import chat
except ImportError as exc:  # pragma: no cover
    raise SystemExit("ollama package is not installed. Run: pip install -r requirements.txt") from exc


ROOT = Path(__file__).resolve().parent
SAMPLES_DIR = ROOT / "samples"
RESULTS_DIR = ROOT / "results"
GROUND_TRUTH_PATH = SAMPLES_DIR / "ground_truth.json"
SUMMARY_MD_PATH = RESULTS_DIR / "results.md"


def normalize_name(text: str) -> str:
    return "".join(text.strip().lower().split())


def percentile(values: list[float], p: float) -> float:
    if not values:
        return math.nan
    if len(values) == 1:
        return values[0]
    k = (len(values) - 1) * p
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return values[int(k)]
    d0 = values[f] * (c - k)
    d1 = values[c] * (k - f)
    return d0 + d1


def call_ollama(model: str, image_path: Path) -> ShelfTagExtraction:
    prompt = (
        "この画像の値札から、1商品の情報をJSONで抽出してください。"
        "商品名、価格(円の整数)、内容量の値、単位のみを返してください。"
        "不明な場合は最も妥当な値を推定してください。"
    )
    response = chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
                "images": [str(image_path)],
            }
        ],
        format=ShelfTagExtraction.model_json_schema(),
        options={"temperature": 0},
    )

    # ollama-pythonの返却形式差異（dict/object）を吸収
    message = response["message"] if isinstance(response, dict) else response.message
    content = message["content"] if isinstance(message, dict) else message.content
    return ShelfTagExtraction.model_validate_json(content)


def evaluate_one(model: str, row: dict[str, Any]) -> dict[str, Any]:
    image_path = SAMPLES_DIR / row["image"]
    t0 = time.perf_counter()
    error = None
    pred_obj = None

    try:
        pred_obj = call_ollama(model=model, image_path=image_path)
    except ValidationError as exc:
        error = f"validation_error: {exc}"
    except Exception as exc:  # noqa: BLE001
        error = f"runtime_error: {exc}"

    latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)

    if pred_obj is None:
        return {
            "image": row["image"],
            "latency_ms": latency_ms,
            "ok": False,
            "error": error,
            "matches": {
                "product_name": False,
                "price_yen": False,
                "quantity_value": False,
                "quantity_unit": False,
            },
            "prediction": None,
        }

    pred = pred_obj.model_dump()
    matches = {
        "product_name": normalize_name(pred["product_name"]) == normalize_name(row["product_name"]),
        "price_yen": int(pred["price_yen"]) == int(row["price_yen"]),
        "quantity_value": abs(float(pred["quantity_value"]) - float(row["quantity_value"])) < 1e-6,
        "quantity_unit": pred["quantity_unit"] == row["quantity_unit"],
    }

    pred_unit_price = asdict(compute_unit_price(pred["price_yen"], pred["quantity_value"], pred["quantity_unit"]))
    gt_unit_price = asdict(compute_unit_price(row["price_yen"], row["quantity_value"], row["quantity_unit"]))

    return {
        "image": row["image"],
        "latency_ms": latency_ms,
        "ok": all(matches.values()),
        "error": None,
        "matches": matches,
        "prediction": pred,
        "ground_truth": {
            "product_name": row["product_name"],
            "price_yen": row["price_yen"],
            "quantity_value": row["quantity_value"],
            "quantity_unit": row["quantity_unit"],
            "tax_included": row.get("tax_included"),
        },
        "unit_price_pred": pred_unit_price,
        "unit_price_gt": gt_unit_price,
    }


def aggregate(model: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    latencies = sorted(r["latency_ms"] for r in rows)
    totals = len(rows)
    field_keys = ["product_name", "price_yen", "quantity_value", "quantity_unit"]
    field_accuracy = {}
    for key in field_keys:
        field_accuracy[key] = round(
            sum(1 for r in rows if r["matches"][key]) / totals * 100.0,
            2,
        )

    ok_count = sum(1 for r in rows if r["ok"])
    summary = {
        "model": model,
        "sample_count": totals,
        "exact_match_count": ok_count,
        "exact_match_rate_percent": round(ok_count / totals * 100.0, 2),
        "latency_ms": {
            "avg": round(statistics.fmean(latencies), 2),
            "p50": round(percentile(latencies, 0.5), 2),
            "p90": round(percentile(latencies, 0.9), 2),
            "max": round(max(latencies), 2),
        },
        "field_accuracy_percent": field_accuracy,
        "rows": rows,
    }
    return summary


def write_summary_markdown() -> None:
    summaries = []
    for path in sorted(RESULTS_DIR.glob("results_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        summaries.append(data)

    if not summaries:
        SUMMARY_MD_PATH.write_text("# Evaluation Results\n\nNo results yet.\n", encoding="utf-8")
        return

    lines: list[str] = []
    lines.append("# Evaluation Results")
    lines.append("")
    lines.append("| model | samples | exact_match(%) | avg_ms | p90_ms |")
    lines.append("|---|---:|---:|---:|---:|")
    for s in summaries:
        lines.append(
            f"| {s['model']} | {s['sample_count']} | {s['exact_match_rate_percent']} | {s['latency_ms']['avg']} | {s['latency_ms']['p90']} |"
        )
    lines.append("")

    for s in summaries:
        lines.append(f"## {s['model']}")
        lines.append("")
        lines.append("- Field accuracy")
        lines.append(
            f"  - product_name: {s['field_accuracy_percent']['product_name']}%"
        )
        lines.append(f"  - price_yen: {s['field_accuracy_percent']['price_yen']}%")
        lines.append(f"  - quantity_value: {s['field_accuracy_percent']['quantity_value']}%")
        lines.append(f"  - quantity_unit: {s['field_accuracy_percent']['quantity_unit']}%")
        lines.append("")

    SUMMARY_MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Ollama model name")
    args = parser.parse_args()

    if not GROUND_TRUTH_PATH.exists():
        raise SystemExit(f"ground truth not found: {GROUND_TRUTH_PATH}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    gt_rows = json.loads(GROUND_TRUTH_PATH.read_text(encoding="utf-8"))
    evaluated = [evaluate_one(args.model, row) for row in gt_rows]
    summary = aggregate(args.model, evaluated)

    out_file = RESULTS_DIR / f"results_{args.model.replace(':', '_')}.json"
    out_file.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_summary_markdown()

    print(f"Wrote: {out_file}")
    print(f"Wrote: {SUMMARY_MD_PATH}")
    print(f"Exact match rate: {summary['exact_match_rate_percent']}%")
    print(f"Latency avg/p90 (ms): {summary['latency_ms']['avg']} / {summary['latency_ms']['p90']}")


if __name__ == "__main__":
    main()
