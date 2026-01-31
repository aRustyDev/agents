# Platform Ecosystem Reference

When converting code between languages that run on different platforms, understanding the underlying runtime characteristics is crucial for successful translation.

## Platform Families

| Platform | Languages | Key Characteristics |
|----------|-----------|---------------------|
| **JVM** | Java, Scala, Kotlin, Clojure, Groovy | Bytecode, JIT compilation, GC, thread-based concurrency, rich stdlib |
| **BEAM** | Erlang, Elixir, Gleam | Lightweight processes, preemptive scheduling, fault tolerance, hot code reload |
| **.NET/CLR** | C#, F#, VB.NET | Similar to JVM, strong Windows integration, async/await primitives |
| **Native** | C, C++, Rust, Zig, Roc | Direct compilation, manual/ownership memory, no runtime overhead |
| **Scripting** | Python, Ruby, JavaScript, Perl | Interpreted/JIT, dynamic typing, rapid development, GIL (Python) |
| **WebAssembly** | Any → WASM | Sandboxed, browser/edge deployment, limited I/O |

## Runtime Characteristics Matrix

| Characteristic | JVM | BEAM | .NET | Native | Scripting |
|----------------|-----|------|------|--------|-----------|
| **Startup time** | Slow (JIT) | Fast | Medium | Instant | Fast |
| **Memory overhead** | High | Medium | High | Low | High |
| **Concurrency model** | Threads + ForkJoin | Processes + actors | Threads + async | Threads/manual | Event loop/GIL |
| **GC style** | Generational | Per-process | Generational | None/ownership | Various |
| **Hot reload** | Limited (JRebel) | Native | Limited | None | Some |
| **FFI** | JNI (complex) | NIFs/ports | P/Invoke | Native | ctypes/ffi |

## Platform Migration Patterns

### JVM → BEAM (e.g., Scala → Elixir)

```
# Key Translations
Threads → Processes (lightweight)
Shared state → Message passing
Exception handling → Let-it-crash + supervision
Akka actors → GenServer
ExecutorService → Task.async_stream
synchronized → No equivalent (processes are isolated)
```

**Considerations:**
- BEAM processes are ~1000x lighter than JVM threads
- No shared mutable state - all state via message passing or ETS
- Supervision trees replace defensive error handling
- Pattern matching more idiomatic than conditionals

### JVM → Native (e.g., Scala → Rust)

```
# Key Translations
GC → Ownership system
null → Option<T>
Exception → Result<T, E>
Class inheritance → Trait composition
Generics → Generics + lifetimes
Maven/Gradle → Cargo
```

**Considerations:**
- Must reason about memory lifetimes
- No runtime reflection (use macros instead)
- Async is explicit (tokio runtime)
- Smaller binaries, faster startup

### .NET → JVM (e.g., F# → Scala)

```
# Key Translations
async/await → Future/ZIO
LINQ → Collections/Stream API
Pattern matching → Pattern matching (similar)
Units of measure → No equivalent (use wrapper types)
Type providers → Macros
NuGet → Maven/SBT
```

**Considerations:**
- Both have rich type systems
- Async models differ (Task vs Future)
- F# is more functional-first than Scala's hybrid
- Effect systems differ significantly

### Scripting → Native (e.g., Python → Rust)

```
# Key Translations
Dynamic types → Static types (add everywhere)
dict → HashMap/struct
list → Vec
None → Option<T>
try/except → Result<T, E> or panic
class → struct + impl
inheritance → trait composition
```

**Considerations:**
- Must add type annotations everywhere
- No runtime flexibility (reflection, dynamic dispatch)
- Memory management explicit
- Significant performance improvement

## Stdlib Mapping by Platform

### I/O Operations

| Operation | JVM | BEAM | .NET | Native (Rust) | Python |
|-----------|-----|------|------|---------------|--------|
| Read file | `Files.readString` | `File.read!` | `File.ReadAllText` | `fs::read_to_string` | `open().read()` |
| Write file | `Files.writeString` | `File.write!` | `File.WriteAllText` | `fs::write` | `open().write()` |
| HTTP GET | `HttpClient.send` | `HTTPoison.get!` | `HttpClient.GetAsync` | `reqwest::get` | `requests.get` |
| JSON parse | `Jackson/Gson` | `Jason.decode!` | `JsonSerializer` | `serde_json` | `json.loads` |

### Concurrency Primitives

| Primitive | JVM | BEAM | .NET | Native (Rust) | Python |
|-----------|-----|------|------|---------------|--------|
| Spawn async | `CompletableFuture.runAsync` | `spawn/1` | `Task.Run` | `tokio::spawn` | `asyncio.create_task` |
| Mutex | `synchronized` | N/A (process isolation) | `lock` | `Mutex` | `threading.Lock` |
| Channel | `BlockingQueue` | Process mailbox | `Channel<T>` | `mpsc::channel` | `queue.Queue` |
| Atomic | `AtomicReference` | Agent | `Interlocked` | `AtomicCell` | N/A |

## Transpiler/Compiler Options

Some languages support cross-platform compilation:

| Source | Target | Tool | Notes |
|--------|--------|------|-------|
| F# | JavaScript | Fable | Full F# to JS, React integration |
| Scala | JavaScript | Scala.js | Full Scala to JS |
| Kotlin | JavaScript | Kotlin/JS | Full Kotlin to JS |
| Elm | JavaScript | Elm compiler | Native, optimized output |
| Python | JavaScript | Transcrypt, Brython | Subset of Python |
| Go | JavaScript | GopherJS | Full Go to JS |
| Rust | WASM | wasm-pack | Native, near-native speed |
| Clojure | JavaScript | ClojureScript | Full Clojure to JS |

When a transpiler exists, consider using it instead of manual conversion for:
- Existing large codebases
- Incremental migration
- When runtime semantics must be preserved exactly

## Interop Considerations

### FFI Complexity by Platform

| From → To | Complexity | Approach |
|-----------|------------|----------|
| JVM ↔ Native | High | JNI, Panama (Java 21+), GraalVM native-image |
| BEAM ↔ Native | Medium | NIFs (Rustler for Rust), Ports |
| .NET ↔ Native | Medium | P/Invoke, C++/CLI |
| Python ↔ Native | Low | ctypes, cffi, PyO3 (Rust) |
| Scripting ↔ Scripting | Low | Usually simple bridges available |

### When to Use Interop vs Rewrite

**Use Interop When:**
- Performance-critical code already exists in native language
- Library has no equivalent in target language
- Incremental migration strategy
- Preserving existing battle-tested code

**Rewrite When:**
- Code is small and well-understood
- Significant idiom mismatch makes interop awkward
- Long-term maintenance by target-language team
- Performance requirements differ

## Platform-Specific Gotchas

### JVM

- Thread startup is expensive (~1MB stack per thread)
- GC pauses can affect latency-sensitive apps
- Startup time makes JVM poor for CLI tools
- Reflection works but has performance cost

### BEAM

- No shared mutable state (design around message passing)
- NIFs can crash the entire VM if not careful
- Binary pattern matching is powerful but has learning curve
- OTP conventions are essential for production

### .NET

- Strong async/await but Task overhead for high-frequency
- LINQ is powerful but can hide complexity
- Platform availability considerations (historically Windows-centric)
- F# computation expressions are powerful but obscure

### Native (Rust)

- Borrow checker learning curve significant
- Async requires runtime (tokio, async-std)
- Build times can be slow for large projects
- Smaller ecosystem than JVM/.NET

### Scripting (Python)

- GIL prevents true parallelism in threads
- Dynamic typing hides bugs until runtime
- Memory management less predictable
- Performance requires native extensions for CPU-bound work

---

## Cross-References

- [Stdlib Mapping](stdlib-mapping.md) - Detailed stdlib function equivalents
- [Concurrency Patterns](../SKILL.md#concurrency-pattern-translation) - Concurrency model translation
- [Difficulty Matrix](../../meta-convert-guide/reference/difficulty-matrix.md) - Language pair difficulty ratings
