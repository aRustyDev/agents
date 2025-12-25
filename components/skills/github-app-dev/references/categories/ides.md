# IDE Integration GitHub Apps

GitHub Apps that integrate with integrated development environments: editor extensions, code navigation, real-time collaboration, and development workflow integration.

## Common Use Cases

- **GitHub Integration** - PR/issue management in editor
- **Code Navigation** - Go to definition across repos
- **Real-time Collaboration** - Live Share, pair programming
- **Copilot Integration** - AI-assisted coding
- **Codespaces** - Cloud development environments
- **Review in Editor** - PR review without leaving IDE

## Key APIs

IDE integrations primarily use:

| API | Use Case |
|-----|----------|
| OAuth User Flow | Authenticate user |
| REST API | Repository operations |
| GraphQL API | Efficient data fetching |
| Git Operations | Clone, push, pull |
| Language Server Protocol | Code intelligence |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Contents | Read/Write | File operations |
| Pull requests | Read/Write | PR management |
| Issues | Read/Write | Issue tracking |
| Codespaces | Write | Cloud environments |
| Metadata | Read | Repository info |

### Extension Permission Set
```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write
  metadata: read
```

## Common Patterns

### VSCode Extension Authentication

```typescript
import * as vscode from "vscode";

export async function authenticate(): Promise<string> {
  const session = await vscode.authentication.getSession(
    "github",
    ["repo", "user"],
    { createIfNone: true }
  );

  return session.accessToken;
}

// Use in extension
export async function activate(context: vscode.ExtensionContext) {
  const token = await authenticate();

  // Now use token for GitHub API calls
  const octokit = new Octokit({ auth: token });
}
```

### Language Server Integration

```typescript
import {
  createConnection,
  TextDocuments,
  ProposedFeatures,
} from "vscode-languageserver/node";

const connection = createConnection(ProposedFeatures.all);
const documents = new TextDocuments();

// Provide hover information with GitHub context
connection.onHover(async (params) => {
  const document = documents.get(params.textDocument.uri);
  if (!document) return null;

  const word = getWordAtPosition(document, params.position);

  // Check if word is a GitHub reference
  if (word.match(/#\d+/)) {
    const issueNumber = parseInt(word.slice(1));
    const issue = await fetchIssue(issueNumber);

    return {
      contents: {
        kind: "markdown",
        value: `**#${issue.number}**: ${issue.title}\n\n${issue.body?.slice(0, 200)}...`,
      },
    };
  }

  return null;
});
```

### Pull Request Review in Editor

```typescript
// VSCode extension for PR review
import * as vscode from "vscode";

interface PRComment {
  path: string;
  line: number;
  body: string;
  author: string;
}

class PRReviewProvider implements vscode.CommentController {
  private controller: vscode.CommentController;
  private comments: Map<string, vscode.CommentThread[]> = new Map();

  constructor() {
    this.controller = vscode.comments.createCommentController(
      "github-pr-review",
      "GitHub PR Review"
    );
  }

  async loadPRComments(owner: string, repo: string, prNumber: number) {
    const comments = await fetchPRComments(owner, repo, prNumber);

    for (const comment of comments) {
      const uri = vscode.Uri.file(comment.path);
      const range = new vscode.Range(comment.line - 1, 0, comment.line - 1, 0);

      const thread = this.controller.createCommentThread(uri, range, [
        {
          author: { name: comment.author },
          body: new vscode.MarkdownString(comment.body),
          mode: vscode.CommentMode.Preview,
        },
      ]);

      const existing = this.comments.get(comment.path) || [];
      existing.push(thread);
      this.comments.set(comment.path, existing);
    }
  }

  async addComment(path: string, line: number, body: string) {
    await createPRComment({
      path,
      line,
      body,
    });
  }
}
```

### Code Actions for GitHub

```typescript
import * as vscode from "vscode";

export class GitHubCodeActionProvider implements vscode.CodeActionProvider {
  provideCodeActions(
    document: vscode.TextDocument,
    range: vscode.Range,
    context: vscode.CodeActionContext
  ): vscode.CodeAction[] {
    const actions: vscode.CodeAction[] = [];

    // Get selected text
    const selectedText = document.getText(range);

    // Action: Create issue from selection
    if (selectedText.length > 0) {
      const createIssue = new vscode.CodeAction(
        "Create GitHub Issue from Selection",
        vscode.CodeActionKind.QuickFix
      );

      createIssue.command = {
        command: "github.createIssueFromSelection",
        title: "Create Issue",
        arguments: [selectedText, document.uri, range],
      };

      actions.push(createIssue);
    }

    // Action: Link to GitHub (create permalink)
    const permalink = new vscode.CodeAction(
      "Copy GitHub Permalink",
      vscode.CodeActionKind.Source
    );

    permalink.command = {
      command: "github.copyPermalink",
      title: "Copy Permalink",
      arguments: [document.uri, range],
    };

    actions.push(permalink);

    return actions;
  }
}
```

### Git Status Integration

```typescript
// File decoration provider for Git status
export class GitHubFileDecorationProvider
  implements vscode.FileDecorationProvider
{
  private _onDidChangeFileDecorations = new vscode.EventEmitter<vscode.Uri | vscode.Uri[]>();
  readonly onDidChangeFileDecorations = this._onDidChangeFileDecorations.event;

  async provideFileDecoration(uri: vscode.Uri): Promise<vscode.FileDecoration | undefined> {
    const relativePath = vscode.workspace.asRelativePath(uri);
    const status = await getFileGitStatus(relativePath);

    switch (status) {
      case "modified":
        return {
          badge: "M",
          color: new vscode.ThemeColor("gitDecoration.modifiedResourceForeground"),
          tooltip: "Modified",
        };
      case "added":
        return {
          badge: "A",
          color: new vscode.ThemeColor("gitDecoration.addedResourceForeground"),
          tooltip: "Added",
        };
      case "deleted":
        return {
          badge: "D",
          color: new vscode.ThemeColor("gitDecoration.deletedResourceForeground"),
          tooltip: "Deleted",
        };
      default:
        return undefined;
    }
  }
}
```

### Codespaces Integration

```typescript
// Launch Codespace from extension
async function openInCodespace(repoUrl: string) {
  const { owner, repo } = parseGitHubUrl(repoUrl);

  // Create or get existing codespace
  const codespaces = await octokit.codespaces.listForAuthenticatedUser({
    per_page: 100,
  });

  let codespace = codespaces.data.codespaces.find(
    cs => cs.repository.full_name === `${owner}/${repo}` && cs.state === "Available"
  );

  if (!codespace) {
    // Create new codespace
    const { data } = await octokit.codespaces.createForAuthenticatedUser({
      repository_id: await getRepoId(owner, repo),
    });
    codespace = data;
  }

  // Open in browser or VS Code
  const openUrl = `https://github.dev/${owner}/${repo}`;
  vscode.env.openExternal(vscode.Uri.parse(openUrl));
}
```

### Real-time Collaboration Awareness

```typescript
// Show collaborators editing same file
interface Collaborator {
  name: string;
  cursor: { line: number; character: number };
  selection?: vscode.Range;
}

class CollaborationProvider {
  private decorationType = vscode.window.createTextEditorDecorationType({
    after: {
      margin: "0 0 0 10px",
      contentText: "",
    },
  });

  updateCollaborators(editor: vscode.TextEditor, collaborators: Collaborator[]) {
    const decorations: vscode.DecorationOptions[] = collaborators.map(c => ({
      range: new vscode.Range(c.cursor.line, c.cursor.character, c.cursor.line, c.cursor.character),
      renderOptions: {
        after: {
          contentText: ` 👤 ${c.name}`,
          color: this.getColorForUser(c.name),
        },
      },
    }));

    editor.setDecorations(this.decorationType, decorations);
  }

  private getColorForUser(name: string): string {
    const colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"];
    const hash = name.split("").reduce((a, b) => a + b.charCodeAt(0), 0);
    return colors[hash % colors.length];
  }
}
```

## IDE-Specific Patterns

### VSCode
```typescript
// Command registration
context.subscriptions.push(
  vscode.commands.registerCommand("github.openPR", async () => {
    const pr = await selectPR();
    if (pr) {
      vscode.env.openExternal(vscode.Uri.parse(pr.html_url));
    }
  })
);

// Status bar item
const statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left);
statusBar.text = "$(git-pull-request) PR #123";
statusBar.command = "github.openPR";
statusBar.show();
```

### JetBrains (IntelliJ, WebStorm, etc.)
```kotlin
// Plugin.xml service registration
class GitHubService : Service {
    fun authenticate() {
        // Use JetBrains credential store
        val credentials = PasswordSafe.instance.get(
            CredentialAttributes("GitHub", "token")
        )
    }
}
```

### Neovim/Vim
```lua
-- Lua plugin for Neovim
local github = require("github")

vim.api.nvim_create_user_command("GHPullRequest", function(opts)
  github.create_pr({
    title = opts.args,
    base = "main",
    head = vim.fn.system("git branch --show-current"):gsub("\n", ""),
  })
end, { nargs = 1 })
```

## Security Considerations

- **Token scope minimization** - Request only needed scopes
- **Credential storage** - Use IDE's secure storage
- **Extension sandboxing** - Respect IDE security model
- **User consent** - Clear permission dialogs
- **Token refresh** - Handle expiration gracefully

## Example Apps in This Category

- **GitHub Pull Requests** - VSCode extension
- **GitLens** - Advanced Git integration
- **GitHub Copilot** - AI pair programmer
- **Codespaces** - Cloud development
- **Live Share** - Real-time collaboration

## Related Categories

- [Desktop Tools](desktop-tools.md) - Native applications
- [Code Review](code-review.md) - Review tools
- [Code Search](code-search.md) - Navigation

## See Also

- [VSCode Extension API](https://code.visualstudio.com/api)
- [GitHub Copilot](https://github.com/features/copilot)
- [GitHub Codespaces](https://github.com/features/codespaces)
