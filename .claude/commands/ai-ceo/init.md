---
description: AI-CEO 初期セットアップ。ヒアリングして .company/ の初期ファイル群を生成する
---
CLAUDE.md の「/ai-ceo:init Flow」に従って初期化する。

**MoGood では初期ファイルは既に生成済み**（`.company/VISION.md` / `STATE.md` / `ROADMAP.md` / `products/mogood/STATE.md` / `departments/*/STATE.md`）。
したがって、このコマンドは次のように振る舞うこと:

1. 既存の `.company/` 配下を読み、内容が現状と合っているかを確認する
2. `docs/instruction.md`・`docs/バージョン履歴.md`・`docs/事業プラン草案.md` と矛盾がある箇所だけを指摘する
3. CEO の承認を得てから該当ファイルを更新する（全ファイルの再生成はしない）

最後に `/ai-ceo:status` 相当のサマリーを日本語で表示する。
