# Company Policies

## Security Policy

### Access Management
- No direct production environment access (CI/CD only)
- All API keys and secrets managed via environment variables
- Security rules configured with least-privilege principle
- Separate personal and business accounts

### Data Protection
- Encrypt stored personal information
- Never leak client confidential information (including AI inputs)
- Regular backups with verification
- Proper deletion of unneeded data

### Security Reviews
- Conduct regular security reviews (monthly)
- Automate dependency vulnerability checks (Dependabot / npm audit / etc.)
- Complete security checklist before production deployment

## Quality Management Policy

### Code Review
- All code changes go through pull requests
- AI-generated code follows the same review process
- PRs with failing tests are not merged

### Deliverable Review
- External communications (email, social, press) require CEO approval
- Invoices and contracts require CEO review before sending
- Technical articles undergo fact-checking before publication

### Testing
- New features must include tests
- Automate regression tests
- Staging tests in production-equivalent environment

## Cost Management Policy

### AI Operations
- Monthly AI cost review, stay within $30/month
- Alert when costs reach 80% of budget
- Monthly review for cost reduction opportunities

### Infrastructure
- Maximize free tiers and low-cost plans
- Paid plan upgrades require CEO decision (include cost-benefit analysis)
- Periodic cleanup of unused resources

### External Services
- New service contracts require CEO approval
- Validate with monthly plan before committing to annual
- Quarterly review of low-usage services

## Development Process Policy

### Branch Strategy
- `main` branch always deployable
- Feature development on `feature/` branches
- Hotfixes on `hotfix/` branches

### Deployment
- Complete staging tests before production deploy
- Production deploys in draft mode (CEO approval to execute)
- Always have rollback procedures ready

### Incident Response
- Report production incidents to CEO immediately
- Identify impact scope and rollback if necessary
- Create post-mortem after every incident

## Compliance Policy

### Data Privacy
- Post privacy policy on all products
- Comply with applicable data protection laws (GDPR, CCPA, etc.)
- Implement proper cookie consent where required

### Intellectual Property
- Comply with OSS licenses
- Do not use third-party copyrighted material without permission
- Clearly license your own code

### Contracts
- Client contracts in written form
- NDAs as needed
- Contract changes require mutual agreement

---

## MoGood 適用注記（2026-08-17 追加・上記より優先）

- **プルリクエスト / CI / ステージング**: 本プロジェクトは現在 git リポジトリではなく、CI もステージング環境もない。上記の branch strategy・PR レビュー・staging テストは Phase 1 で開発リポジトリを立てた時点から適用する。それまでは「変更前に差分を提示する」で代替する。
- **PoC の再現性**: `poc/` `20260713/` `20260714/` は実験の記録である。書き換える場合は変更前に差分を提示し、実測結果の再現性を壊さない。
- **数値の扱い**: 事業計画の数値はすべて仮置き。実測が出るまで断定形で書かない（`.company/steering/brand.md`）。
- **個人情報**: スキャン画像・購入履歴は個人の購買データである。価格データを他ユーザーと共有・公開しない（`docs/instruction.md` 確定事項8）。ベータ配布前にプライバシー方針を固める。
- **AI の役割制限**: 単価・消費量の計算は必ずルールベース＋検算。LLM に丸投げしない（`docs/instruction.md` §8）。
