# Skill Gap Detection

Proactively identify missing skills and improve existing ones.

## At Task Start

When beginning any implementation task:

1. **Identify domains** - List languages, platforms, tools, and patterns involved
2. **Check skill coverage** - For each domain, verify a matching skill exists
3. **Flag gaps** - If no skill covers a domain, inform the user:
   ```
   No skill found for <domain>. Create one?
   - Yes: Create issue in aRustyDev/ai + local todo
   - No: Proceed without skill
   ```

## Domain Detection Patterns

| User Request Contains | Expected Skill Pattern |
|-----------------------|------------------------|
| Language (Zig, Rust, Python) | `lang-<lang>-*` |
| Platform (AWS, GCP, Cloudflare) | `cloud-<platform>-*` or `<platform>-*` |
| Tool (Terraform, Docker, Helm) | `<tool>-*` or `iac-<tool>-*` |
| Pattern (SDK, CLI, library) | `meta-<pattern>-*` or `<domain>-<pattern>-*` |
| Service (OpenMetadata, Stripe) | `<service>-*` |

## Gap Response Workflow

When user confirms gap creation:

1. **Create GitHub issue** in `aRustyDev/ai`:
   ```
   Title: feat(skills): add <skill-name> skill
   Body: Identified during task: "<brief context>"
   Labels: enhancement, skills
   ```

2. **Add local todo** to track during session

3. **Continue with task** - Don't block on skill creation

## At Task End

Review skill effectiveness (see `meta-skill-gaps-dev` for methodology):

- Were loaded skills useful?
- Was context wasted on unused sections?
- Did user need knowledge the skill lacked?
- Should a derivative skill exist?

Flag issues for later refinement rather than interrupting the user.
