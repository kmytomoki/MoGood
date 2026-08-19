---
description: 朝のダイジェスト。全部門の状態＋承認待ち＋KPIを日本語でまとめる
---
CLAUDE.md の「/ai-ceo:morning Flow」を実行する。

- 稼働中の部門（`dev` / `marketing` / `sales` / `legal` / `cs`）の `.company/departments/{dept}/STATE.md` を読む
- 休止中の部門（`finance` / `hr` / `publishing` / `consulting` / `tax`）は「休止中」の1行のみで済ませ、詳細は読まない
- `.company/approval-queue.md` と `.company/products/mogood/STATE.md` を読む
- 出力は日本語。CLAUDE.md 記載のダイジェスト書式に従う
- 「今日の推奨アクション」は `docs/AI班_ToDoリスト.md` / `docs/アプリ班_ToDoリスト.md` の未完了項目と整合させる
