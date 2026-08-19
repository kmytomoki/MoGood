---
description: 承認待ちアイテムを理由付きで却下する
argument-hint: <AQ-ID> "理由"
---
却下対象と理由: $ARGUMENTS

CLAUDE.md の「Approval Rules」に従う。
1. `.company/approval-queue.md` から該当アイテムを削除する
2. `.company/decisions/{今月}.md` に却下理由と代替方針を記録する
3. 担当部門の `STATE.md` に差し戻しメモを残す
