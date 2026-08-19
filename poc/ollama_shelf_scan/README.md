# Ollamaローカル検証PoC

`instruction.md` の §6（レイテンシ・読み取り精度）を、ローカルPCだけで先に検証する最小実験です。  
このPoCでは「値札風の疑似画像」を生成して、OllamaのVLMで構造化抽出し、正解データと比較します。

## 前提

- Windows + Python 3.11
- Ollamaインストール済み
- 推奨モデル:
  - `moondream`
  - `qwen2.5vl:3b`

## セットアップ

```powershell
pip install -r poc/ollama_shelf_scan/requirements.txt
```

## 実行手順

1) 疑似値札画像と正解データ生成

```powershell
python poc/ollama_shelf_scan/generate_samples.py
```

2) モデルごとに抽出・評価

```powershell
python poc/ollama_shelf_scan/extract_and_evaluate.py --model moondream
python poc/ollama_shelf_scan/extract_and_evaluate.py --model qwen2.5vl:3b
```

## 出力

- サンプル画像: `poc/ollama_shelf_scan/samples/*.png`
- 正解データ: `poc/ollama_shelf_scan/samples/ground_truth.json`
- 評価結果: `poc/ollama_shelf_scan/results/results_<model>.json`
- 集約Markdown: `poc/ollama_shelf_scan/results/results.md`

## 注記

- 単価計算は `unit_price.py` のルールベースで行い、LLMに計算を任せません。
- 疑似画像は実店舗の難しさ（反射、斜め、手書き等）を再現しないため、実写テストは別途必要です。
