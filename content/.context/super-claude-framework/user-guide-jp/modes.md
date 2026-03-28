# SuperClaude 行動モードガイド 🧠

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#superclaude-behavioral-modes-guide-)

## ✅ クイック検証

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#-quick-verification)

コマンドを使用してモードをテストします`/sc:`。モードはタスクの複雑さに基づいて自動的にアクティブになります。コマンドの完全なリファレンスについては、[コマンドガイド](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md)をご覧ください。

## クイックリファレンステーブル

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#quick-reference-table)

|モード|目的|自動トリガー|重要な行動|最適な用途|
|---|---|---|---|---|
|**🧠 ブレインストーミング**|インタラクティブな発見|「ブレインストーミング」、「たぶん」、漠然とした要望|ソクラテス式の質問、要件の抽出|新しいプロジェクトの計画、不明確な要件|
|**🔍 内省**|メタ認知分析|エラー回復、「推論の分析」|透明な思考マーカー（🤔、🎯、💡）|デバッグ、学習、最適化|
|**📋 タスク管理**|複雑な調整|>3ステップ、>2ディレクトリ|相の崩壊、記憶の持続|多段階操作、プロジェクト管理|
|**🎯 オーケストレーション**|インテリジェントなツール選択|複数のツールを使用した操作、高いリソース使用率|最適なツールルーティング、並列実行|複雑な分析、パフォーマンスの最適化|
|**⚡ トークン効率**|圧縮通信|コンテキスト使用率が高い、`--uc`フラグ|シンボルシステム、推定30～50%のトークン削減|リソースの制約、大規模な操作|

---

## はじめに（2分の概要）

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#getting-started-2-minute-overview)

**モードは動作指示を通じてアクティブ化されます**- Claude Code はコンテキスト ファイルを読み取り、タスクのパターンと複雑さに基づいてどのモード動作を採用するかを決定します。

**簡単な例:**

```shell
# Automatic activation examples
/sc:brainstorm "mobile app"        # → Socratic discovery questions
/sc:implement "auth system"        # → Multi-phase coordination  
"--uc analyze large-codebase/"     # → Compressed symbol output
```

**手動フラグを使用する場合:**

- 特定の動作が必要: `--brainstorm`、、`--introspect``--uc`
- 学習/デバッグのための自動検出をオーバーライドする
- 特定の制約（メモリ、時間、明瞭性）に合わせて最適化する

---

## モードの詳細

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#mode-details)

### 🧠 ブレインストーミングモード - インタラクティブな発見

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#-brainstorming-mode---interactive-discovery)

**目的**: 共同作業による発見を通じて、漠然としたアイデアを構造化された要件に変換します。

**自動アクティベーショントリガー:**

- 漠然としたプロジェクトリクエスト:「...を構築したい」、「...を作成しようと考えている」
- 探索キーワード: ブレインストーミング、探索、議論、理解、不明
- 不確実性指標：「たぶん」、「おそらく」、「できるかもしれない」
- 手動フラグ: `--brainstorm`、`--bs`

**行動の変化:**

- **ソクラテス式質問**：隠れた要件を明らかにするために掘り下げた質問をする
- **非推定的アプローチ**：推定を避け、発見の方向性を導く
- **協力的なパートナーシップ**：指示的な相談ではなく、探索的に協力します
- **要件統合**：洞察を構造化された技術概要に変換します
- **クロスセッションメモリ**：フォローアップの議論のために発見のコンテキストを維持する

**経験例:**

```
Standard Approach: "I'll build a user authentication system with JWT tokens..."
Brainstorming Approach: 
"🤔 Let's explore this together:
 - What specific user problems does auth solve for your app?
 - Who are your users and what's their technical comfort level?  
 - Any existing systems or social logins to integrate with?
 - What security/compliance requirements do you have?
 📝 Outcome: Detailed auth requirements brief ready for implementation"
```

#### 成功基準

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#success-criteria)

- [ ] すぐに解決策を提示するのではなく、質問で応答する
- [ ] 質問はユーザーのニーズ、技術的制約、ビジネス目標を探ります
- [ ] 発見プロセス全体を通じて協力的な姿勢を維持する
- [ ] 結果として構造化された要件または技術概要を作成します

**検証:** `/sc:brainstorm "web app"`ユーザー、機能、テクノロジーについて質問する必要があります。  
**テスト:**漠然としたリクエストは、推測ではなく発見のための質問を引き起こす必要があります。  
**チェック:**モードは、同じ会話内のフォローアップの質問でも維持される必要があります。

**最適な組み合わせ:**

- **→ タスク管理**：要件の発見 → 体系的な実装計画
- **→ オーケストレーション**：要件の明確化 → 実装に最適なツールの選択
- **手動オーバーライド**: `--brainstorm`「明確な」要件であっても強制的に検出するために使用します

---

### 🔍 内省モード - メタ認知分析

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#-introspection-mode---meta-cognitive-analysis)

**目的**: 学習の最適化と透明な意思決定のための推論プロセスを公開します。

**自動アクティベーショントリガー:**

- 自己分析の要求：「自分の推論を分析する」、「決定を振り返る」
- エラー回復シナリオと調査を必要とする予期しない結果
- 複数の実行可能なアプローチによる複雑な問題解決
- 最適化の機会のためのパターン認識の必要性
- 手動フラグ:`--introspect`

**行動の変化:**

- **推論の透明性**: 思考プロセスを明確なマーカーで公開します (🤔、🎯、⚡、📊、💡)
- **意思決定分析**：選択ロジックを評価し、代替アプローチを検討する
- **パターン認識**：繰り返される行動と改善の機会を特定します
- **メタ学習**：継続的なフレームワーク改善のための洞察を抽出
- **フレームワークコンプライアンス**: SuperClaude原則と品質ゲートに照らしてアクションを検証します

**経験例:**

```
Standard Approach: "I'll analyze this code structure and suggest improvements..."
Introspective Approach:
"🧠 Meta-Analysis: Why did I choose structural analysis over functional flow?
 🎯 Decision Logic: Saw class hierarchy → assumed OOP pattern dominance
 🔄 Alternative Considered: Data flow analysis might reveal hidden dependencies
 📊 Evidence Check: File imports suggest functional composition, not OOP
 💡 Learning: Need to analyze imports before choosing analysis strategy
 ⚡ Correction: Switching to functional flow analysis approach"
```

**最適な組み合わせ:**

- **→ タスク管理**: 複雑なフェーズの決定に透明な推論を提供します
- **任意のモード**: 他のモードの操作に推論の透明性レイヤーを追加します
- **手動オーバーライド**:`--introspect`学習セッションやワークフローのデバッグに使用します

---

### 📋 タスク管理モード - 複雑な調整

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#-task-management-mode---complex-coordination)

**目的**: 複数ステップの操作のためのセッション永続性を備えた階層的なタスク構成。

**自動アクティベーショントリガー:**

- 3 つ以上の調整されたステップを必要とする操作
- 複数のファイル/ディレクトリ スコープ (ディレクトリが 2 つ以上、またはファイル数が 3 つ以上)
- フェーズとチェックポイントを必要とする複雑な依存関係
- 品質改善の要望：磨き、洗練、強化
- 手動フラグ: `--task-manage`、`--delegate`

**行動の変化:**

- **階層的計画**：複雑な作業を計画→フェーズ→タスク→ToDo構造に分割します
- **セッションの永続性**: 中断があってもプロジェクトのコンテキストと進行状況を維持します
- **メモリ統合**: 状態保存のために write_memory/read_memory を使用する
- **進捗オーケストレーション**: 追跡のためにメモリ更新とTodoWriteを調整する
- **品質ゲート**:フェーズ間の体系的な検証チェックポイントを実装します

**経験例:**

```
Standard Approach: "I'll implement user authentication..." → Direct implementation
Task Management Approach:
"📋 Multi-Phase Implementation Plan:
 🎯 Phase 1: Security Requirements Analysis (Session 1)
 🎯 Phase 2: API Design & Documentation (Session 2)  
 🎯 Phase 3: Implementation & Testing (Session 3-4)
 🎯 Phase 4: Integration & Validation (Session 5)
 💾 Session persistence: Resume context automatically
 ✓ Quality gates: Validation before each phase transition"
```

**最適な組み合わせ:**

- **ブレインストーミング→**：要件発見と体系的な実装
- **+ オーケストレーション**: 最適なツール選択によるタスク調整
- **+ イントロスペクション**：複雑なフェーズの決定のための透過的な推論

---

### 🎯 オーケストレーションモード - インテリジェントなツール選択

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#-orchestration-mode---intelligent-tool-selection)

**目的**: インテリジェントなツールルーティングと並列調整を通じてタスクの実行を最適化します。

**自動アクティベーショントリガー:**

- 高度な調整を必要とするマルチツール操作
- パフォーマンス制約（リソース使用量が多い）
- 並列実行の機会（3つ以上の独立したファイル/操作）
- 複数の有効なツールアプローチによる複雑なルーティング決定

**行動の変化:**

- **インテリジェントツールルーティング**:各タスクタイプに最適なMCPサーバーとネイティブツールを選択します。
- **リソース認識**: システムの制約と可用性に基づいてアプローチを適応させます
- **並列最適化**: 同時実行のための独立した操作を識別します
- **調整の焦点**：調整された実行を通じてツールの選択と使用を最適化します
- **アダプティブフォールバック**: 優先オプションが利用できない場合にツールを適切に切り替えます

**経験例:**

```
Standard Approach: Sequential file-by-file analysis and editing
Orchestration Approach:
"🎯 Multi-Tool Coordination Strategy:
 🔍 Phase 1: Serena (semantic analysis) + Sequential (architecture review)
 ⚡ Phase 2: Morphllm (pattern edits) + Magic (UI components) 
 🧪 Phase 3: Playwright (testing) + Context7 (documentation patterns)
 🔄 Parallel execution: 3 tools working simultaneously
\"
```

**最適な組み合わせ:**

- **タスク管理 →** : 複雑な多段階計画のためのツール調整を提供します
- **+ トークン効率**: 圧縮通信による最適なツール選択
- **複雑なタスク**: インテリジェントなツールルーティングを追加して実行を強化

---

### ⚡ トークン効率モード - 圧縮通信

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#-token-efficiency-mode---compressed-communication)

**目的**: 情報の品質を維持しながら、シンボル システムを通じて推定 30 ～ 50% のトークン削減を実現します。

**自動アクティベーショントリガー:**

- 高いコンテキストの使用が限界に近づいています
- 資源効率が求められる大規模運用
- ユーザー明示フラグ: `--uc`、`--ultracompressed`
- 複数の出力を持つ複雑な分析ワークフロー

**行動の変化:**

- **シンボルコミュニケーション**: ロジックフロー、ステータス、技術ドメインに視覚的なシンボルを使用します
- **技術略語**：繰り返される技術用語のコンテキスト認識圧縮
- **構造化された密度**: 冗長な段落よりも箇条書き、表、簡潔な書式
- **情報保存**: 圧縮しても95%以上の情報品質を維持
- **構造化されたフォーマット**: 明確さとタスクの完了のために整理されています

**経験例:**

```
Standard Approach: "The authentication system implementation shows a security vulnerability in the user validation function that needs immediate attention..."
Token Efficient Approach:
"🛡️ Security Alert:
 auth.js:45 → user val() → critical vuln
 📊 Impact: ❌ token bypass possible
 ⚡ Action: fix validation + audit ∵ high sev
 🔧 Est: 2h impl + 1h test"
```

**最適な組み合わせ:**

- **任意のモード**: モード固有の動作を維持しながら圧縮レイヤーを追加します
- **オーケストレーション →** : 圧縮されたツール調整とステータス更新
- **手動オーバーライド**:`--uc`コンテキストのプレッシャーや効率が優先される場合に使用します

---

### 🎨 標準モード - バランスのとれたデフォルト

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#-standard-mode---balanced-default)

**目的**: 簡単な開発タスクに対して明確でプロフェッショナルなコミュニケーションを提供します。

**自動アクティベーショントリガー:**

- 複雑さの指標のない、シンプルで明確に定義されたタスク
- 明確な要件を備えた単一ファイル操作
- 基本的な説明と標準的な開発ワークフロー
- 他のモードトリガーは検出されません（デフォルトのフォールバック）

**行動の変化:**

- **プロフェッショナルなコミュニケーション**：明確で簡潔な技術用語
- **中程度の詳細**: ほとんどの開発タスクに適したバランスの取れた情報の深さ
- **標準ツール選択**: ネイティブのClaude機能と基本ツールを使用
- **品質重視**: 複雑なオーケストレーションのオーバーヘッドなしでコードの品質を維持
- **応答的な適応**：複雑さが増すと、特化したモードに切り替える準備ができています

**経験例:**

```
Standard Approach: Consistent, professional baseline for all tasks
"I'll implement the login function with proper error handling:
 
 1. Validate user input (email format, password requirements)
 2. Authenticate against database with secure hashing
 3. Generate JWT token with appropriate expiration
 4. Return success response with user data
 
 The implementation will follow security best practices and include comprehensive error handling."
```

**最適な組み合わせ:**

- **→ 任意のモード**: 他のモードを強化する基準として機能します
- **モード切り替え**: 必要に応じて自動的に特殊モードに切り替えます
- **明確さの優先**: 最適化よりも分かりやすいコミュニケーションが重要な場合

---

## 高度な使用法

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#advanced-usage)

### モードの組み合わせ

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#mode-combinations)

**マルチモードワークフロー:**

```shell
# Discovery → Planning → Implementation
/sc:brainstorm "microservices architecture" --task-manage
# → Brainstorming: requirement discovery
# → Task Management: multi-phase coordination

# Analysis with transparency and efficiency
/sc:analyze legacy-system/ --introspect --uc
# → Introspection: transparent reasoning
# → Token Efficiency: compressed output
```

### 手動モード制御

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#manual-mode-control)

**特定の動作を強制する:**

- `--brainstorm`: あらゆるタスクで共同発見を強制
- `--introspect`: あらゆるモードに推論の透明性を追加
- `--task-manage`: 階層的な調整を可能にする
- `--orchestrate`: ツール選択と並列実行を最適化
- `--uc`: 効率化のために通信を圧縮する

**オーバーライドの例:**

```shell
# Force brainstorming on "clear" requirements
/sc:implement "user login" --brainstorm

# Add reasoning transparency to debugging
# 認証問題を透明な推理でデバッグ

# Enable task management for simple operations
# システマチックなタスク管理でスタイルファイルを更新
```

### モードの境界と優先順位

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#mode-boundaries-and-priority)

**モードがアクティブになると:**

1. **複雑さの閾値**: >3ファイル → タスク管理
2. **リソースの圧力**：コンテキスト使用率が高い → トークン効率
3. **複数のツールが必要**: 複雑な分析 → オーケストレーション
4. **不確実性**：漠然とした要件 → ブレインストーミング
5. **エラー回復**：問題 → イントロスペクション

**優先ルール:**

- **安全第一**：品質と検証は常に効率よりも優先されます
- **ユーザーの意図**: 手動フラグは自動検出を上書きします
- **コンテキスト適応**: 複雑さに基づいてモードをスタック
- **リソース管理**：プレッシャー下では効率モードが活性化する

---

## 実世界の例

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#real-world-examples)

### 完全なワークフローの例

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#complete-workflow-examples)

**新規プロジェクト開発:**

```shell
# Phase 1: Discovery (Brainstorming Mode auto-activates)
"I want to build a productivity app"
→ 🤔 Socratic questions about users, features, platform choice
→ 📝 Structured requirements brief

# Phase 2: Planning (Task Management Mode auto-activates)  
/sc:implement "core productivity features"
→ 📋 Multi-phase breakdown with dependencies
→ 🎯 Phase coordination with quality gates

# Phase 3: Implementation (Orchestration Mode coordinates tools)
/sc:implement "frontend and backend systems"
→ 🎯 Magic (UI) + Context7 (patterns) + Sequential (architecture)
→ ⚡ Parallel execution optimization
```

**複雑な問題のデバッグ:**

```shell
# Problem analysis (Introspection Mode auto-activates)
"Users getting intermittent auth failures"
→ 🤔 Transparent reasoning about potential causes
→ 🎯 Hypothesis formation and evidence gathering
→ 💡 Pattern recognition across similar issues

# Systematic resolution (Task Management coordinates)
# 認証システムを包括的に修正
→ 📋 Phase 1: Root cause analysis
→ 📋 Phase 2: Solution implementation  
→ 📋 Phase 3: Testing and validation
```

### モードの組み合わせパターン

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#mode-combination-patterns)

**非常に複雑なシナリオ:**

```shell
# Large refactoring with multiple constraints
/sc:improve legacy-system/ --introspect --uc --orchestrate
→ 🔍 Transparent reasoning (Introspection)
→ ⚡ Compressed communication (Token Efficiency)  
→ 🎯 Optimal tool coordination (Orchestration)
→ 📋 Systematic phases (Task Management auto-activates)
```

---

## クイックリファレンス

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#quick-reference)

### モード起動パターン

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#mode-activation-patterns)

|トリガータイプ|入力例|モードが有効|主要な動作|
|---|---|---|---|
|**漠然とした要求**|「アプリを作りたい」|🧠 ブレインストーミング|ソクラテス式の発見的質問|
|**複雑なスコープ**|>3 つのファイルまたは >2 つのディレクトリ|📋 タスク管理|位相調整|
|**マルチツールの必要性**|分析 + 実装|🎯 オーケストレーション|ツールの最適化|
|**エラー回復**|「期待通りに動作していません」|🔍 内省|透明な推論|
|**リソースの圧力**|高コンテキスト使用|⚡ トークン効率|シンボル圧縮|
|**簡単なタスク**|「この機能を修正する」|🎨 標準|明確で直接的なアプローチ|

### 手動オーバーライドコマンド

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#manual-override-commands)

```shell
# Force specific mode behaviors
/sc:command --brainstorm    # Collaborative discovery
/sc:command --introspect    # Reasoning transparency
/sc:command --task-manage   # Hierarchical coordination
/sc:command --orchestrate   # Tool optimization
/sc:command --uc           # Token compression

# Combine multiple modes
/sc:command --introspect --uc    # Transparent + efficient
/sc:command --task-manage --orchestrate  # Coordinated + optimized
```

---

## トラブルシューティング

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#troubleshooting)

トラブルシューティングのヘルプについては、以下を参照してください。

- [よくある問題](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/reference/common-issues.md)- よくある問題に対するクイック修正
- [トラブルシューティングガイド](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/reference/troubleshooting.md)- 包括的な問題解決

### よくある問題

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#common-issues)

- **モードがアクティブ化されていません**: 手動フラグを使用してください: `--brainstorm`、、`--introspect``--uc`
- **間違ったモードがアクティブです**: リクエスト内の複雑なトリガーとキーワードを確認してください
- **予期しないモード切り替え**：タスクの進行に基づく通常の動作
- **実行への影響**: モードはツールの使用を最適化するものであり、実行には影響しないはずです。
- **モードの競合**:[フラグガイドでフラグの優先順位ルールを確認してください](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/flags.md)

### 即時修正

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#immediate-fixes)

- **特定のモードを強制**:`--brainstorm`またはのような明示的なフラグを使用する`--task-manage`
- **リセットモードの動作**: モード状態をリセットするには、Claude Code セッションを再起動します。
- **モードインジケーターを確認する**: 応答に🤔、🎯、📋の記号があるかどうかを確認します
- **複雑さを検証**: 単純なタスクは標準モードを使用し、複雑なタスクは自動的に切り替わります

### モード固有のトラブルシューティング

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#mode-specific-troubleshooting)

**ブレインストーミングモードの問題:**

```shell
# Problem: Mode gives solutions instead of asking questions
# Quick Fix: Check request clarity and use explicit flag
/sc:brainstorm "web app" --brainstorm         # Force discovery mode
"I have a vague idea about..."                # Use uncertainty language
"Maybe we could build..."                     # Trigger exploration
```

**タスク管理モードの問題:**

```shell
# Problem: Simple tasks getting complex coordination
# Quick Fix: Reduce scope or use simpler commands
/sc:implement "function" --no-task-manage     # Disable coordination
/sc:troubleshoot bug.js                       # Use basic commands
# Check if task really is complex (>3 files, >2 directories)
```

**トークン効率モードの問題:**

```shell
# Problem: Output too compressed or unclear
# Quick Fix: Disable compression for clarity
/sc:command --no-uc                           # Disable compression
/sc:command --verbose                         # Force detailed output
# Use when clarity is more important than efficiency
```

**イントロスペクションモードの問題:**

```shell
# Problem: Too much meta-commentary, not enough action
# Quick Fix: Disable introspection for direct work
/sc:command --no-introspect                   # Direct execution
# Use introspection only for learning and debugging
```

**オーケストレーション モードの問題:**

```shell
# Problem: Tool coordination causing confusion
# Quick Fix: Simplify tool usage
/sc:command --no-mcp                          # Native tools only
/sc:command --simple                          # Basic execution
# Check if task complexity justifies orchestration
```

### エラーコードリファレンス

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#error-code-reference)

|モードエラー|意味|クイックフィックス|
|---|---|---|
|**B001**|ブレインストーミングが起動できませんでした|`--brainstorm`明示的なフラグを使用する|
|**T001**|タスク管理のオーバーヘッド|`--no-task-manage`簡単なタスクに使用する|
|**U001**|トークン効率が強すぎる|使用`--verbose`または`--no-uc`|
|**I001**|イントロスペクションモードが停止しました|`--no-introspect`直接行動に使う|
|**O001**|オーケストレーション調整に失敗|使用`--no-mcp`または`--simple`|
|**M001**|モードの競合が検出されました|フラグの優先順位のルールを確認する|
|**M002**|モード切り替えループ|状態をリセットするにはセッションを再起動してください|
|**M003**|モードが認識されません|SuperClaudeを更新するかスペルをチェックする|

### プログレッシブサポートレベル

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#progressive-support-levels)

**レベル 1: クイックフィックス (< 2 分)**

- 自動モード選択を無効にするには手動フラグを使用します
- タスクの複雑さが期待されるモードの動作と一致しているかどうかを確認する
- Claude Codeセッションを再起動してみてください

**レベル2: 詳細なヘルプ（5～15分）**

```shell
# Mode-specific diagnostics
/sc:help modes                            # List all available modes
/sc:reflect --type mode-status            # Check current mode state
# Review request complexity and triggers
```

- モードのインストールに関する問題については、[一般的な問題ガイドを](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/reference/common-issues.md)参照してください。

**レベル3: 専門家によるサポート（30分以上）**

```shell
# Deep mode analysis
SuperClaude install --diagnose
# Check mode activation patterns
# Review behavioral triggers and thresholds
```

- 行動モード分析については[診断リファレンスガイド](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/reference/diagnostic-reference.md)を参照してください

**レベル4: コミュニティサポート**

- [GitHub Issues](https://github.com/SuperClaude-Org/SuperClaude_Framework/issues)でのモードの問題の報告[](https://github.com/SuperClaude-Org/SuperClaude_Framework/issues)
- 予期しないモード動作の例を含める
- 望ましいモードと実際のモードのアクティベーションを説明する

### 成功の検証

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#success-validation)

モード修正を適用した後、次のようにテストします。

- [ ] シンプルなリクエストには標準モード（明確で直接的な応答）を使用します
- [ ] 複雑な要求は適切なモード（調整、推論）を自動的にアクティブ化します
- [ ] 手動フラグは自動検出を正しく上書きします
- [ ] モードインジケーター（🤔、🎯、📋）は予想通りに表示されます
- [ ] さまざまなモードでパフォーマンスは良好です

## クイックトラブルシューティング（レガシー）

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#quick-troubleshooting-legacy)

- **モードがアクティブ化されない**→手動フラグを使用: `--brainstorm`、、`--introspect``--uc`
- **間違ったモードがアクティブです**→ リクエスト内の複雑なトリガーとキーワードを確認してください
- **予期せぬモード切り替え**→ タスクの進行に基づく通常の動作
- **実行への影響**→ モードはツールの使用を最適化するものであり、実行には影響しないはずです
- **モードの競合→**[フラグガイド](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/flags.md)でフラグの優先順位ルールを確認してください[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/flags.md)

## よくある質問

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#frequently-asked-questions)

**Q: どのモードがアクティブになっているかはどうすればわかりますか?** A: 通信パターンで次のインジケーターを確認してください。

- 🤔発見の質問 → ブレインストーミング
- 🎯 推論の透明性 → 内省
- フェーズの内訳 → タスク管理
- ツール調整 → オーケストレーション
- シンボル圧縮 → トークン効率

**Q: 特定のモードを強制できますか?** A: はい、手動フラグを使用して自動検出をオーバーライドします。

```shell
/sc:command --brainstorm     # Force discovery
/sc:command --introspect     # Add transparency
/sc:command --task-manage    # Enable coordination
/sc:command --uc            # Compress output
```

**Q: モードは実行に影響しますか?** A: モードは調整を通じてツールの使用を最適化します。

- **トークン効率**: 30～50%のコンテキスト削減
- **オーケストレーション**：並列処理
- **タスク管理**：体系的な計画を通じて手戻りを防止

**Q: モードは連携して動作しますか?** A: はい、モードは互いに補完し合うように設計されています。

- **タスク管理は**他のモードを調整します
- **トークン効率は**あらゆるモードの出力を圧縮する
- **イントロスペクションは**あらゆるワークフローに透明性をもたらします

---

## まとめ

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#summary)

SuperClaude の 5 つの行動モードは、ユーザーのニーズに自動的に適合する**インテリジェントな適応システムを作成します。**

- **🧠 ブレインストーミング**：漠然としたアイデアを明確な要件に変換する
- **🔍 イントロスペクション**：学習とデバッグのための透過的な推論を提供します
- **📋 タスク管理**：複雑な複数ステップの操作を調整します
- **🎯 オーケストレーション**: ツールの選択と並列実行を最適化します
- **⚡ トークン効率**: 明瞭さを保ちながらコミュニケーションを圧縮する
- **🎨 標準**: 単純なタスクに対してプロフェッショナルな基準を維持します

**重要な洞察**：モードについて考える必要はありません。モードは透過的に動作し、開発エクスペリエンスを向上させます。達成したいことを説明するだけで、SuperClaudeはニーズに合わせてアプローチを自動的に調整します。

---

## 関連ガイド

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/modes.md#related-guides)

**学習の進捗:**

**🌱 エッセンシャル（第1週）**

- [クイックスタートガイド](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/getting-started/quick-start.md)- モードの有効化例
- [コマンドリファレンス](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md)- コマンドは自動的にモードをアクティブ化します
- [インストールガイド](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/getting-started/installation.md)- 動作モードの設定

**🌿中級（第2～3週）**

- [エージェントガイド](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/agents.md)- モードとスペシャリストの連携方法
- [フラグガイド](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/flags.md)- 手動モードの制御と最適化
- [例文集](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/reference/examples-cookbook.md)- モードパターンの実践

**🌲 上級（2ヶ月目以降）**

- [MCP サーバー](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/mcp-servers.md)- 拡張機能を備えたモード統合
- [セッション管理](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/session-management.md)- タスク管理モードのワークフロー
- [はじめに](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/getting-started/quick-start.md)- モードの使用パターン

**🔧 エキスパート**

- [技術アーキテクチャ](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/developer-guide/technical-architecture.md)- モード実装の詳細
- [コードの貢献](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/developer-guide/contributing-code.md)- モードの機能を拡張する

**モード固有のガイド:**

- **ブレインストーミング**：[要件発見パターン](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/reference/examples-cookbook.md#requirements)
- **タスク管理**：[セッション管理ガイド](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/session-management.md)
- **オーケストレーション**: [MCP サーバー ガイド](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/mcp-servers.md)
- **トークン効率**：[コマンドの基礎](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#token-efficiency)
