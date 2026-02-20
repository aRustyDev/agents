"""TypeScript synthesizer for the IR extraction/synthesis pipeline.

This package synthesizes TypeScript source code from the 5-layer IR representation,
generating valid TypeScript with proper:

- Type annotations and generics
- Interface and type alias definitions
- Import/export statements
- Class definitions with decorators
- Async/await syntax
- ESLint integration for code quality

Example:
    from ir_synthesize_typescript import TypeScriptSynthesizer
    from ir_core.base import SynthConfig, OutputFormat

    synthesizer = TypeScriptSynthesizer()
    code = synthesizer.synthesize(ir, SynthConfig(
        output_format=OutputFormat.FORMATTED,
        target_version="ES2022",
    ))

    # Lint the generated code
    lint_result = synthesizer.lint(code)
    if not lint_result.success:
        for issue in lint_result.issues:
            print(f"{issue.line}:{issue.column} - {issue.rule}: {issue.message}")

    print(code)
"""

from ir_synthesize_typescript.linter import (
    ESLinter,
    ESLintConfig,
    LintIssue,
    LintResult,
    LintSeverity,
    lint_typescript,
)
from ir_synthesize_typescript.synthesizer import TypeScriptSynthesizer

__all__ = [
    "TypeScriptSynthesizer",
    "ESLinter",
    "ESLintConfig",
    "LintIssue",
    "LintResult",
    "LintSeverity",
    "lint_typescript",
]
__version__ = "0.1.0"
