# Permissions & Thresholds

## Cost Thresholds

| Action | Threshold | Mode |
|--------|-----------|------|
| Auto-approve limit | $5/item | execute |
| CEO approval required | Above $5/item | draft |
| Monthly AI operations budget | $30/month | monitor |

```yaml
auto_approve_limit: 5  # USD
ceo_approval_above: 5  # USD
monthly_ai_budget: 30    # USD
```

## Hypothesis Validation Gate (required)

The following initiatives require `/validate-hypothesis` before execution.

| Trigger | Mode |
|---------|------|
| New advertising channel | validation required |
| New product or service | validation required |
| New market or customer segment | validation required |
| Recurring cost above threshold | validation required |
| "We use it so it'll sell" assumption | validation required |

Skipping validation requires explicit CEO approval.

```yaml
hypothesis_validation:
  required_triggers:
    - new_ad_channel
    - new_product
    - new_market_segment
    - recurring_cost_above_threshold
    - self_use_assumption
  skip_allowed: ceo_explicit_approval_only
  skill: /validate-hypothesis
```

## Development Thresholds

### Auto-execute (execute)
- Bug fixes (bugfix)
- Minor feature additions (minor_feature)
- Test additions/fixes (test)
- Refactoring (refactor)
- Documentation updates (docs)
- Dependency patches (patch/minor)

### CEO Approval Required (draft)
- New feature development (new_feature)
- Architecture changes (architecture_change)
- Production deployment (deploy_production)
- Major dependency updates (major_update)
- New library/service adoption (new_dependency)
- Database schema changes (schema_change)

```yaml
auto_execute:
  - bugfix
  - minor_feature
  - test
  - refactor
  - docs
  - dependency_patch

ceo_approval:
  - new_feature
  - architecture_change
  - deploy_production
  - major_update
  - new_dependency
  - schema_change
```

## External Communication

### Always Draft (CEO review required)
- Press releases (press_release)
- Pricing change announcements (pricing_change)
- Complaint/claim responses (claim_response)
- Client proposals (proposal)
- Contracts and NDAs (contract)
- Invoices (invoice)

### Auto-execute After Approval
- Scheduled social posts (scheduled_sns) -- using approved templates
- FAQ/standard responses (faq_response) -- using approved templates
- Technical articles (tech_article) -- after review

### Auto-execute (read-only)
- Analytics reports (analytics_report)
- KPI dashboard updates (kpi_update)
- Competitive analysis (competitor_analysis)
- Internal documentation (internal_docs)

```yaml
always_draft:
  - press_release
  - pricing_change
  - claim_response
  - proposal
  - contract
  - invoice

auto_after_approval:
  - scheduled_sns
  - faq_response
  - tech_article

auto_execute_readonly:
  - analytics_report
  - kpi_update
  - competitor_analysis
  - internal_docs
```

## Deployment Permissions

| Environment | Mode | Notes |
|-------------|------|-------|
| Local dev | execute | Free to run |
| Staging | execute | Auto-deploy allowed |
| Production | draft | CEO approval before deploy |

```yaml
deploy:
  local: execute
  staging: execute
  production: draft
```

## Email Permissions

| Type | Mode | Notes |
|------|------|-------|
| Internal notifications | execute | Auto-send |
| Client communication | draft | CEO review before send |
| Marketing emails | draft | CEO review before send |
| System notifications (auto) | execute | Approved templates only |

```yaml
email:
  internal_notification: execute
  client_communication: draft
  marketing_email: draft
  system_notification: execute
```

## Escalation Rules

1. Auto-execute task fails 3 consecutive times -> CEO notification
2. Budget reaches 80% -> CEO notification
3. Security incident suspected -> Immediate CEO notification
4. Customer complaint received -> Immediate CEO notification

---

## MoGood 適用注記（2026-08-17 追加・上記より優先）

未ローンチ・従業員なしの学生プロジェクトであるため、上記のうち以下は読み替える。

| 上記の項目 | MoGood での扱い |
|---|---|
| Invoices / Client communication / Marketing emails | **対象なし**（顧客・請求は存在しない） |
| Staging: execute / Production: draft | ストア公開前のため対象なし。ローカル実行のみ execute |
| Press releases / Pricing change | 対象なし（未ローンチ） |
| Monthly AI budget $30 | 有効。80%到達で CEO に通知 |

**追加で必ず draft にするもの**

1. グランプリ応募書類・提出物の確定版
2. 外部の人に渡すもの全般（アンケート配布文面、ヒアリング依頼文、SNS投稿）
3. 有料APIの利用条件を変える判断（モデル変更・呼び出し回数の増加）
4. `docs/instruction.md` の確定事項・禁止事項の変更提案
5. `docs/` 配下の既存ファイルの書き換え（差分を提示して承認を得る）

**Phase ゲート**: `docs/instruction.md` §6 の検証3項目が未通過の間、アプリ本体の実装・レコメンド高度化は auto-execute にしない（着手自体が CEO 判断）。
