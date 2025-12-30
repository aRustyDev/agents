# Dev Workflow & REPL Reference (9th Pillar)

Guidance for translating development workflows, especially REPL-centric patterns.

---

## Why This Matters

REPL-centric languages enable a fundamentally different development style:

- Incremental, exploratory development
- Immediate feedback on code changes
- Hot code reloading in production (BEAM)
- Interactive debugging and data inspection

When converting FROM these languages, developers lose familiar workflows.
When converting TO them, developers gain powerful new capabilities.

---

## REPL-Centric Languages

| Language    | REPL/Workflow       | Key Features                                          |
|-------------|---------------------|-------------------------------------------------------|
| Clojure     | `clj`, CIDER, Calva | Send forms to REPL, hot reload, REPL-driven design    |
| Elixir      | `iex`, IEx.pry      | Interactive shell, hot code loading, remote debugging |
| Erlang      | `erl`, observer     | Shell, hot code loading, runtime introspection        |
| Haskell     | `ghci`              | Type checking, expression evaluation, :reload         |
| Lisp/Scheme | Various             | SLIME/Sly, image-based development                    |
| F#          | FSI, Ionide         | Scripts, notebooks, interactive exploration           |

---

## Workflow Translation: REPL → Compiled

When converting FROM REPL-centric TO compiled languages:

| REPL Workflow              | Compiled Equivalent       | Tools                      |
|----------------------------|---------------------------|----------------------------|
| Send expression to REPL    | Run tests / scratch files | cargo watch, go run        |
| Hot reload function        | Recompile + restart       | Fast incremental builds    |
| Interactive debugging      | Debugger breakpoints      | lldb, delve, gdb           |
| Data inspection at runtime | Logging, tracing          | tracing crate, log package |
| REPL-driven design         | Test-driven design        | Property-based tests       |

### Development Speed Comparison

| Task | REPL Language | Compiled Language |
|------|---------------|-------------------|
| Try new function | < 1 second | 5-30 seconds |
| Modify and retest | < 1 second | 2-10 seconds |
| Inspect data | Immediate | Add logging, rebuild |
| Debug issue | Inspect in REPL | Debugger or logs |

### Maintaining Rapid Feedback

**For Rust:**
```bash
# Fast iteration with cargo watch
cargo watch -x test
cargo watch -x "run -- args"

# REPL-like exploration
evcxr  # Limited Rust REPL
```

**For Go:**
```bash
# Fast rebuilds
go run .

# Watch mode
air  # Hot reload for web apps
```

---

## Workflow Translation: Compiled → REPL

When converting FROM compiled TO REPL-centric languages:

| Compiled Workflow        | REPL Enhancement             | Benefit              |
|--------------------------|------------------------------|----------------------|
| Write test, compile, run | Evaluate expression directly | Instant feedback     |
| Step debugger            | Data inspection in REPL      | Richer exploration   |
| Print-based debugging    | Live value inspection        | No recompile needed  |
| Full rebuild on change   | Reload single function       | Sub-second iteration |

### New Capabilities to Leverage

**In Clojure:**
```clojure
;; Evaluate in REPL, see result immediately
(defn process-user [user]
  (-> user
      (update :name str/upper-case)
      (assoc :processed-at (java.time.Instant/now))))

;; Test immediately:
(process-user {:name "alice"})
;; => {:name "ALICE", :processed-at #inst "2024-..."}
```

**In Elixir:**
```elixir
# IEx.pry for inline debugging
def process(data) do
  require IEx
  IEx.pry()  # Execution pauses here, can inspect

  transform(data)
end
```

---

## Hot Code Loading (BEAM)

Erlang/Elixir support hot code loading in production.

### How It Works

1. Compile new module version
2. Load into running VM
3. Running processes upgrade on next function call
4. Old version kept for in-flight calls
5. Old version purged after grace period

### Production Hot Reload

```elixir
# Deploy without restart
# Processes automatically upgrade

defmodule Counter do
  use GenServer

  # Old version running in production
  def handle_call(:get, _from, count) do
    {:reply, count, count}
  end

  # Deploy new version - running processes upgrade
  def handle_call(:get, _from, count) do
    {:reply, {:count, count, :version, 2}, count}
  end
end
```

### Converting FROM BEAM

When moving away from Erlang/Elixir, document that:

- Hot reload won't be available (requires restart)
- Blue-green deployments or rolling updates replace hot loading
- Feature flags can simulate gradual rollout
- Deployment pipeline needs adjustment

### Converting TO BEAM

Take advantage of:

- Zero-downtime deployments
- Live debugging with `:observer`
- Remote shell into production
- Runtime code modification for debugging

---

## Development Tool Mapping

| Capability        | Clojure        | Elixir           | Haskell     | Rust            | Go             |
|-------------------|----------------|------------------|-------------|-----------------|----------------|
| REPL              | clj/CIDER      | iex              | ghci        | evcxr (limited) | gore (limited) |
| Watch mode        | shadow-cljs    | mix test --watch | ghcid       | cargo watch     | air            |
| Hot reload        | Built-in       | Built-in         | :reload     | No              | No             |
| Interactive debug | CIDER debugger | IEx.pry          | GHCi :break | lldb            | delve          |
| Notebooks         | Clerk          | Livebook         | IHaskell    | Rust Jupyter    | -              |

---

## Editor Integration

### REPL-Integrated Editors

| Editor | Clojure | Elixir | Haskell |
|--------|---------|--------|---------|
| VS Code | Calva | ElixirLS | Haskell extension |
| Emacs | CIDER | Alchemist | haskell-mode |
| IntelliJ | Cursive | - | IntelliJ Haskell |
| Vim/Neovim | Conjure | - | haskell-vim |

### Key REPL Keybindings to Learn

| Action | Purpose |
|--------|---------|
| Eval expression | Run code under cursor |
| Eval buffer | Reload entire file |
| Eval region | Run selected code |
| Show docs | View documentation |
| Jump to definition | Navigate codebase |
| Inspect value | Examine data structures |

---

## Testing Strategy Translation

| REPL Pattern | Compiled Equivalent |
|--------------|---------------------|
| REPL exploration | Unit tests |
| Quick experiments | Property-based tests |
| Interactive validation | Integration tests |
| Live inspection | Logging + tracing |

### From REPL-Driven to Test-Driven

```clojure
;; Clojure: REPL-driven development
(defn process-user [user]
  (-> user
      (update :name str/upper-case)
      (assoc :processed-at (java.time.Instant/now))))

;; Evaluate in REPL:
(process-user {:name "alice"})
;; => {:name "ALICE", :processed-at #inst "2024-..."}
```

```rust
// Rust: Test-driven equivalent
fn process_user(mut user: User) -> User {
    user.name = user.name.to_uppercase();
    user.processed_at = Some(Utc::now());
    user
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_process_user() {
        let user = User { name: "alice".into(), processed_at: None };
        let result = process_user(user);
        assert_eq!(result.name, "ALICE");
        assert!(result.processed_at.is_some());
    }
}
// Run with: cargo watch -x test
```

---

## Livebook / Notebooks

Some REPL languages have notebook environments:

| Language | Notebook | Use Case |
|----------|----------|----------|
| Elixir | Livebook | Data exploration, docs |
| Clojure | Clerk | Visual notebooks |
| Haskell | IHaskell | Jupyter integration |
| Python | Jupyter | Data science standard |

### When Converting FROM Notebooks

- Extract reusable code to modules
- Convert cells to functions
- Add proper tests
- Document data dependencies
