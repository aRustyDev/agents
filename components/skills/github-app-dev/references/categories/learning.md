# Learning GitHub Apps

GitHub Apps that support educational use cases: coding tutorials, course management, student assessments, and interactive learning experiences.

## Common Use Cases

- **Assignment Distribution** - Distribute coding assignments
- **Automated Grading** - Grade submissions automatically
- **Code Feedback** - Provide learning-oriented feedback
- **Progress Tracking** - Monitor student progress
- **Classroom Management** - Organize student repositories
- **Interactive Tutorials** - Step-by-step code lessons

## Key Webhooks

| Webhook | Use Case |
|---------|----------|
| `push` | Detect student submissions |
| `pull_request.opened` | Submission via PR |
| `repository.created` | New student repo |
| `issues.opened` | Student questions |
| `issue_comment.created` | Student-teacher interaction |
| `check_run.completed` | Test results |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Contents | Read/Write | Access student code, provide feedback |
| Issues | Write | Create feedback issues |
| Pull requests | Write | Review submissions |
| Checks | Write | Report test results |
| Administration | Read | Access classroom org |

### Minimal Permission Set
```yaml
permissions:
  contents: read
  checks: write
```

### Full Classroom Set
```yaml
permissions:
  contents: write
  issues: write
  pull-requests: write
  checks: write
  administration: read
```

## Common Patterns

### Assignment Distribution

```typescript
interface Assignment {
  id: string;
  title: string;
  templateRepo: string;
  dueDate: Date;
  maxPoints: number;
  testFile: string;
}

async function distributeAssignment(
  context,
  classroom: string,
  assignment: Assignment,
  students: string[]
) {
  for (const student of students) {
    const repoName = `${assignment.id}-${student}`;

    // Create repo from template
    await context.octokit.repos.createUsingTemplate({
      template_owner: classroom,
      template_repo: assignment.templateRepo,
      owner: classroom,
      name: repoName,
      private: true,
    });

    // Add student as collaborator
    await context.octokit.repos.addCollaborator({
      owner: classroom,
      repo: repoName,
      username: student,
      permission: "push",
    });

    // Create assignment issue
    await context.octokit.issues.create({
      owner: classroom,
      repo: repoName,
      title: `📚 ${assignment.title}`,
      body: `
## Assignment: ${assignment.title}

**Due Date**: ${assignment.dueDate.toLocaleDateString()}
**Max Points**: ${assignment.maxPoints}

### Instructions
1. Clone this repository
2. Complete the tasks in the assignment files
3. Push your changes before the due date

### Grading
Your submission will be automatically graded when you push. Check the "Actions" tab for test results.

Good luck! 🍀
      `,
    });

    // Notify student
    await sendNotification(student, {
      type: "assignment",
      title: assignment.title,
      repo: `${classroom}/${repoName}`,
    });
  }
}
```

### Automated Grading

```typescript
app.on("push", async (context) => {
  const { repository, ref, after, pusher } = context.payload;

  // Check if this is a student assignment repo
  const assignment = await getAssignmentForRepo(repository.name);
  if (!assignment) return;

  // Don't grade instructor pushes
  if (await isInstructor(pusher.name)) return;

  // Create check run
  const { data: check } = await context.octokit.checks.create(
    context.repo({
      name: "Assignment Grader",
      head_sha: after,
      status: "in_progress",
    })
  );

  try {
    // Run tests
    const testResults = await runAssignmentTests(context, after, assignment);

    // Calculate grade
    const grade = calculateGrade(testResults, assignment.maxPoints);

    // Update check run with detailed feedback
    await context.octokit.checks.update(
      context.repo({
        check_run_id: check.id,
        status: "completed",
        conclusion: grade.percentage >= 60 ? "success" : "failure",
        output: {
          title: `Grade: ${grade.points}/${assignment.maxPoints} (${grade.percentage}%)`,
          summary: generateGradeSummary(testResults, grade),
          annotations: testResults.failures.map(failure => ({
            path: failure.file,
            start_line: failure.line,
            end_line: failure.line,
            annotation_level: "warning",
            message: failure.message,
            title: failure.testName,
          })),
        },
      })
    );

    // Record grade
    await recordGrade({
      student: extractStudentFromRepo(repository.name),
      assignment: assignment.id,
      points: grade.points,
      maxPoints: assignment.maxPoints,
      submittedAt: new Date(),
      sha: after,
    });

    // Check for late submission
    if (new Date() > assignment.dueDate) {
      await context.octokit.issues.createComment({
        owner: repository.owner.login,
        repo: repository.name,
        issue_number: 1, // Assignment issue
        body: `⚠️ **Late Submission**\n\nThis submission was received after the due date. Late penalty may apply.`,
      });
    }
  } catch (error) {
    await context.octokit.checks.update(
      context.repo({
        check_run_id: check.id,
        status: "completed",
        conclusion: "failure",
        output: {
          title: "Grading Failed",
          summary: `Error running tests: ${error.message}`,
        },
      })
    );
  }
});

function generateGradeSummary(results: TestResults, grade: Grade): string {
  return `
## Test Results

| Category | Passed | Failed | Points |
|----------|--------|--------|--------|
${results.categories.map(cat =>
  `| ${cat.name} | ${cat.passed} | ${cat.failed} | ${cat.points}/${cat.maxPoints} |`
).join("\n")}

**Total**: ${grade.points}/${grade.maxPoints}

### Passing Tests
${results.passed.map(t => `- ✅ ${t.name}`).join("\n") || "None"}

### Failing Tests
${results.failures.map(t => `- ❌ ${t.name}: ${t.message}`).join("\n") || "None"}

### Suggestions for Improvement
${generateSuggestions(results)}
  `.trim();
}
```

### Educational Feedback

```typescript
app.on("pull_request.opened", async (context) => {
  const { pull_request, repository } = context.payload;

  // Check if educational repo
  const isEducational = await isEducationalRepo(repository);
  if (!isEducational) return;

  // Get changed files
  const { data: files } = await context.octokit.pulls.listFiles(
    context.pullRequest({ per_page: 100 })
  );

  const feedback = [];

  for (const file of files) {
    // Analyze code for learning opportunities
    const content = await getFileContent(context, file.filename, pull_request.head.sha);
    const suggestions = await analyzeForLearning(content, file.filename);

    for (const suggestion of suggestions) {
      feedback.push({
        path: file.filename,
        line: suggestion.line,
        side: "RIGHT",
        body: formatEducationalFeedback(suggestion),
      });
    }
  }

  if (feedback.length > 0) {
    // Create educational review
    await context.octokit.pulls.createReview(
      context.pullRequest({
        event: "COMMENT",
        body: "Here's some feedback to help you learn! 📚",
        comments: feedback.slice(0, 20),
      })
    );
  }
});

function formatEducationalFeedback(suggestion: LearningPoint): string {
  return `
### 💡 Learning Opportunity: ${suggestion.concept}

${suggestion.message}

**Why this matters**: ${suggestion.explanation}

**Example**:
\`\`\`${suggestion.language}
${suggestion.example}
\`\`\`

📖 [Learn more](${suggestion.resourceUrl})
  `.trim();
}
```

### Progress Dashboard

```typescript
interface StudentProgress {
  student: string;
  assignments: Array<{
    id: string;
    status: "not_started" | "in_progress" | "submitted" | "graded";
    grade?: number;
    maxPoints: number;
    attempts: number;
  }>;
  overallGrade: number;
}

async function generateProgressReport(classroom: string): Promise<StudentProgress[]> {
  const students = await getClassroomStudents(classroom);
  const assignments = await getClassroomAssignments(classroom);

  const progress: StudentProgress[] = [];

  for (const student of students) {
    const studentProgress: StudentProgress = {
      student: student.login,
      assignments: [],
      overallGrade: 0,
    };

    for (const assignment of assignments) {
      const repo = `${assignment.id}-${student.login}`;
      const grade = await getGrade(classroom, repo);

      studentProgress.assignments.push({
        id: assignment.id,
        status: grade ? "graded" : await getSubmissionStatus(classroom, repo),
        grade: grade?.points,
        maxPoints: assignment.maxPoints,
        attempts: await getAttemptCount(classroom, repo),
      });
    }

    // Calculate overall grade
    const totalPoints = studentProgress.assignments.reduce(
      (sum, a) => sum + (a.grade || 0), 0
    );
    const totalMax = studentProgress.assignments.reduce(
      (sum, a) => sum + a.maxPoints, 0
    );
    studentProgress.overallGrade = (totalPoints / totalMax) * 100;

    progress.push(studentProgress);
  }

  return progress;
}
```

### Interactive Tutorial Bot

```typescript
interface TutorialStep {
  id: string;
  title: string;
  instructions: string;
  hint?: string;
  solution?: string;
  validation: (code: string) => boolean;
}

app.on("issue_comment.created", async (context) => {
  const { comment, issue, repository } = context.payload;

  // Check for tutorial commands
  if (!comment.body.startsWith("/")) return;

  const [command, ...args] = comment.body.slice(1).split(" ");

  switch (command) {
    case "hint":
      const currentStep = await getCurrentStep(repository.name);
      if (currentStep?.hint) {
        await context.octokit.issues.createComment(
          context.issue({ body: `💡 **Hint**: ${currentStep.hint}` })
        );
      }
      break;

    case "check":
      await checkProgress(context, repository.name);
      break;

    case "next":
      await advanceToNextStep(context, repository.name);
      break;

    case "reset":
      await resetToStep(context, repository.name, args[0] || "1");
      break;

    case "solution":
      const step = await getCurrentStep(repository.name);
      if (step?.solution) {
        await context.octokit.issues.createComment(
          context.issue({
            body: `<details><summary>🔓 Solution (click to reveal)</summary>\n\n\`\`\`\n${step.solution}\n\`\`\`\n\n</details>`,
          })
        );
      }
      break;
  }
});

async function checkProgress(context, repoName: string) {
  const step = await getCurrentStep(repoName);
  const code = await getStudentCode(context, step.targetFile);

  const passed = step.validation(code);

  await context.octokit.issues.createComment(
    context.issue({
      body: passed
        ? `✅ **Great job!** You've completed "${step.title}"!\n\nType \`/next\` to continue.`
        : `❌ **Not quite right.** Review the instructions and try again.\n\nType \`/hint\` for a hint.`,
    })
  );
}
```

## Security Considerations

- **Student privacy** - Protect student work and grades
- **Fair grading** - Prevent tampering with tests
- **Isolation** - Sandbox test execution
- **Academic integrity** - Detect plagiarism
- **Access control** - Students can't see others' work

## Example Apps in This Category

- **GitHub Classroom** - Official education platform
- **Replit** - Online coding environment
- **CodeGrade** - Automated grading platform
- **Gradescope** - Assignment grading

## Related Categories

- [Testing](testing.md) - Automated tests
- [Code Quality](code-quality.md) - Code analysis
- [Code Review](code-review.md) - Feedback mechanisms

## See Also

- [GitHub Classroom](https://classroom.github.com/)
- [GitHub Education](https://education.github.com/)
- [Git for Education](https://git-scm.com/book/en/v2/Git-and-Other-Systems-Git-as-a-Client)
