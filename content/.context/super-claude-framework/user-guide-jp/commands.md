# SuperClaude コマンドガイド

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#superclaude-commands-guide)

`/sc:*`SuperClaude は、ワークフロー用コマンドと`@agent-*`スペシャリスト用コマンドの 21 個の Claude Code コマンドを提供します。

## コマンドの種類

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#command-types)

|タイプ|使用場所|形式|例|
|---|---|---|---|
|**スラッシュコマンド**|クロード・コード|`/sc:[command]`|`/sc:implement "feature"`|
|**エージェント**|クロード・コード|`@agent-[name]`|`@agent-security "review"`|
|**インストール**|ターミナル|`SuperClaude [command]`|`SuperClaude install`|

## クイックテスト

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#quick-test)

```shell
# Terminal: Verify installation
python3 -m SuperClaude --version
# Claude Code CLI verification: claude --version

# Claude Code: Test commands
/sc:brainstorm "test project"    # Should ask discovery questions
/sc:analyze README.md           # Should provide analysis
```

**ワークフロー**：`/sc:brainstorm "idea"`→→`/sc:implement "feature"`​`/sc:test`

## 🎯 SuperClaude コマンドの理解

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#-understanding-superclaude-commands)

## SuperClaudeの仕組み

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#how-superclaude-works)

SuperClaude は、Claude Code が特殊な動作を実行するために読み込む動作コンテキストファイルを提供します。 と入力すると`/sc:implement`、Claude Code は`implement.md`コンテキストファイルを読み込み、その動作指示に従います。

**SuperClaude コマンドはソフトウェアによって実行されるのではなく**、フレームワークから特殊な命令ファイルを読み取ることで Claude コードの動作を変更するコンテキスト トリガーです。

### コマンドの種類:

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#command-types-1)

- **スラッシュコマンド**（`/sc:*`）：ワークフローパターンと動作​​モードをトリガーする
- **エージェントの呼び出し**（`@agent-*`）：特定のドメインスペシャリストを手動で起動する
- **フラグ**（`--think`、`--safe-mode`）：コマンドの動作と深さを変更する

### コンテキストメカニズム:

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#the-context-mechanism)

1. **ユーザー入力**: 入力する`/sc:implement "auth system"`
2. **コンテキスト読み込み**: クロードコード読み取り`~/.claude/superclaude/Commands/implement.md`
3. **行動の採用**：クロードはドメインの専門知識、ツールの選択、検証パターンを適用します
4. **強化された出力**: セキュリティ上の考慮事項とベストプラクティスを備えた構造化された実装

**重要なポイント**: これにより、従来のソフトウェア実行ではなくコンテキスト管理を通じて洗練された開発ワークフローが作成されます。

### インストールコマンドと使用コマンド

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#installation-vs-usage-commands)

**🖥️ ターミナルコマンド**（実際の CLI ソフトウェア）：

- `SuperClaude install`- フレームワークコンポーネントをインストールします
- `SuperClaude update`- 既存のインストールを更新します
- `SuperClaude uninstall`- フレームワークのインストールを削除します
- `python3 -m SuperClaude --version`- インストール状態を確認する

**💬 クロード コード コマンド**(コンテキスト トリガー):

- `/sc:brainstorm`- 要件検出コンテキストをアクティブ化します
- `/sc:implement`- 機能開発コンテキストをアクティブ化します
- `@agent-security`- セキュリティスペシャリストのコンテキストをアクティブ化します
- すべてのコマンドはClaude Codeチャットインターフェース内でのみ機能します

> **クイック スタート**: `/sc:brainstorm "your project idea"`→ `/sc:implement "feature name"`→を試して`/sc:test`、コア ワークフローを体験してください。

## 🧪 セットアップのテスト

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#-testing-your-setup)

### 🖥️ ターミナル検証（ターミナル/CMDで実行）

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#%EF%B8%8F-terminal-verification-run-in-terminalcmd)

```shell
# Verify SuperClaude is working (primary method)
python3 -m SuperClaude --version
# Example output: SuperClaude 4.1.5

# Claude Code CLI version check
claude --version

# Check installed components
python3 -m SuperClaude install --list-components | grep mcp
# Example output: Shows installed MCP components
```

### 💬 クロードコードテスト（クロードコードチャットに入力）

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#-claude-code-testing-type-in-claude-code-chat)

```
# Test basic /sc: command
/sc:brainstorm "test project"
# Example behavior: Interactive requirements discovery starts

# Test command help
/sc:help
# Example behavior: List of available commands
```

**テストが失敗した場合**:[インストールガイド](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/getting-started/installation.md)または[トラブルシューティングを確認してください](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#troubleshooting)

### 📝 コマンドクイックリファレンス

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#-command-quick-reference)

|コマンドタイプ|走る場所|形式|目的|例|
|---|---|---|---|---|
|**🖥️ インストール**|ターミナル/CMD|`SuperClaude [command]`|セットアップとメンテナンス|`SuperClaude install`|
|**🔧 構成**|ターミナル/CMD|`python3 -m SuperClaude [command]`|高度な設定|`python3 -m SuperClaude --version`|
|**💬 スラッシュコマンド**|クロード・コード|`/sc:[command]`|ワークフロー自動化|`/sc:implement "feature"`|
|**🤖 エージェントの呼び出し**|クロード・コード|`@agent-[name]`|手動スペシャリストの有効化|`@agent-security "review"`|
|**⚡ 強化されたフラグ**|クロード・コード|`/sc:[command] --flags`|行動修正|`/sc:analyze --think-hard`|

> **注意**：すべての`/sc:`コマンドと`@agent-`呼び出しは、ターミナルではなくClaude Codeチャット内で動作します。これらのコマンドと呼び出しは、Claude CodeがSuperClaudeフレームワークから特定のコンテキストファイルを読み取るようにトリガーします。

## 目次

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#table-of-contents)

- [必須コマンド](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#essential-commands)- ここから始めましょう（8つのコアコマンド）
- [一般的なワークフロー](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#common-workflows)- 機能するコマンドの組み合わせ
- [完全なコマンドリファレンス](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#full-command-reference)- カテゴリ別に整理された全21個のコマンド
- [トラブルシューティング](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#troubleshooting)- よくある問題と解決策
- [コマンドインデックス](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#command-index)- カテゴリ別にコマンドを検索

---

## 必須コマンド

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#essential-commands)

**即時の生産性向上のためのコアワークフロー コマンド:**

### `/sc:brainstorm`- プロジェクト発見

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#scbrainstorm---project-discovery)

**目的**: 対話型の要件検出とプロジェクト計画  
**構文**:`/sc:brainstorm "your idea"` `[--strategy systematic|creative]`

**ユースケース**:

- 新しいプロジェクトの計画:`/sc:brainstorm "e-commerce platform"`
- 機能の探索:`/sc:brainstorm "user authentication system"`
- 問題解決:`/sc:brainstorm "slow database queries"`

### `/sc:implement`- 機能開発

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#scimplement---feature-development)

**目的**: インテリジェントなスペシャリストルーティングによるフルスタック機能の実装  
**構文**:`/sc:implement "feature description"` `[--type frontend|backend|fullstack] [--focus security|performance]`

**ユースケース**:

- 認証:`/sc:implement "JWT login system"`
- UI コンポーネント:`/sc:implement "responsive dashboard"`
- API:`/sc:implement "REST user endpoints"`
- データベース:`/sc:implement "user schema with relationships"`

### `/sc:analyze`- コード評価

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#scanalyze---code-assessment)

**目的**: 品質、セキュリティ、パフォーマンスにわたる包括的なコード分析  
**構文**:`/sc:analyze [path]` `[--focus quality|security|performance|architecture]`

**ユースケース**:

- プロジェクトの健全性:`/sc:analyze .`
- セキュリティ監査:`/sc:analyze --focus security`
- パフォーマンスレビュー:`/sc:analyze --focus performance`

### `/sc:troubleshoot`- 問題診断

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#sctroubleshoot---problem-diagnosis)

**目的**: 根本原因分析による体系的な問題診断  
**構文**:`/sc:troubleshoot "issue description"` `[--type build|runtime|performance]`

**ユースケース**:

- ランタイムエラー:`/sc:troubleshoot "500 error on login"`
- ビルドの失敗:`/sc:troubleshoot --type build`
- パフォーマンスの問題:`/sc:troubleshoot "slow page load"`

### `/sc:test`- 品質保証

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#sctest---quality-assurance)

**目的**: カバレッジ分析による包括的なテスト  
**構文**:`/sc:test` `[--type unit|integration|e2e] [--coverage] [--fix]`

**ユースケース**:

- 完全なテストスイート:`/sc:test --coverage`
- ユニットテスト:`/sc:test --type unit --watch`
- E2E検証:`/sc:test --type e2e`

### `/sc:improve`- コード強化

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#scimprove---code-enhancement)

**目的**: 体系的なコードの改善と最適化を適用する  
**構文**:`/sc:improve [path]` `[--type performance|quality|security] [--preview]`

**ユースケース**:

- 一般的な改善点:`/sc:improve src/`
- パフォーマンスの最適化:`/sc:improve --type performance`
- セキュリティ強化:`/sc:improve --type security`

### `/sc:document`- ドキュメント生成

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#scdocument---documentation-generation)

**目的**: コードとAPIの包括的なドキュメントを生成する  
**構文**:`/sc:document [path]` `[--type api|user-guide|technical] [--format markdown|html]`

**ユースケース**:

- APIドキュメント:`/sc:document --type api`
- ユーザーガイド:`/sc:document --type user-guide`
- 技術ドキュメント:`/sc:document --type technical`

### `/sc:workflow`- 実装計画

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#scworkflow---implementation-planning)

**目的**: 要件から構造化された実装計画を生成する  
**構文**:`/sc:workflow "feature description"` `[--strategy agile|waterfall] [--format markdown]`

**ユースケース**:

- 機能計画:`/sc:workflow "user authentication"`
- スプリント計画:`/sc:workflow --strategy agile`
- アーキテクチャ計画：`/sc:workflow "microservices migration"`

---

## 一般的なワークフロー

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#common-workflows)

**実証済みのコマンドの組み合わせ:**

### 新しいプロジェクトのセットアップ

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#new-project-setup)

```shell
/sc:brainstorm "project concept"      # Define requirements
/sc:design "system architecture"      # Create technical design  
/sc:workflow "implementation plan"    # Generate development roadmap
```

### 機能開発

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#feature-development)

```shell
/sc:implement "feature name"          # Build the feature
/sc:test --coverage                   # Validate with tests
/sc:document --type api               # Generate documentation  
```

### コード品質の改善

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#code-quality-improvement)

```shell
/sc:analyze --focus quality           # Assess current state
/sc:improve --preview                 # Preview improvements
/sc:test --coverage                   # Validate changes
```

### バグ調査

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#bug-investigation)

```shell
/sc:troubleshoot "issue description"  # Diagnose the problem
/sc:analyze --focus problem-area      # Deep analysis
/sc:improve --fix --safe-mode         # Apply targeted fixes
```

## 完全なコマンドリファレンス

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#full-command-reference)

### 開発コマンド

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#development-commands)

|指示|目的|最適な用途|
|---|---|---|
|**ワークフロー**|実施計画|プロジェクトロードマップ、スプリント計画|
|**埋め込む**|機能開発|フルスタック機能、API開発|
|**建てる**|プロジェクトのコンパイル|CI/CD、プロダクションビルド|
|**デザイン**|システムアーキテクチャ|API仕様、データベーススキーマ|

### 分析コマンド

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#analysis-commands)

|指示|目的|最適な用途|
|---|---|---|
|**分析する**|コード評価|品質監査、セキュリティレビュー|
|**トラブルシューティング**|問題診断|バグ調査、パフォーマンスの問題|
|**説明する**|コードの説明|学習、コードレビュー|

### 品質コマンド

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#quality-commands)

|指示|目的|最適な用途|
|---|---|---|
|**改善する**|コード強化|パフォーマンスの最適化、リファクタリング|
|**掃除**|技術的負債|デッドコードの削除、整理|
|**テスト**|品質保証|テスト自動化、カバレッジ分析|
|**書類**|ドキュメント|APIドキュメント、ユーザーガイド|

### プロジェクト管理

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#project-management)

|指示|目的|最適な用途|
|---|---|---|
|**見積もり**|プロジェクト見積もり|タイムライン計画、リソース割り当て|
|**タスク**|タスク管理|複雑なワークフロー、タスク追跡|
|**スポーン**|メタオーケストレーション|大規模プロジェクト、並列実行|

### ユーティリティコマンド

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#utility-commands)

|指示|目的|最適な用途|
|---|---|---|
|**ギット**|バージョン管理|コミット管理、ブランチ戦略|
|**索引**|コマンド検出|機能の探索、コマンドの検索|

### セッションコマンド

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#session-commands)

|指示|目的|最適な用途|
|---|---|---|
|**負荷**|コンテキストの読み込み|セッションの初期化、プロジェクトのオンボーディング|
|**保存**|セッションの永続性|チェックポイント、コンテキスト保存|
|**反映する**|タスクの検証|進捗評価、完了検証|
|**選択ツール**|ツールの最適化|パフォーマンスの最適化、ツールの選択|

---

## コマンドインデックス

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#command-index)

**機能別:**

- **計画**：ブレインストーミング、設計、ワークフロー、見積もり
- **開発**：実装、ビルド、git
- **分析**：分析、トラブルシューティング、説明
- **品質**: 改善、クリーンアップ、テスト、ドキュメント化
- **管理**: タスク、スポーン、ロード、保存、反映
- **ユーティリティ**: インデックス、選択ツール

**複雑さ別:**

- **初心者**：ブレインストーミング、実装、分析、テスト
- **中級**：ワークフロー、設計、改善、ドキュメント
- **上級**：スポーン、タスク、選択ツール、リフレクト

## トラブルシューティング

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#troubleshooting)

**コマンドの問題:**

- **コマンドが見つかりません**: インストールを確認してください:`python3 -m SuperClaude --version`
- **応答なし**: Claude Codeセッションを再開する
- **処理遅延**: `--no-mcp`MCPサーバーなしでテストするために使用します

**クイックフィックス:**

- セッションをリセット:`/sc:load`再初期化する
- ステータスを確認:`SuperClaude install --list-components`
- ヘルプ:[トラブルシューティングガイド](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/reference/troubleshooting.md)

## 次のステップ

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/commands.md#next-steps)

- [フラグガイド](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/flags.md)- コマンドの動作を制御する
- [エージェントガイド](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/user-guide/agents.md)- スペシャリストのアクティベーション
- [例のクックブック](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/reference/examples-cookbook.md)- 実際の使用パターン
