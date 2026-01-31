---
name: context-optimization
description: Apply optimization techniques to extend effective context capacity. Use when context limits constrain agent performance, optimizing for cost or latency, implementing long-running agent systems, agents exhaust memory, or when designing conversation summarization strategies.
---

# Context Optimization Techniques

Context optimization extends the effective capacity of limited context windows through strategic compression, masking, caching, and partitioning. The goal is not to magically increase context windows but to make better use of available capacity. Effective optimization can double or triple effective context capacity without requiring larger models or longer contexts.

## When to Activate

Activate this skill when:
- Context limits constrain task complexity
- Optimizing for cost reduction (fewer tokens = lower costs)
- Reducing latency for long conversations
- Implementing long-running agent systems
- Needing to handle larger documents or conversations
- Building production systems at scale
- Agent sessions exceed context window limits
- Codebases exceed context windows (5M+ token systems)
- Designing conversation summarization strategies
- Debugging cases where agents "forget" what files they modified

## Core Concepts

Context optimization extends effective capacity through four primary strategies: compaction (summarizing context near limits), observation masking (replacing verbose outputs with references), KV-cache optimization (reusing cached computations), and context partitioning (splitting work across isolated contexts).

The key insight is that context quality matters more than quantity. Optimization preserves signal while reducing noise. The art lies in selecting what to keep versus what to discard, and when to apply each technique.

## Detailed Topics

### Compaction Strategies

**What is Compaction**
Compaction is the practice of summarizing context contents when approaching limits, then reinitializing a new context window with the summary. This distills the contents of a context window in a high-fidelity manner, enabling the agent to continue with minimal performance degradation.

Compaction typically serves as the first lever in context optimization. The art lies in selecting what to keep versus what to discard.

**Why Tokens-Per-Task Matters**
Traditional compression metrics target tokens-per-request. This is the wrong optimization. When compression loses critical details like file paths or error messages, the agent must re-fetch information, re-explore approaches, and waste tokens recovering context.

The right metric is tokens-per-task: total tokens consumed from task start to completion. A compression strategy saving 0.5% more tokens but causing 20% more re-fetching costs more overall.

**Three Production-Ready Compression Approaches**

1. **Anchored Iterative Summarization**: Maintain structured, persistent summaries with explicit sections for session intent, file modifications, decisions, and next steps. When compression triggers, summarize only the newly-truncated span and merge with the existing summary. Structure forces preservation by dedicating sections to specific information types.

2. **Opaque Compression**: Produce compressed representations optimized for reconstruction fidelity. Achieves highest compression ratios (99%+) but sacrifices interpretability. Cannot verify what was preserved.

3. **Regenerative Full Summary**: Generate detailed structured summaries on each compression. Produces readable output but may lose details across repeated compression cycles due to full regeneration rather than incremental merging.

The critical insight: structure forces preservation. Dedicated sections act as checklists that the summarizer must populate, preventing silent information drift.

**Compression Ratio Considerations**

| Method | Compression Ratio | Quality Score | Trade-off |
|--------|-------------------|---------------|-----------|
| Anchored Iterative | 98.6% | 3.70 | Best quality, slightly less compression |
| Regenerative | 98.7% | 3.44 | Good quality, moderate compression |
| Opaque | 99.3% | 3.35 | Best compression, quality loss |

The 0.7% additional tokens retained by structured summarization buys 0.35 quality points. For any task where re-fetching costs matter, this trade-off favors structured approaches.

**The Artifact Trail Problem**
Artifact trail integrity is the weakest dimension across all compression methods, scoring 2.2-2.5 out of 5.0 in evaluations. Even structured summarization with explicit file sections struggles to maintain complete file tracking across long sessions.

Coding agents need to know:
- Which files were created
- Which files were modified and what changed
- Which files were read but not changed
- Function names, variable names, error messages

This problem likely requires specialized handling beyond general summarization: a separate artifact index or explicit file-state tracking in agent scaffolding.

**Structured Summary Sections**
Effective structured summaries include explicit sections:

```markdown
## Session Intent
[What the user is trying to accomplish]

## Files Modified
- auth.controller.ts: Fixed JWT token generation
- config/redis.ts: Updated connection pooling

## Decisions Made
- Using Redis connection pool instead of per-request connections
- Retry logic with exponential backoff for transient failures

## Current State
- 14 tests passing, 2 failing

## Next Steps
1. Fix remaining test failures
2. Run full test suite
```

This structure prevents silent loss of file paths or decisions because each section must be explicitly addressed.

**Compression Trigger Strategies**

| Strategy | Trigger Point | Trade-off |
|----------|---------------|-----------|
| Fixed threshold | 70-80% context utilization | Simple but may compress too early |
| Sliding window | Keep last N turns + summary | Predictable context size |
| Importance-based | Compress low-relevance sections first | Complex but preserves signal |
| Task-boundary | Compress at logical task completions | Clean summaries but unpredictable timing |

The sliding window approach with structured summaries provides the best balance of predictability and quality for most coding agent use cases.

**Summary Generation by Message Type**
Effective summaries preserve different elements depending on message type:

Tool outputs: Preserve key findings, metrics, and conclusions. Remove verbose raw output.

Conversational turns: Preserve key decisions, commitments, and context shifts. Remove filler and back-and-forth.

Retrieved documents: Preserve key facts and claims. Remove supporting evidence and elaboration.

**When to Use Each Compression Approach**

Use anchored iterative summarization when:
- Sessions are long-running (100+ messages)
- File tracking matters (coding, debugging)
- You need to verify what was preserved

Use opaque compression when:
- Maximum token savings required
- Sessions are relatively short
- Re-fetching costs are low

Use regenerative summaries when:
- Summary interpretability is critical
- Sessions have clear phase boundaries
- Full context review is acceptable on each compression

### Observation Masking

**The Observation Problem**
Tool outputs can comprise 80%+ of token usage in agent trajectories. Much of this is verbose output that has already served its purpose. Once an agent has used a tool output to make a decision, keeping the full output provides diminishing value while consuming significant context.

Observation masking replaces verbose tool outputs with compact references. The information remains accessible if needed but does not consume context continuously.

**Masking Strategy Selection**
Not all observations should be masked equally:

Never mask: Observations critical to current task, observations from the most recent turn, observations used in active reasoning.

Consider masking: Observations from 3+ turns ago, verbose outputs with key points extractable, observations whose purpose has been served.

Always mask: Repeated outputs, boilerplate headers/footers, outputs already summarized in conversation.

### KV-Cache Optimization

**Understanding KV-Cache**
The KV-cache stores Key and Value tensors computed during inference, growing linearly with sequence length. Caching the KV-cache across requests sharing identical prefixes avoids recomputation.

Prefix caching reuses KV blocks across requests with identical prefixes using hash-based block matching. This dramatically reduces cost and latency for requests with common prefixes like system prompts.

**Cache Optimization Patterns**
Optimize for caching by reordering context elements to maximize cache hits. Place stable elements first (system prompt, tool definitions), then frequently reused elements, then unique elements last.

Design prompts to maximize cache stability: avoid dynamic content like timestamps, use consistent formatting, keep structure stable across sessions.

### Context Partitioning

**Sub-Agent Partitioning**
The most aggressive form of context optimization is partitioning work across sub-agents with isolated contexts. Each sub-agent operates in a clean context focused on its subtask without carrying accumulated context from other subtasks.

This approach achieves separation of concerns—the detailed search context remains isolated within sub-agents while the coordinator focuses on synthesis and analysis.

**Result Aggregation**
Aggregate results from partitioned subtasks by validating all partitions completed, merging compatible results, and summarizing if still too large.

### Budget Management

**Context Budget Allocation**
Design explicit context budgets. Allocate tokens to categories: system prompt, tool definitions, retrieved docs, message history, and reserved buffer. Monitor usage against budget and trigger optimization when approaching limits.

**Trigger-Based Optimization**
Monitor signals for optimization triggers: token utilization above 80%, degradation indicators, and performance drops. Apply appropriate optimization techniques based on context composition.

### Probe-Based Compression Evaluation

Traditional metrics like ROUGE or embedding similarity fail to capture functional compression quality. A summary may score high on lexical overlap while missing the one file path the agent needs.

Probe-based evaluation directly measures functional quality by asking questions after compression:

| Probe Type | What It Tests | Example Question |
|------------|---------------|------------------|
| Recall | Factual retention | "What was the original error message?" |
| Artifact | File tracking | "Which files have we modified?" |
| Continuation | Task planning | "What should we do next?" |
| Decision | Reasoning chain | "What did we decide about the Redis issue?" |

If compression preserved the right information, the agent answers correctly. If not, it guesses or hallucinates.

**Evaluation Dimensions for Compression**

Six dimensions capture compression quality for coding agents:

1. **Accuracy**: Are technical details correct? File paths, function names, error codes.
2. **Context Awareness**: Does the response reflect current conversation state?
3. **Artifact Trail**: Does the agent know which files were read or modified?
4. **Completeness**: Does the response address all parts of the question?
5. **Continuity**: Can work continue without re-fetching information?
6. **Instruction Following**: Does the response respect stated constraints?

Accuracy shows the largest variation between compression methods (0.6 point gap). Artifact trail is universally weak (2.2-2.5 range).

### Three-Phase Compression Workflow

For large codebases or agent systems exceeding context windows, apply compression through three phases:

1. **Research Phase**: Produce a research document from architecture diagrams, documentation, and key interfaces. Compress exploration into a structured analysis of components and dependencies. Output: single research document.

2. **Planning Phase**: Convert research into implementation specification with function signatures, type definitions, and data flow. A 5M token codebase compresses to approximately 2,000 words of specification.

3. **Implementation Phase**: Execute against the specification. Context remains focused on the spec rather than raw codebase exploration.

**Using Example Artifacts as Seeds**
When provided with a manual migration example or reference PR, use it as a template to understand the target pattern. The example reveals constraints that static analysis cannot surface: which invariants must hold, which services break on changes, and what a clean migration looks like.

## Practical Guidance

### Optimization Decision Framework

When to optimize:
- Context utilization exceeds 70%
- Response quality degrades as conversations extend
- Costs increase due to long contexts
- Latency increases with conversation length

What to apply:
- Tool outputs dominate: observation masking
- Retrieved documents dominate: summarization or partitioning
- Message history dominates: compaction with summarization
- Multiple components: combine strategies

### Performance Considerations

Compaction should achieve 50-70% token reduction with less than 5% quality degradation. Masking should achieve 60-80% reduction in masked observations. Cache optimization should achieve 70%+ hit rate for stable workloads.

Monitor and iterate on optimization strategies based on measured effectiveness.

## Examples

**Example 1: Compaction Trigger**
```python
if context_tokens / context_limit > 0.8:
    context = compact_context(context)
```

**Example 2: Observation Masking**
```python
if len(observation) > max_length:
    ref_id = store_observation(observation)
    return f"[Obs:{ref_id} elided. Key: {extract_key(observation)}]"
```

**Example 3: Cache-Friendly Ordering**
```python
# Stable content first
context = [system_prompt, tool_definitions]  # Cacheable
context += [reused_templates]  # Reusable
context += [unique_content]  # Unique
```

**Example 4: Debugging Session Compression**

Original context (89,000 tokens, 178 messages):
- 401 error on /api/auth/login endpoint
- Traced through auth controller, middleware, session store
- Found stale Redis connection
- Fixed connection pooling, added retry logic

Structured summary after compression:

```markdown
## Session Intent
Debug 401 Unauthorized error on /api/auth/login despite valid credentials.

## Root Cause
Stale Redis connection in session store. JWT generated correctly but session could not be persisted.

## Files Modified
- auth.controller.ts: No changes (read only)
- config/redis.ts: Fixed connection pooling configuration
- services/session.service.ts: Added retry logic for transient failures

## Test Status
14 passing, 2 failing (mock setup issues)

## Next Steps
1. Fix remaining test failures (mock session service)
2. Run full test suite
```

**Example 5: Probe Response Quality Comparison**

After compression, asking "What was the original error?":

Good response (structured summarization):
> "The original error was a 401 Unauthorized response from the /api/auth/login endpoint. Users received this error with valid credentials. Root cause was stale Redis connection in session store."

Poor response (aggressive compression):
> "We were debugging an authentication issue. The login was failing. We fixed some configuration problems."

The structured response preserves endpoint, error code, and root cause. The aggressive response loses all technical detail.

## Guidelines

1. Optimize for tokens-per-task, not tokens-per-request
2. Use structured summaries with explicit sections for file tracking
3. Trigger compression at 70-80% context utilization
4. Implement incremental merging rather than full regeneration
5. Test compression quality with probe-based evaluation
6. Track artifact trail separately if file tracking is critical
7. Accept slightly lower compression ratios for better quality retention
8. Monitor re-fetching frequency as a compression quality signal
9. Design for cache stability with consistent prompts
10. Partition before context becomes problematic

## Integration

This skill builds on context-fundamentals and context-degradation. It connects to:

- multi-agent-patterns - Partitioning as isolation
- evaluation - Measuring optimization effectiveness
- memory-systems - Offloading context to memory

## References

Internal reference:
- [Optimization Techniques Reference](./references/optimization_techniques.md) - Detailed technical reference
- [Evaluation Framework Reference](./references/evaluation-framework.md) - Probe types and scoring rubrics

Related skills in this collection:
- context-fundamentals - Context basics
- context-degradation - Understanding when to optimize
- evaluation - Measuring optimization

External resources:
- Factory Research: Evaluating Context Compression for AI Agents (December 2025)
- Netflix Engineering: "The Infinite Software Crisis" - Three-phase workflow and context compression at scale (AI Summit 2025)
- Research on LLM-as-judge evaluation methodology (Zheng et al., 2023)
- KV-cache optimization techniques
- Production engineering guides

---

## Skill Metadata

**Created**: 2025-12-20
**Last Updated**: 2025-12-27
**Author**: Agent Skills for Context Engineering Contributors
**Version**: 1.1.0
