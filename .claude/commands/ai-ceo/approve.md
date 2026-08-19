---
description: 承認待ちアイテムを承認する
argument-hint: <AQ-ID>
---
承認対象: $ARGUMENTS

CLAUDE.md の「Approval Rules」に従う。
1. `.company/approval-queue.md` から該当 ID のアイテムを確認し、内容を要約して提示する
2. `.company/approval-queue.md` から Pending を削除し、Recent Approvals へ移す
3. `.company/decisions/{今月}.md` に決定・理由・影響範囲を追記する
4. 実行が伴う場合は、実行内容を明示してから実行する（外部発信は `.company/steering/permissions.md` の閾値に従う）
