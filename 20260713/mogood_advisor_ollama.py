# -*- coding: utf-8 -*-
"""
MoGood 買い物アドバイザー（Ollama版・完全無料のローカルLLM実験用）

Claude API版と同じ実験を、自分のPC上で動くLLM（Ollama）で行う。
APIキー不要・課金なし・データも外部に送信されない。

準備（初回のみ）:
  1. https://ollama.com からOllamaをインストール
  2. モデルを取得:  ollama pull qwen3:8b
     （日本語に強い。PCのメモリが少なければ qwen3:4b でも可）
  3. 実行:  python3 mogood_advisor_ollama.py

標準ライブラリのみ使用（pip install 不要）。
"""

import json
import urllib.request

# データ（家庭在庫・スーパー商品・レシピ）はルールベース版と共通
from mogood_advisor import HOME_STOCK, SUPERMARKET, RECIPES, TODAY

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3:8b"  # 例: "qwen3:4b", "llama3.1:8b", "gemma3:12b" などに変更可

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
- 最後に購入合計金額と、期限間近在庫の消費アドバイスを付ける。
- 回答は日本語で簡潔に。
"""

def build_user_prompt(dish, preference_text):
    def d(o):  # date を文字列化
        return json.dumps(o, ensure_ascii=False, default=str, indent=1)
    return f"""\
基準日: {TODAY}

## 家庭食材リスト
{d(HOME_STOCK)}

## スーパー食材リスト
{d(SUPERMARKET)}

## レシピ
{d(RECIPES[dish])}

## 依頼
料理「{dish}」を作ります。私の好みは「{preference_text}」です。
スーパーで何を買えばよいか提案してください。
"""

def advise_ollama(dish, preference_text):
    payload = {
        "model": MODEL,
        "stream": True,   # 生成中の文章を逐次表示（無反応に見えるのを防ぐ）
        "think": False,   # qwen3の「思考」を省略して大幅高速化
        "options": {"temperature": 0.2},  # 提案のブレを抑える
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(dish, preference_text)},
        ],
    }
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    # localhost宛の通信がシステムのプロキシ設定を経由すると503等になるため、
    # プロキシを使わないopenerで直接接続する
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        chunks = []
        with opener.open(req, timeout=600) as resp:
            for line in resp:  # ストリーミング: 1行=1JSONチャンク
                data = json.loads(line.decode("utf-8"))
                token = data.get("message", {}).get("content", "")
                if token:
                    print(token, end="", flush=True)
                    chunks.append(token)
        print()
        return "".join(chunks)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise SystemExit(
            f"Ollamaがエラーを返しました（HTTP {e.code}）: {detail}\n"
            f"モデルが未取得の場合は:  ollama pull {MODEL}"
        )
    except urllib.error.URLError as e:
        raise SystemExit(
            f"Ollamaに接続できません（{e}）。\n"
            "Ollamaを起動し、モデル取得済みか確認してください:\n"
            f"  ollama pull {MODEL}"
        )

if __name__ == "__main__":
    # 自然文の好み（定型の3分類に限らず自由に書ける点がLLM版の利点）
    preferences = [
        "とにかく安く済ませたい",
        "健康重視。有機や無添加、国産を選びたい",
        "冷蔵庫の食材をできるだけ使い切りたい。買い物は最小限に",
        "安さ優先だけど、肉だけは国産がいい",  # 複合的な好みの例
    ]
    for pref in preferences:
        print(f"\n{'='*62}\n● 好み: {pref}\n{'='*62}")
        advise_ollama("肉じゃが", pref)  # 生成文はストリーミングで逐次表示される
