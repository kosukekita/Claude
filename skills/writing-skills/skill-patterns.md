# Skill Patterns

スキル設計で効果的なパターン集。ユースケースに合わせて適切なパターンを選択。

## Pattern 1: Sequential Workflow Orchestration

**使用場面:** マルチステッププロセスを特定の順序で実行する必要がある場合

### 例: 新規顧客オンボーディング

```markdown
## Workflow: Onboard New Customer

### Step 1: Create Account
Call MCP tool: `create_customer`
Parameters: name, email, company

### Step 2: Setup Payment
Call MCP tool: `setup_payment_method`
Wait for: payment method verification

### Step 3: Create Subscription
Call MCP tool: `create_subscription`
Parameters: plan_id, customer_id (from Step 1)

### Step 4: Send Welcome Email
Call MCP tool: `send_email`
Template: welcome_email_template
```

### Key Techniques

- **明示的なステップ順序**: 各ステップを番号付きで記述
- **ステップ間の依存関係**: 前のステップの出力を次のステップで使用
- **各段階でのバリデーション**: 次に進む前に確認
- **失敗時のロールバック指示**: エラー発生時の対処法を明記

---

## Pattern 2: Multi-MCP Coordination

**使用場面:** ワークフローが複数のサービスにまたがる場合

### 例: デザインから開発へのハンドオフ

```markdown
### Phase 1: Design Export (Figma MCP)
1. Export design assets from Figma
2. Generate design specifications
3. Create asset manifest

### Phase 2: Asset Storage (Drive MCP)
1. Create project folder in Drive
2. Upload all assets
3. Generate shareable links

### Phase 3: Task Creation (Linear MCP)
1. Create development tasks
2. Attach asset links to tasks
3. Assign to engineering team

### Phase 4: Notification (Slack MCP)
1. Post handoff summary to #engineering
2. Include asset links and task references
```

### Key Techniques

- **明確なフェーズ分離**: 各MCPごとにフェーズを分ける
- **MCP間のデータ受け渡し**: 前フェーズの出力を次フェーズへ
- **次フェーズに進む前のバリデーション**: 各フェーズ完了を確認
- **一元的なエラーハンドリング**: どのMCPでエラーが起きても対処可能に

---

## Pattern 3: Iterative Refinement

**使用場面:** 出力品質がイテレーションで改善される場合

### 例: レポート生成

```markdown
## Iterative Report Creation

### Initial Draft
1. Fetch data via MCP
2. Generate first draft report
3. Save to temporary file

### Quality Check
1. Run validation script: `scripts/check_report.py`
2. Identify issues:
   - Missing sections
   - Inconsistent formatting
   - Data validation errors

### Refinement Loop
1. Address each identified issue
2. Regenerate affected sections
3. Re-validate
4. Repeat until quality threshold met

### Finalization
1. Apply final formatting
2. Generate summary
3. Save final version
```

### Key Techniques

- **明示的な品質基準**: 何をもって「完了」とするか定義
- **イテレーティブな改善**: ループで品質向上
- **バリデーションスクリプト**: 自動チェックで一貫性確保
- **停止条件の明確化**: 無限ループを防ぐ

---

## Pattern 4: Context-aware Tool Selection

**使用場面:** 同じ成果を異なるツールで達成する場合

### 例: スマートファイルストレージ

```markdown
## Smart File Storage

### Decision Tree
1. Check file type and size
2. Determine best storage location:
   - Large files (>10MB): Use cloud storage MCP
   - Collaborative docs: Use Notion/Docs MCP
   - Code files: Use GitHub MCP
   - Temporary files: Use local storage

### Execute Storage
Based on decision:
- Call appropriate MCP tool
- Apply service-specific metadata
- Generate access link

### Provide Context to User
Explain why storage was chosen
```

### Key Techniques

- **明確な判断基準**: どの条件でどのツールを使うか
- **フォールバックオプション**: 主要ツールが使えない場合の代替
- **選択の透明性**: なぜそのツールを選んだかユーザーに説明

---

## Pattern 5: Domain-specific Intelligence

**使用場面:** スキルがツールアクセス以上の専門知識を追加する場合

### 例: 金融コンプライアンス

```markdown
## Payment Processing with Compliance

### Before Processing (Compliance Check)
1. Fetch transaction details via MCP
2. Apply compliance rules:
   - Check sanctions lists
   - Verify jurisdiction allowances
   - Assess risk level
3. Document compliance decision

### Processing
IF compliance passed:
  - Call payment processing MCP tool
  - Apply appropriate fraud checks
  - Process transaction
ELSE:
  - Flag for review
  - Create compliance case

### Audit Trail
- Log all compliance checks
- Record processing decisions
- Generate audit report
```

### Key Techniques

- **ロジックに組み込まれたドメイン専門知識**: 業界固有のルールを埋め込み
- **アクション前のコンプライアンス**: 処理前にチェック
- **包括的なドキュメント**: 監査証跡を残す
- **明確なガバナンス**: 判断基準を明示

---

## Approach Selection: Problem-first vs Tool-first

Home Depotで考える。問題を抱えて来店し、適切なツールを案内されるか、ツールを持っていて最適な使い方を教わるか。

### Problem-first
「プロジェクトワークスペースをセットアップしたい」
→ スキルが適切なMCP呼び出しを正しい順序でオーケストレーション
→ ユーザーは成果を記述し、スキルがツールを扱う

### Tool-first
「Notion MCPを接続した」
→ スキルがClaudeに最適なワークフローとベストプラクティスを教える
→ ユーザーはアクセスを持ち、スキルが専門知識を提供

ほとんどのスキルはどちらかに偏る。どちらのフレーミングがユースケースに合うかで適切なパターンを選択。
