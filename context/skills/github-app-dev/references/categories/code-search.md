# Code Search GitHub Apps

GitHub Apps that provide enhanced code search, indexing, and navigation capabilities beyond GitHub's built-in search.

## Common Use Cases

- **Semantic Search** - Natural language code queries
- **Cross-Repo Search** - Search across organization repos
- **Symbol Navigation** - Find definitions and references
- **Code Intelligence** - Language-aware indexing
- **Usage Analytics** - Track code usage patterns
- **Dead Code Detection** - Find unused code

## Key Webhooks

| Webhook | Use Case |
|---------|----------|
| `push` | Re-index on code changes |
| `repository.created` | Index new repositories |
| `repository.deleted` | Remove from index |
| `repository.renamed` | Update index references |
| `repository.transferred` | Handle ownership changes |
| `installation.created` | Initial full index |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Contents | Read | Access source code for indexing |
| Metadata | Read | Repository information |
| Administration | Read | List repositories in org |

### Minimal Permission Set
```yaml
permissions:
  contents: read
  metadata: read
```

## Common Patterns

### Incremental Indexing on Push

```typescript
app.on("push", async (context) => {
  const { commits, ref, after, repository, before } = context.payload;

  // Only index default branch
  if (ref !== `refs/heads/${repository.default_branch}`) return;

  // Get changed files
  const changedFiles = new Set<string>();
  for (const commit of commits) {
    commit.added.forEach(f => changedFiles.add(f));
    commit.modified.forEach(f => changedFiles.add(f));
    commit.removed.forEach(f => changedFiles.add(f));
  }

  // Index each changed file
  for (const file of changedFiles) {
    const isRemoved = commits.some(c => c.removed.includes(file));

    if (isRemoved) {
      await removeFromIndex(repository.full_name, file);
    } else {
      const content = await getFileContent(context, file, after);
      if (content && isIndexableFile(file)) {
        await indexFile({
          repo: repository.full_name,
          path: file,
          content,
          sha: after,
          language: detectLanguage(file),
        });
      }
    }
  }

  // Update repository metadata
  await updateRepoMetadata(repository.full_name, {
    lastIndexed: new Date().toISOString(),
    headSha: after,
    fileCount: await getFileCount(repository.full_name),
  });
});

function isIndexableFile(filename: string): boolean {
  const INDEXABLE_EXTENSIONS = [
    ".js", ".ts", ".jsx", ".tsx", ".py", ".go", ".rs",
    ".java", ".rb", ".php", ".cs", ".cpp", ".c", ".h",
  ];
  return INDEXABLE_EXTENSIONS.some(ext => filename.endsWith(ext));
}
```

### Full Repository Indexing

```typescript
async function fullIndexRepository(context, repository) {
  // Get file tree
  const { data: tree } = await context.octokit.git.getTree(
    context.repo({
      tree_sha: repository.default_branch,
      recursive: "true",
    })
  );

  const indexableFiles = tree.tree.filter(
    item => item.type === "blob" && isIndexableFile(item.path)
  );

  // Index in batches to avoid rate limits
  const BATCH_SIZE = 50;
  for (let i = 0; i < indexableFiles.length; i += BATCH_SIZE) {
    const batch = indexableFiles.slice(i, i + BATCH_SIZE);

    await Promise.all(
      batch.map(async file => {
        const { data } = await context.octokit.git.getBlob(
          context.repo({ file_sha: file.sha })
        );

        const content = Buffer.from(data.content, "base64").toString();

        await indexFile({
          repo: repository.full_name,
          path: file.path,
          content,
          sha: file.sha,
          language: detectLanguage(file.path),
        });
      })
    );

    // Respect rate limits
    await sleep(1000);
  }
}
```

### Symbol Extraction

```typescript
interface Symbol {
  name: string;
  kind: "function" | "class" | "method" | "variable" | "interface" | "type";
  file: string;
  line: number;
  signature?: string;
  docstring?: string;
}

async function extractSymbols(file: string, content: string, language: string): Promise<Symbol[]> {
  const symbols: Symbol[] = [];

  switch (language) {
    case "typescript":
    case "javascript":
      return extractJSSymbols(file, content);
    case "python":
      return extractPythonSymbols(file, content);
    case "go":
      return extractGoSymbols(file, content);
    default:
      return [];
  }
}

function extractJSSymbols(file: string, content: string): Symbol[] {
  const symbols: Symbol[] = [];
  const lines = content.split("\n");

  // Simple regex-based extraction (use AST parser for production)
  const patterns = [
    { regex: /^(?:export\s+)?(?:async\s+)?function\s+(\w+)/gm, kind: "function" as const },
    { regex: /^(?:export\s+)?class\s+(\w+)/gm, kind: "class" as const },
    { regex: /^(?:export\s+)?interface\s+(\w+)/gm, kind: "interface" as const },
    { regex: /^(?:export\s+)?type\s+(\w+)/gm, kind: "type" as const },
  ];

  for (const { regex, kind } of patterns) {
    let match;
    while ((match = regex.exec(content)) !== null) {
      const line = content.slice(0, match.index).split("\n").length;
      symbols.push({
        name: match[1],
        kind,
        file,
        line,
      });
    }
  }

  return symbols;
}
```

### Cross-Repository Reference Tracking

```typescript
interface Reference {
  sourceRepo: string;
  sourceFile: string;
  sourceLine: number;
  targetSymbol: string;
  targetRepo: string;
  targetFile: string;
}

async function findCrossRepoReferences(org: string, symbolName: string): Promise<Reference[]> {
  const references: Reference[] = [];

  // Search for imports/requires across all repos
  const importPatterns = [
    `from "${org}/`,
    `require("${org}/`,
    `import { ${symbolName} }`,
    `import ${symbolName} from`,
  ];

  for (const pattern of importPatterns) {
    const results = await searchIndex({
      org,
      query: pattern,
      type: "content",
    });

    for (const result of results) {
      references.push({
        sourceRepo: result.repo,
        sourceFile: result.path,
        sourceLine: result.line,
        targetSymbol: symbolName,
        targetRepo: "", // Resolve from import path
        targetFile: "", // Resolve from import path
      });
    }
  }

  return references;
}
```

### Dead Code Detection

```typescript
async function findDeadCode(context, repository) {
  // Get all exported symbols
  const exports = await getAllExports(repository.full_name);

  // Find which symbols are referenced
  const referenced = new Set<string>();

  for (const exp of exports) {
    const refs = await findReferences(repository.full_name, exp.name);

    // If referenced outside its own file, it's used
    const externalRefs = refs.filter(r => r.file !== exp.file);
    if (externalRefs.length > 0) {
      referenced.add(`${exp.file}:${exp.name}`);
    }
  }

  // Find unreferenced exports
  const deadCode = exports.filter(
    exp => !referenced.has(`${exp.file}:${exp.name}`)
  );

  return deadCode;
}
```

### Search Query Processing

```typescript
interface SearchQuery {
  terms: string[];
  language?: string;
  repo?: string;
  path?: string;
  type?: "symbol" | "content" | "file";
}

function parseSearchQuery(query: string): SearchQuery {
  const result: SearchQuery = { terms: [] };

  // Parse filters
  const filters = query.match(/(\w+):(\S+)/g) || [];
  for (const filter of filters) {
    const [key, value] = filter.split(":");
    switch (key) {
      case "lang":
      case "language":
        result.language = value;
        break;
      case "repo":
        result.repo = value;
        break;
      case "path":
        result.path = value;
        break;
      case "type":
        result.type = value as SearchQuery["type"];
        break;
    }
  }

  // Remaining terms
  const cleanQuery = query.replace(/\w+:\S+/g, "").trim();
  result.terms = cleanQuery.split(/\s+/).filter(Boolean);

  return result;
}

// Example usage:
// "parseJSON lang:typescript repo:my-app" ->
// { terms: ["parseJSON"], language: "typescript", repo: "my-app" }
```

## Indexing Strategies

### Inverted Index
```typescript
interface InvertedIndex {
  // term -> list of (repo, file, line) occurrences
  [term: string]: Array<{
    repo: string;
    file: string;
    line: number;
    score: number;
  }>;
}

function tokenize(content: string): string[] {
  // Split on non-alphanumeric, convert to lowercase
  return content
    .toLowerCase()
    .split(/[^a-z0-9]+/)
    .filter(token => token.length >= 2);
}

function camelCaseSplit(token: string): string[] {
  // parseJSON -> ["parse", "JSON", "parsejson"]
  const parts = token.split(/(?=[A-Z])/);
  return [...parts.map(p => p.toLowerCase()), token.toLowerCase()];
}
```

### Trigram Index
```typescript
function trigramTokenize(content: string): string[] {
  const trigrams: string[] = [];
  const normalized = content.toLowerCase();

  for (let i = 0; i < normalized.length - 2; i++) {
    trigrams.push(normalized.slice(i, i + 3));
  }

  return trigrams;
}

// Enables fuzzy matching: "pars" matches "parseJSON"
```

## Storage Backends

| Backend | Best For |
|---------|----------|
| Elasticsearch | Full-text search, scalable |
| Algolia | Fast, hosted search |
| Typesense | Open-source alternative |
| PostgreSQL + pg_trgm | Simple deployments |
| SQLite FTS5 | Single-node, embedded |

## Security Considerations

- **Respect repository visibility** - Don't index private repos publicly
- **Token scope validation** - Only index repos app has access to
- **Secure index storage** - Encrypt sensitive code
- **Audit search queries** - Track who searches what
- **Rate limit searches** - Prevent enumeration attacks

## Example Apps in This Category

- **Sourcegraph** - Universal code search
- **Hound** - Fast code search
- **OpenGrok** - Source code search engine
- **Livegrep** - Real-time code search

## Related Categories

- [IDEs](ides.md) - Editor integration
- [Code Quality](code-quality.md) - Code analysis
- [Monitoring](monitoring.md) - Usage analytics

## See Also

- [GitHub Code Search](https://docs.github.com/en/search-github/github-code-search/about-github-code-search)
- [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) - Parsing library
