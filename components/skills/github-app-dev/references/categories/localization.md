# Localization GitHub Apps

GitHub Apps that manage translation and localization workflows: i18n file management, translation synchronization, and localized content automation.

## Common Use Cases

- **Translation Management** - Sync with translation platforms
- **i18n File Validation** - Check translation completeness
- **Locale PR Creation** - Auto-create PRs for new translations
- **Translation Review** - Facilitate translation review workflow
- **Missing Key Detection** - Find untranslated strings
- **Plural/Format Validation** - Validate ICU/i18n formats

## Key Webhooks

| Webhook | Use Case |
|---------|----------|
| `push` | Detect i18n file changes |
| `pull_request.*` | Validate translations in PRs |
| `pull_request_review.submitted` | Track translation approvals |
| `issue_comment.created` | Translation discussion |
| `schedule` | Periodic sync with translation platforms |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Contents | Write | Update translation files |
| Pull requests | Write | Create translation PRs |
| Issues | Write | Track translation tasks |
| Checks | Write | Report validation results |

### Minimal Permission Set
```yaml
permissions:
  contents: write
  pull-requests: write
```

## Common Patterns

### Sync with Translation Platform

```typescript
app.on("push", async (context) => {
  const { ref, commits, repository, after } = context.payload;

  // Only sync from default branch
  if (ref !== `refs/heads/${repository.default_branch}`) return;

  // Check for source locale changes
  const sourceLocale = "en";
  const sourceFiles = commits.flatMap(c =>
    [...c.added, ...c.modified].filter(f =>
      f.includes(`/${sourceLocale}/`) || f.includes(`${sourceLocale}.json`)
    )
  );

  if (sourceFiles.length === 0) return;

  // Upload to translation platform
  for (const file of sourceFiles) {
    const content = await getFileContent(context, file, after);

    await translationPlatform.uploadSource({
      projectId: repository.full_name,
      file: file,
      content: JSON.parse(content),
      branch: repository.default_branch,
    });
  }

  // Notify of new strings
  const newStrings = await translationPlatform.getNewStrings(repository.full_name);

  if (newStrings.length > 0) {
    await context.octokit.issues.create(
      context.repo({
        title: `New strings for translation (${newStrings.length})`,
        body: `
The following strings need translation:

${newStrings.map(s => `- \`${s.key}\`: "${s.text}"`).join("\n")}

**Affected files**: ${sourceFiles.join(", ")}
        `,
        labels: ["translation", "needs-translation"],
      })
    );
  }
});
```

### Pull Translation Updates

```typescript
// Scheduled job to pull translations
async function pullTranslations(context, repository) {
  const locales = await translationPlatform.getLocales(repository.full_name);
  const updates: Array<{ locale: string; file: string; content: string }> = [];

  for (const locale of locales) {
    if (locale === "en") continue; // Skip source

    const translations = await translationPlatform.getTranslations({
      projectId: repository.full_name,
      locale,
      status: "approved",
    });

    for (const translation of translations) {
      updates.push({
        locale,
        file: translation.file.replace("/en/", `/${locale}/`),
        content: JSON.stringify(translation.content, null, 2),
      });
    }
  }

  if (updates.length === 0) return;

  // Create PR with updates
  const branchName = `translations-${Date.now()}`;

  await context.octokit.git.createRef(
    context.repo({
      ref: `refs/heads/${branchName}`,
      sha: repository.default_branch_sha,
    })
  );

  for (const update of updates) {
    await context.octokit.repos.createOrUpdateFileContents(
      context.repo({
        path: update.file,
        message: `chore(i18n): update ${update.locale} translations`,
        content: Buffer.from(update.content).toString("base64"),
        branch: branchName,
      })
    );
  }

  await context.octokit.pulls.create(
    context.repo({
      title: "Update translations from translation platform",
      head: branchName,
      base: repository.default_branch,
      body: `
## Translation Update

This PR includes translation updates from the translation platform.

### Updated Locales
${[...new Set(updates.map(u => u.locale))].map(l => `- ${l}`).join("\n")}

### Files Changed
${updates.map(u => `- ${u.file}`).join("\n")}
      `,
    })
  );
}
```

### Translation Completeness Check

```typescript
app.on("pull_request.opened", async (context) => {
  const { pull_request } = context.payload;

  // Get translation files changed
  const { data: files } = await context.octokit.pulls.listFiles(
    context.pullRequest({ per_page: 100 })
  );

  const translationFiles = files.filter(f =>
    f.filename.match(/locales?\/.*\.json$/) ||
    f.filename.match(/i18n\/.*\.json$/) ||
    f.filename.match(/translations?\/.*\.json$/)
  );

  if (translationFiles.length === 0) return;

  // Get source locale keys
  const sourceKeys = await getSourceLocaleKeys(context, pull_request.head.sha);

  // Check each translation file
  const results: LocaleCheckResult[] = [];

  for (const file of translationFiles) {
    const locale = extractLocale(file.filename);
    const content = await getFileContent(context, file.filename, pull_request.head.sha);
    const keys = Object.keys(flattenObject(JSON.parse(content)));

    const missing = sourceKeys.filter(k => !keys.includes(k));
    const extra = keys.filter(k => !sourceKeys.includes(k));

    results.push({
      locale,
      file: file.filename,
      total: sourceKeys.length,
      translated: keys.length,
      missing,
      extra,
      completeness: (keys.length / sourceKeys.length) * 100,
    });
  }

  // Create check run with results
  const allComplete = results.every(r => r.missing.length === 0);

  await context.octokit.checks.create(
    context.repo({
      name: "Translation Completeness",
      head_sha: pull_request.head.sha,
      status: "completed",
      conclusion: allComplete ? "success" : "neutral",
      output: {
        title: allComplete ? "All translations complete" : "Missing translations",
        summary: formatCompletenessReport(results),
      },
    })
  );
});

function formatCompletenessReport(results: LocaleCheckResult[]): string {
  return `
## Translation Status

| Locale | Completeness | Missing | Extra |
|--------|--------------|---------|-------|
${results.map(r => `| ${r.locale} | ${r.completeness.toFixed(1)}% | ${r.missing.length} | ${r.extra.length} |`).join("\n")}

${results.filter(r => r.missing.length > 0).map(r => `
### ${r.locale} - Missing Keys
${r.missing.slice(0, 10).map(k => `- \`${k}\``).join("\n")}
${r.missing.length > 10 ? `\n... and ${r.missing.length - 10} more` : ""}
`).join("\n")}
  `.trim();
}
```

### ICU Message Format Validation

```typescript
import { parse } from "@formatjs/icu-messageformat-parser";

app.on("push", async (context) => {
  const { commits, after, repository } = context.payload;

  const translationFiles = commits.flatMap(c =>
    [...c.added, ...c.modified].filter(f => f.match(/\.json$/))
  );

  const errors: FormatError[] = [];

  for (const file of translationFiles) {
    const content = await getFileContent(context, file, after);
    let translations;

    try {
      translations = JSON.parse(content);
    } catch {
      errors.push({ file, key: "", message: "Invalid JSON" });
      continue;
    }

    const flattened = flattenObject(translations);

    for (const [key, value] of Object.entries(flattened)) {
      if (typeof value !== "string") continue;

      try {
        // Validate ICU format
        parse(value, { requiresOtherClause: true });
      } catch (error) {
        errors.push({
          file,
          key,
          message: `Invalid ICU format: ${error.message}`,
        });
      }

      // Check for common issues
      const issues = validateTranslationString(value);
      for (const issue of issues) {
        errors.push({ file, key, message: issue });
      }
    }
  }

  if (errors.length > 0) {
    await context.octokit.repos.createCommitStatus(
      context.repo({
        sha: after,
        state: "failure",
        context: "i18n/validation",
        description: `${errors.length} translation format errors`,
      })
    );
  }
});

function validateTranslationString(value: string): string[] {
  const issues: string[] = [];

  // Check for unbalanced braces
  const openBraces = (value.match(/{/g) || []).length;
  const closeBraces = (value.match(/}/g) || []).length;
  if (openBraces !== closeBraces) {
    issues.push("Unbalanced braces");
  }

  // Check for HTML tags
  if (/<[^>]+>/.test(value)) {
    issues.push("Contains HTML tags - consider using rich text components");
  }

  // Check for hardcoded numbers
  if (/\d{4,}/.test(value)) {
    issues.push("Contains large numbers - consider using number formatting");
  }

  return issues;
}
```

### Locale-Specific PR Labels

```typescript
app.on("pull_request.opened", async (context) => {
  const { pull_request } = context.payload;

  const { data: files } = await context.octokit.pulls.listFiles(
    context.pullRequest({ per_page: 100 })
  );

  // Extract locales from file paths
  const locales = new Set<string>();

  for (const file of files) {
    const localeMatch = file.filename.match(/(?:locales?|i18n|translations?)\/([a-z]{2}(?:-[A-Z]{2})?)/);
    if (localeMatch) {
      locales.add(localeMatch[1]);
    }
  }

  // Add labels for each locale
  if (locales.size > 0) {
    const labels = Array.from(locales).map(l => `locale:${l}`);
    labels.push("i18n");

    await context.octokit.issues.addLabels(
      context.issue({ labels })
    );
  }
});
```

## Translation File Formats

| Format | Extension | Pattern |
|--------|-----------|---------|
| JSON | `.json` | Flat or nested key-value |
| YAML | `.yml` | Nested key-value |
| PO | `.po` | gettext format |
| XLIFF | `.xlf` | XML-based |
| ARB | `.arb` | Flutter/Dart format |
| Properties | `.properties` | Java format |

## Integration Platforms

| Platform | API Type | Best For |
|----------|----------|----------|
| Crowdin | REST API | Large projects |
| Lokalise | REST API | Developers |
| Transifex | REST API | Open source |
| Phrase | REST API | Enterprise |
| Weblate | Self-hosted | Privacy-focused |
| POEditor | REST API | Simple projects |

## Security Considerations

- **Validate file paths** - Prevent path traversal
- **Sanitize content** - Don't execute translation strings
- **API key management** - Secure translation platform keys
- **Access control** - Limit who can push translations
- **Review translations** - Malicious strings possible

## Example Apps in This Category

- **Crowdin GitHub Integration** - Sync with Crowdin
- **Lokalise** - Translation management
- **GitLocalize** - GitHub-native translation

## Related Categories

- [Code Quality](code-quality.md) - Format validation
- [Utilities](utilities.md) - Automation tools

## See Also

- [ICU Message Format](https://unicode-org.github.io/icu/userguide/format_parse/messages/)
- [i18next](https://www.i18next.com/)
- [FormatJS](https://formatjs.io/)
