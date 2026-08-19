# -*- coding: utf-8 -*-
"""
MoGood 買い物アドバイザー（Claude API版・LLM実験用）

Excelのデータ（家庭食材リスト・スーパー食材リスト・レシピリスト）をLLMに渡し、
好みの解釈・商品選択・理由説明をすべてLLMに行わせる構成。

実行すると、作りたい料理名と好みをプロンプトで入力できる。
好みは「安さ最優先だけど国産の肉がいい」のような自然文でOK。
買い物リストには必ず各食材の価格と合計金額が出力される。

実行前に:
  pip install anthropic
  export ANTHROPIC_API_KEY=sk-ant-...
"""

import json
import os

from anthropic import Anthropic

# データ（家庭在庫・スーパー商品・レシピ）はルールベース版と共通（Excelから読込）
from mogood_advisor import HOME_STOCK, SUPERMARKET, RECIPES, TODAY

MODEL = "claude-sonnet-5"

SYSTEM_PROMPT = """\
あなたは買い物支援アプリ「MoGood」のアドバイザーです。
家庭食材リスト・スーパー食材リスト・レシピを与えるので、
指定された料理を作るために何をスーパーで購入すべきかを提案してください。

必ず守るルール:
- 期限切れの家庭在庫は使わない。期限が近い在庫（3日以内）は優先消費を提案する。
- 商品比較は容量×パック数から共通単価（100gあたり等）に換算して行う。
- 利用者の「好み」の自然文を解釈し、それに沿った商品を選ぶ。
- 各購入品に選択理由（単価・産地・健康属性・余りの少なさ等）を1行で付ける。
- 在庫で足りる材料は「購入不要」と明示する。
- 【重要】買い物リストには、購入する各食材の商品名と価格（○○円）を必ず明記し、
  最後に「合計金額: ○○円」を必ず計算して出力すること。価格の記載漏れは不可。
- 期限間近在庫の消費アドバイスを最後に付ける。
"""

def build_user_prompt(dish, preference_text):
    # レシピに関係するカテゴリだけに絞ってLLMに渡す（プロンプト削減・精度向上）
    cats = {c for req in RECIPES[dish] for c in req["categories"]}
    market = [p for p in SUPERMARKET if p["category"] in cats]
    def d(o):  # date を文字列化
        return json.dumps(o, ensure_ascii=False, default=str, indent=1)
    return f"""\
基準日: {TODAY}

## 家庭食材リスト
{d(HOME_STOCK)}

## スーパー食材リスト（この料理に関係する商品のみ抜粋）
{d(market)}

## レシピ（カテゴリ候補の先頭が本来の指定、2番目以降は代替候補）
{d(RECIPES[dish])}

## 依頼
料理「{dish}」を作ります。私の好みは「{preference_text}」です。
スーパーで何を買えばよいか、各商品の価格と合計金額を明示して提案してください。
"""

def advise_llm(dish, preference_text):
    client = Anthropic()  # ANTHROPIC_API_KEY を環境変数から取得
    resp = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_prompt(dish, preference_text)}],
    )
    return resp.content[0].text

if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY を設定してください")

    dish = input(f"作りたい料理名（登録済み: {'、'.join(RECIPES)}）: ").strip()
    if dish not in RECIPES:
        raise SystemExit(f"レシピ未登録です: {dish}（レシピリスト.xlsxに追加できます）")
    pref = input("あなたの好み（自由に記述。例: 安さ優先だけど肉だけは国産がいい）: ").strip()
    if not pref:
        pref = "特にこだわりなし。バランスよく"

    print(f"\n{'='*62}\n● 料理: {dish} ／ 好み: {pref}\n{'='*62}")
    print(advise_llm(dish, pref))
