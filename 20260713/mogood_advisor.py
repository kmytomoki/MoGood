# -*- coding: utf-8 -*-
"""
MoGood 買い物アドバイザー（ルールベース版・LLM実験用）

家庭食材リストとスーパー食材リストを照合し、指定した料理を作るために
「何をスーパーで買えばよいか」を、個人の好みに応じてアドバイスする。

好み（preference）:
  - price  : 低価格重視（共通単価に換算して最も割安な商品を選ぶ）
  - health : 健康重視（有機・減塩・無添加・国産を優先）
  - stock  : 家庭在庫の効率消費重視（代替食材で在庫を使い切り、買い物と余りを最小化）
"""

from datetime import date, timedelta

TODAY = date(2026, 7, 13)
EXPIRY_WARN_DAYS = 3  # この日数以内に期限が来る食材は「早めに使う」対象

# ----------------------------------------------------------------------
# 1. 家庭食材リスト（冷蔵庫・保存庫の在庫）
#    amount/unit: 残量, expiry: 賞味・消費期限
# ----------------------------------------------------------------------
HOME_STOCK = [
    {"category": "じゃがいも",   "amount": 1,   "unit": "個",  "expiry": date(2026, 7, 22)},
    {"category": "玉ねぎ",       "amount": 2,   "unit": "個",  "expiry": date(2026, 7, 28)},
    {"category": "豚こま切れ",   "amount": 120, "unit": "g",   "expiry": date(2026, 7, 14)},  # 期限間近
    {"category": "牛乳",         "amount": 300, "unit": "ml",  "expiry": date(2026, 7, 15)},  # 期限間近
    {"category": "卵",           "amount": 4,   "unit": "個",  "expiry": date(2026, 7, 24)},
    {"category": "醤油",         "amount": 200, "unit": "ml",  "expiry": date(2027, 1, 10)},
    {"category": "みりん",       "amount": 100, "unit": "ml",  "expiry": date(2026, 12, 1)},
    {"category": "砂糖",         "amount": 500, "unit": "g",   "expiry": date(2028, 1, 1)},
]

# ----------------------------------------------------------------------
# 2. スーパー食材リスト
#    容量(size)・パック数(packs)・産地(origin)・健康属性(health_tags)に
#    バリエーションを持たせている
# ----------------------------------------------------------------------
SUPERMARKET = [
    # --- じゃがいも ---
    {"category": "じゃがいも", "name": "じゃがいも バラ1個",        "price": 58,   "size": 1,   "unit": "個", "packs": 1, "origin": "北海道産", "health_tags": []},
    {"category": "じゃがいも", "name": "じゃがいも 3個袋",          "price": 148,  "size": 3,   "unit": "個", "packs": 1, "origin": "北海道産", "health_tags": []},
    {"category": "じゃがいも", "name": "じゃがいも 徳用6個袋",      "price": 258,  "size": 6,   "unit": "個", "packs": 1, "origin": "アメリカ産", "health_tags": []},
    # --- にんじん ---
    {"category": "にんじん",   "name": "にんじん バラ1本",          "price": 68,   "size": 1,   "unit": "本", "packs": 1, "origin": "千葉県産", "health_tags": []},
    {"category": "にんじん",   "name": "にんじん 3本袋",            "price": 158,  "size": 3,   "unit": "本", "packs": 1, "origin": "千葉県産", "health_tags": []},
    {"category": "にんじん",   "name": "有機にんじん 2本袋",        "price": 228,  "size": 2,   "unit": "本", "packs": 1, "origin": "熊本県産", "health_tags": ["有機"]},
    # --- 玉ねぎ ---
    {"category": "玉ねぎ",     "name": "玉ねぎ バラ1個",            "price": 48,   "size": 1,   "unit": "個", "packs": 1, "origin": "兵庫県産", "health_tags": []},
    {"category": "玉ねぎ",     "name": "玉ねぎ 3個袋",              "price": 128,  "size": 3,   "unit": "個", "packs": 1, "origin": "ニュージーランド産", "health_tags": []},
    # --- 牛肉 ---
    {"category": "牛肉",       "name": "国産牛切り落とし 200g",     "price": 598,  "size": 200, "unit": "g",  "packs": 1, "origin": "国産",     "health_tags": []},
    {"category": "牛肉",       "name": "豪州産牛切り落とし 300g",   "price": 698,  "size": 300, "unit": "g",  "packs": 1, "origin": "豪州産",   "health_tags": []},
    {"category": "牛肉",       "name": "米国産牛切り落とし 250g×2", "price": 998,  "size": 250, "unit": "g",  "packs": 2, "origin": "米国産",   "health_tags": []},
    # --- 豚肉 ---
    {"category": "豚こま切れ", "name": "国産豚こま切れ 250g",       "price": 348,  "size": 250, "unit": "g",  "packs": 1, "origin": "国産",     "health_tags": []},
    {"category": "豚こま切れ", "name": "カナダ産豚こま切れ 500g",   "price": 598,  "size": 500, "unit": "g",  "packs": 1, "origin": "カナダ産", "health_tags": []},
    {"category": "豚こま切れ", "name": "無添加飼育豚こま 200g",     "price": 428,  "size": 200, "unit": "g",  "packs": 1, "origin": "鹿児島県産", "health_tags": ["無添加"]},
    # --- しらたき ---
    {"category": "しらたき",   "name": "しらたき 1袋",              "price": 98,   "size": 1,   "unit": "袋", "packs": 1, "origin": "国産",     "health_tags": []},
    {"category": "しらたき",   "name": "しらたき 2袋パック",        "price": 178,  "size": 1,   "unit": "袋", "packs": 2, "origin": "国産",     "health_tags": []},
    # --- 調味料 ---
    {"category": "醤油",       "name": "濃口醤油 1L",               "price": 298,  "size": 1000,"unit": "ml", "packs": 1, "origin": "国内製造", "health_tags": []},
    {"category": "醤油",       "name": "減塩醤油 500ml",            "price": 328,  "size": 500, "unit": "ml", "packs": 1, "origin": "国内製造", "health_tags": ["減塩"]},
    {"category": "醤油",       "name": "有機丸大豆醤油 500ml",      "price": 498,  "size": 500, "unit": "ml", "packs": 1, "origin": "国内製造", "health_tags": ["有機", "無添加"]},
]

# ----------------------------------------------------------------------
# 3. レシピ定義
#    categories: 許容する食材カテゴリ（先頭が本来の指定、以降は代替候補）
# ----------------------------------------------------------------------
RECIPES = {
    "肉じゃが": [
        {"ingredient": "じゃがいも", "categories": ["じゃがいも"],          "amount": 3,  "unit": "個"},
        {"ingredient": "玉ねぎ",     "categories": ["玉ねぎ"],              "amount": 1,  "unit": "個"},
        {"ingredient": "にんじん",   "categories": ["にんじん"],            "amount": 1,  "unit": "本"},
        {"ingredient": "肉",         "categories": ["牛肉", "豚こま切れ"],  "amount": 200,"unit": "g"},
        {"ingredient": "しらたき",   "categories": ["しらたき"],            "amount": 1,  "unit": "袋"},
        {"ingredient": "醤油",       "categories": ["醤油"],                "amount": 45, "unit": "ml"},
        {"ingredient": "みりん",     "categories": ["みりん"],              "amount": 30, "unit": "ml"},
        {"ingredient": "砂糖",       "categories": ["砂糖"],                "amount": 15, "unit": "g"},
    ],
}

# ----------------------------------------------------------------------
# 4. 補助関数
# ----------------------------------------------------------------------
def usable_stock(category):
    """期限切れでない在庫量を返す"""
    return sum(s["amount"] for s in HOME_STOCK
               if s["category"] == category and s["expiry"] >= TODAY)

def expiring_soon():
    """期限が近い家庭在庫（フードロス警告用）"""
    limit = TODAY + timedelta(days=EXPIRY_WARN_DAYS)
    return [s for s in HOME_STOCK if TODAY <= s["expiry"] <= limit]

def unit_price(p):
    """共通単価: 1単位（g/ml/個/本/袋）あたりの価格"""
    return p["price"] / (p["size"] * p["packs"])

def unit_price_label(p):
    if p["unit"] in ("g", "ml"):
        return f"100{p['unit']}あたり {unit_price(p)*100:.1f}円"
    return f"1{p['unit']}あたり {unit_price(p):.1f}円"

def health_score(p):
    score = 2 * len(p["health_tags"])
    if ("国産" in p["origin"]) or p["origin"].endswith(("県産", "道産", "府産", "都産")) or p["origin"] == "国内製造":
        score += 1
    return score

def candidates(categories):
    return [p for p in SUPERMARKET if p["category"] in categories]

# ----------------------------------------------------------------------
# 5. 好み別の商品選択ロジック
# ----------------------------------------------------------------------
def select_product(cands, need, preference):
    """
    不足量 need を満たす商品を好みに応じて1つ選び、(商品, 理由) を返す。
    容量が不足分に満たない商品は複数個購入を想定せず、1商品で足りるものを優先。
    """
    enough = [p for p in cands if p["size"] * p["packs"] >= need] or cands

    if preference == "price":
        # 共通単価が最安のもの。単価同率なら総額の安いもの
        best = min(enough, key=lambda p: (unit_price(p), p["price"]))
        reason = f"{unit_price_label(best)} と候補中最安"
    elif preference == "health":
        # 健康属性・国産を優先し、同点なら単価で選ぶ
        best = max(enough, key=lambda p: (health_score(p), -unit_price(p)))
        tags = "・".join(best["health_tags"]) or "なし"
        reason = f"健康属性: {tags} / 産地: {best['origin']}"
    elif preference == "stock":
        # 余りが最小になる容量を選ぶ（フードロス最小化）。同点なら安いもの
        best = min(enough, key=lambda p: (p["size"] * p["packs"] - need, p["price"]))
        leftover = best["size"] * best["packs"] - need
        reason = f"必要量{need:g}{best['unit']}に対し余り{leftover:g}{best['unit']}で最小"
    else:
        raise ValueError(f"未知の好み: {preference}")
    return best, reason

# ----------------------------------------------------------------------
# 6. メイン: 購入アドバイス生成
# ----------------------------------------------------------------------
def advise(dish, preference):
    labels = {"price": "低価格重視", "health": "健康重視", "stock": "家庭在庫の効率消費重視"}
    lines = [f"\n{'='*62}", f"● 料理: {dish} ／ 好み: {labels[preference]}", f"{'='*62}"]
    total = 0

    for req in RECIPES[dish]:
        cats = req["categories"]
        need = req["amount"]

        # 在庫消費重視なら代替カテゴリの在庫も積極的に使う
        use_cats = cats if preference == "stock" else cats[:1]
        stock_used = []
        remaining = need
        for c in use_cats:
            s = usable_stock(c)
            if s > 0 and remaining > 0:
                use = min(s, remaining)
                stock_used.append((c, use, req["unit"]))
                remaining -= use
        # 在庫消費重視以外でも、本来カテゴリの在庫は普通に使う
        if preference != "stock" and remaining > 0 and len(cats) > 1:
            pass  # 代替はしない（好みが stock のときのみ代替）

        if remaining <= 0:
            used = "、".join(f"{c}{a:g}{u}" for c, a, u in stock_used)
            lines.append(f"  ○ {req['ingredient']:　<6}: 購入不要（家庭在庫 {used} で充足）")
            continue

        cands = candidates(cats)
        if not cands:
            lines.append(f"  × {req['ingredient']}: スーパーに該当商品なし")
            continue

        best, reason = select_product(cands, remaining, preference)
        total += best["price"]
        stock_note = ""
        if stock_used:
            used = "、".join(f"{c}{a:g}{u}" for c, a, u in stock_used)
            stock_note = f"（在庫 {used} を使用し不足 {remaining:g}{req['unit']} 分を購入）"
        lines.append(f"  ★ {req['ingredient']:　<6}: 「{best['name']}」 {best['price']}円 {stock_note}")
        lines.append(f"      └ 理由: {reason}")

    lines.append(f"\n  ▶ 購入合計: {total}円")

    exp = expiring_soon()
    if exp:
        items = "、".join(f"{s['category']}（{s['expiry'].strftime('%m/%d')}期限）" for s in exp)
        lines.append(f"  ⚠ 期限間近の在庫: {items} → 早めの消費を推奨")
        if preference == "stock":
            lines.append("     今回のレシピでこれらを優先的に使う選択をしています。")
    return "\n".join(lines)

# ----------------------------------------------------------------------
if __name__ == "__main__":
    print("MoGood 買い物アドバイザー（実験）  基準日:", TODAY)
    for pref in ["price", "health", "stock"]:
        print(advise("肉じゃが", pref))
