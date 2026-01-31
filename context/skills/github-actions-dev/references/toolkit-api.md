# GitHub Actions Toolkit API Reference

Complete reference for the `@actions/*` packages used to build GitHub Actions.

## Package Overview

| Package | Purpose | Install |
|---------|---------|---------|
| `@actions/core` | Inputs, outputs, logging, failure | Required |
| `@actions/github` | GitHub API client, context | Common |
| `@actions/exec` | Run shell commands | Common |
| `@actions/io` | File system operations | Common |
| `@actions/cache` | Caching dependencies | Optional |
| `@actions/tool-cache` | Download and cache tools | Optional |
| `@actions/artifact` | Upload/download artifacts | Optional |
| `@actions/glob` | File pattern matching | Optional |
| `@actions/http-client` | HTTP requests | Optional |

## @actions/core

### Inputs

```typescript
import * as core from '@actions/core';

// Required input (throws if missing)
const token = core.getInput('token', { required: true });

// Optional input (returns empty string if missing)
const optional = core.getInput('optional-param');

// With trimming disabled
const raw = core.getInput('content', { trimWhitespace: false });

// Multiline input (returns array)
const items = core.getMultilineInput('items');
// For input: "item1\nitem2\nitem3" → ['item1', 'item2', 'item3']

// Boolean input (handles 'true', 'True', 'TRUE', etc.)
const debug = core.getBooleanInput('debug');
```

### Outputs

```typescript
// Set output for use by other steps
core.setOutput('version', '1.2.3');
core.setOutput('artifact-url', 'https://...');

// Complex objects (will be JSON stringified)
core.setOutput('results', { passed: 10, failed: 2 });
```

### Logging

```typescript
// Standard logging
core.debug('Detailed debug info');     // Only with ACTIONS_STEP_DEBUG=true
core.info('General information');
core.notice('Notable but not error');
core.warning('Something might be wrong');
core.error('Something is definitely wrong');

// Annotations with file location
core.error('Syntax error', {
  file: 'src/index.ts',
  startLine: 10,
  endLine: 10,
  startColumn: 5,
  endColumn: 20
});

core.warning('Deprecated API usage', {
  file: 'src/api.ts',
  startLine: 25
});

// Log grouping
core.startGroup('Installing dependencies');
core.info('Running npm ci...');
core.endGroup();

// Async group
await core.group('Build', async () => {
  await exec.exec('npm', ['run', 'build']);
});
```

### State and Environment

```typescript
// Save state between main and post scripts
core.saveState('pid', process.pid.toString());

// Retrieve in post script
const pid = core.getState('pid');

// Export environment variable for subsequent steps
core.exportVariable('MY_VAR', 'value');
core.exportVariable('MY_JSON', JSON.stringify({ key: 'value' }));

// Add to PATH
core.addPath('/custom/bin');

// Mask sensitive value in logs
core.setSecret(apiKey);
```

### Failure

```typescript
// Mark action as failed (sets exit code 1)
core.setFailed('Action failed: reason');

// Often used in catch block
try {
  await run();
} catch (error) {
  core.setFailed(error instanceof Error ? error.message : 'Unknown error');
}
```

### Summary (Job Summary)

```typescript
// Add markdown to job summary
await core.summary
  .addHeading('Test Results')
  .addTable([
    [{ data: 'Test', header: true }, { data: 'Result', header: true }],
    ['Unit Tests', '✅ Passed'],
    ['Integration', '✅ Passed']
  ])
  .addBreak()
  .addLink('View Report', 'https://example.com/report')
  .addCodeBlock('console.log("hello")', 'javascript')
  .write();

// Or build incrementally
core.summary.addRaw('# Summary\n');
core.summary.addRaw('All tests passed!\n');
await core.summary.write();
```

## @actions/github

### Context

```typescript
import * as github from '@actions/github';

// Repository info
const { owner, repo } = github.context.repo;

// Commit/ref info
const sha = github.context.sha;           // Full SHA
const ref = github.context.ref;           // refs/heads/main
const branch = github.context.ref.replace('refs/heads/', '');

// Actor and event
const actor = github.context.actor;       // Username who triggered
const eventName = github.context.eventName; // push, pull_request, etc.

// Run info
const runId = github.context.runId;
const runNumber = github.context.runNumber;
const workflow = github.context.workflow;
const job = github.context.job;
const action = github.context.action;     // Action identifier

// Event payload (type depends on event)
const payload = github.context.payload;

// For pull_request events
if (github.context.eventName === 'pull_request') {
  const pr = github.context.payload.pull_request;
  const prNumber = pr?.number;
  const prTitle = pr?.title;
  const prBody = pr?.body;
}

// For issue events
if (github.context.eventName === 'issues') {
  const issue = github.context.payload.issue;
  const issueNumber = issue?.number;
}
```

### Octokit Client

```typescript
// Create authenticated client
const octokit = github.getOctokit(token);

// REST API calls
const { data: issue } = await octokit.rest.issues.get({
  owner,
  repo,
  issue_number: 1
});

const { data: pr } = await octokit.rest.pulls.get({
  owner,
  repo,
  pull_number: 123
});

// Create comment
await octokit.rest.issues.createComment({
  owner,
  repo,
  issue_number: prNumber,
  body: 'Thanks for your contribution!'
});

// GraphQL queries
const { repository } = await octokit.graphql<{
  repository: { id: string }
}>(`
  query($owner: String!, $name: String!) {
    repository(owner: $owner, name: $name) {
      id
    }
  }
`, { owner, name: repo });

// Pagination
const issues = await octokit.paginate(octokit.rest.issues.listForRepo, {
  owner,
  repo,
  state: 'open',
  per_page: 100
});
```

## @actions/exec

```typescript
import * as exec from '@actions/exec';

// Simple execution
const exitCode = await exec.exec('npm', ['install']);

// With options
await exec.exec('npm', ['test'], {
  cwd: './packages/core',
  env: { ...process.env, NODE_ENV: 'test' },
  silent: true,  // Suppress stdout/stderr
  ignoreReturnCode: true  // Don't throw on non-zero exit
});

// Capture output
let stdout = '';
let stderr = '';
const options: exec.ExecOptions = {
  listeners: {
    stdout: (data: Buffer) => {
      stdout += data.toString();
    },
    stderr: (data: Buffer) => {
      stderr += data.toString();
    }
  }
};

await exec.exec('git', ['rev-parse', 'HEAD'], options);
console.log(`SHA: ${stdout.trim()}`);

// Get output directly
const { stdout: version } = await exec.getExecOutput('node', ['--version']);
console.log(`Node version: ${version.trim()}`);
```

## @actions/io

```typescript
import * as io from '@actions/io';

// Create directory (recursive)
await io.mkdirP('/path/to/deep/dir');

// Copy file or directory
await io.cp('source.txt', 'dest.txt');
await io.cp('src-dir', 'dest-dir', { recursive: true });

// Move/rename
await io.mv('old-name.txt', 'new-name.txt');

// Remove file or directory
await io.rmRF('/path/to/remove');

// Find tool in PATH
const nodePath = await io.which('node');         // Returns path or empty string
const npmPath = await io.which('npm', true);     // Throws if not found
```

## @actions/tool-cache

```typescript
import * as tc from '@actions/tool-cache';

// Download file
const downloadPath = await tc.downloadTool('https://example.com/tool.tar.gz');

// Extract archives
const extractedFolder = await tc.extractTar(downloadPath);
// Also: extractZip, extractXar, extract7z

// Cache tool for future runs
const cachedPath = await tc.cacheDir(extractedFolder, 'mytool', '1.0.0');

// Find cached tool
const toolPath = tc.find('mytool', '1.0.0');
if (toolPath) {
  core.addPath(toolPath);
} else {
  // Download and cache
}

// Find with version range
const cachedTool = tc.find('mytool', '1.x');
```

## @actions/artifact

```typescript
import * as artifact from '@actions/artifact';

const client = artifact.create();

// Upload artifact
await client.uploadArtifact(
  'my-artifact',           // Name
  ['dist/**/*', 'package.json'],  // Files
  '.',                     // Root directory
  { continueOnError: true }
);

// Download artifact
const downloadResponse = await client.downloadArtifact('my-artifact', './download');
console.log(`Downloaded to: ${downloadResponse.downloadPath}`);

// Download all artifacts
await client.downloadAllArtifacts('./artifacts');
```

## @actions/glob

```typescript
import * as glob from '@actions/glob';

// Create globber
const globber = await glob.create('**/*.ts\n!node_modules/**');

// Get matching files
const files = await globber.glob();

// Stream for large result sets
for await (const file of globber.globGenerator()) {
  console.log(file);
}

// Hash files (useful for cache keys)
const hash = await glob.hashFiles('**/package-lock.json');
```

## @actions/http-client

```typescript
import * as http from '@actions/http-client';

const client = new http.HttpClient('my-action');

// GET request
const response = await client.get('https://api.example.com/data');
const body = await response.readBody();
const data = JSON.parse(body);

// POST with JSON
const postResponse = await client.postJson<ResponseType>(
  'https://api.example.com/submit',
  { key: 'value' }
);
console.log(postResponse.result);

// With headers
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};
const authClient = new http.HttpClient('my-action', [], { headers });
```
