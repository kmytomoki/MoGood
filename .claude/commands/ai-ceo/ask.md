---
description: AI経営チームに何でも聞く（Party Mode）
argument-hint: "質問"
---
質問: $ARGUMENTS

関連する部門エージェント（`.claude/agents/`）を必要な分だけ呼び、各視点の見解を短くまとめて日本語で提示する。
- 稼働中部門（dev / marketing / sales / legal / cs / growth / biz-dev / cso / cto / cmo）を優先する
- 意見が対立する場合は対立点を隠さず書き、最後に推奨案を1つ示す
- MoGood の確定事項・禁止事項（`docs/instruction.md`）に反する提案はしない
