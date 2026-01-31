# Recurse ML Rules

This directory contains rules for Recurse ML to use during PR analysis.

`rml-verify.md` is a special case here.
It instructs an agentic IDE to use Recurse ML's CLI for code verification.
See [this excellent blogpost](https://blog.continue.dev/recurse-ml-rules-that-enable-async-context-engineering-with-kids-around/) for an example use case.

## Quickstart

See [the docs](https://docs.recurse.ml/gh/configs/rules/) for info on Recurse ML rules and configuration instructions.
The [release blogpost](https://blog.recurse.ml/rules) provides more details on how to use rules in production.

### rml (CLI)

Get started with these rules using the [CLI tool](https://docs.recurse.ml/rml/):

1. **Install rml**: Run the installation command:
   ```bash
   curl install.recurse.ml | sh
   ```

2. **Create configuration file**: Add a `.recurseml.yaml` file to your project root with the rules directory specified:
   ```yaml
   rules: .rules/
   ```

3. **Create rules directory**: Make a `.rules/` directory in your project (or use any directory name you prefer).

4. **Copy rules**: Copy the rule files from this directory into your `.rules/` directory. You can copy all rules or select specific ones that match your project's needs.

5. **Run analysis**: Execute `rml` in your project directory. Rules will be reported along with regular issues in the CLI output.

### GitHub App

Get started with these rules using the GitHub App:

1. **Install GitHub App**: Install the [Recurse ML GitHub App](https://github.com/marketplace/recurse-ml) on your repository.

2. **Create configuration file**: Add a `.recurseml.yaml` file to your project root with the rules directory specified:
   ```yaml
   rules: .rules/
   ```

3. **Create rules directory**: Make a `.rules/` directory in your project (or use any directory name you prefer).

4. **Copy rules**: Copy the rule files from this directory into your `.rules/` directory. You can copy all rules or select specific ones that match your project's needs.

5. **Create PR**: When you create a pull request, Recurse ML will automatically analyze your changes and report rule violations in PR comments.



## Rules

`bare_exceptions.md:` Avoid catching bare exceptions without specifying the exception type to prevent masking unintended errors.

`bool.md:` Break down complex boolean expressions into smaller, readable parts using intermediate variables or helper functions.

`effective_comments.md:` Write comments that explain why code does something rather than what it does, avoiding redundant explanations.

`explicit_conditionals.md:` Use explicit conditional checks for lists, None values, and other truthiness evaluations instead of implicit checks.

`flow.md:` Keep code execution flow simple and sequential by avoiding deeply nested conditions and convoluted control structures.

`infinite_loops.md:` Ensure all loops have proper termination conditions to prevent programs from hanging or consuming excessive resources.

`mutable_defaults.md:` Avoid using mutable objects as default function arguments since they persist between function calls and cause unexpected behavior.

`side_effects.md:` Functions should not have unexpected mutability side effects that modify input arguments without clear indication.

`typing.md:` Use built-in types over typing module types, prefer Optional for optional types, and never ignore type errors.

`uncreachable_code.md:` Remove code that can never be executed due to control flow issues like statements after return or within impossible conditions.

