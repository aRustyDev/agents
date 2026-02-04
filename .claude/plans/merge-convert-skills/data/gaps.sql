-- Phase 3: Semantic Gap Analysis Data
-- Generated: 2026-02-04
-- Populates existing tables from schema.sql
-- Run AFTER schema.sql and patterns.sql

BEGIN TRANSACTION;

-- ============================================================================
-- Family Lookup Helper
-- ============================================================================
-- Ensure families exist (should already be in schema.sql)

INSERT OR IGNORE INTO families (name, category, description) VALUES
  ('ml-fp', 'paradigm', 'ML-style functional programming: Scala, Haskell, F#, Elm, Roc, Gleam'),
  ('beam', 'runtime', 'BEAM VM languages: Elixir, Erlang'),
  ('lisp', 'paradigm', 'Lisp family: Clojure, Common Lisp, Scheme'),
  ('systems', 'memory', 'Systems programming: Rust, C, C++, Go, Zig'),
  ('dynamic', 'typing', 'Dynamically typed: Python, TypeScript, JavaScript, Ruby'),
  ('managed-oop', 'runtime', 'Managed OOP: Java, Kotlin'),
  ('apple', 'platform', 'Apple platform: Swift, Objective-C'),
  ('logic', 'paradigm', 'Logic programming: Prolog'),
  ('procedural', 'paradigm', 'Procedural languages: COBOL, Fortran, Pascal, Ada');

-- ============================================================================
-- Gap Patterns (54 entries from gap-patterns.md)
-- ============================================================================

INSERT OR REPLACE INTO gap_patterns
  (name, category, description, from_concept, to_concept, mitigation_strategy, example_from, example_to)
VALUES
  -- Type System Patterns (16)
  ('ts-001-dynamic-to-static', 'type_system',
   'Converting dynamically typed code to statically typed',
   'Dynamic typing (any)', 'Static typing (concrete types)',
   'Type inference with manual annotations for ambiguous cases',
   'def process(data): return data.upper()',
   'fn process(data: &str) -> String { data.to_uppercase() }'),

  ('ts-002-nullable-to-nonnull', 'type_system',
   'Converting from pervasive null/nil to explicit Option/Maybe',
   'Nullable values', 'Option/Maybe wrappers',
   'Track nullable values through data flow analysis; convert null checks to pattern matching',
   'return user != null ? user.name : null;',
   'self.user.as_ref().map(|u| u.name.as_str())'),

  ('ts-003-hkt-to-no-hkt', 'type_system',
   'Converting code using higher-kinded types to languages without HKT',
   'Higher-kinded types (Functor, Monad)', 'Concrete types',
   'Specialize generic code for each concrete type; use code generation',
   'fmap :: Functor f => (a -> b) -> f a -> f b',
   'func MapSlice[A, B any](f func(A) B, xs []A) []B'),

  ('ts-004-gradual-to-static', 'type_system',
   'Converting from gradual typing to full static typing',
   'Optional type annotations', 'Required type coverage',
   'Run type coverage tools; replace any/dynamic with concrete types',
   'function process(data: any): unknown',
   'public <T extends Transformable> Object process(T data)'),

  ('ts-005-duck-to-interfaces', 'type_system',
   'Converting from duck typing to explicit interfaces',
   'Structural duck typing', 'Explicit interface declarations',
   'Identify method signatures; extract interfaces from usage patterns',
   'def serialize(obj): return obj.to_json()',
   'interface JsonSerializable { String toJson(); }'),

  ('ts-006-union-to-tagged', 'type_system',
   'Converting untagged union types to tagged unions/variants',
   'Untagged union types', 'Tagged union/variant types',
   'Analyze type guards; create explicit variant types; convert to pattern matching',
   'type Result = string | number | Error;',
   'enum Result { Text(String), Number(i64), Err(Error) }'),

  ('ts-007-structural-to-nominal', 'type_system',
   'Converting from structural to nominal type systems',
   'Types match by shape', 'Types match by name',
   'Create named interfaces; add explicit implements declarations',
   'function greet(person: { name: string })',
   'void greet(Person person)'),

  ('ts-008-implicit-to-explicit-generics', 'type_system',
   'Converting from implicit to explicit generic instantiation',
   'Implicit generic type parameters', 'Explicit type parameters',
   'Use type inference to discover generic parameters; add explicit declarations',
   'identity x = x',
   'public static <T> T identity(T x)'),

  ('ts-009-type-erasure', 'type_system',
   'Converting from reified generics to type-erased generics',
   'Runtime type information', 'Type erasure',
   'Add class token parameters; use factory patterns for instantiation',
   'public T CreateInstance<T>() where T : new()',
   'public <T> T createInstance(Class<T> clazz)'),

  ('ts-010-typeclasses-to-interfaces', 'type_system',
   'Converting type class polymorphism to interface dispatch',
   'Type classes', 'Interface/vtable dispatch',
   'Convert type class to interface; add self-referential bounds',
   'class Eq a where (==) :: a -> a -> Bool',
   'interface Eq<T> { boolean eq(T other); }'),

  ('ts-011-dependent-to-runtime', 'type_system',
   'Converting dependent types to conventional typing',
   'Dependent types', 'Runtime validation',
   'Add runtime assertions; use property-based testing; document lost guarantees',
   'append : Vect n a -> Vect m a -> Vect (n + m) a',
   'append :: [a] -> [a] -> [a] -- length guarantee lost'),

  ('ts-012-row-poly-to-fixed', 'type_system',
   'Converting extensible records to fixed record types',
   'Row polymorphism', 'Fixed record types',
   'Create interfaces for common field sets; use composition',
   'getName :: forall r. { name :: String | r } -> String',
   'type Named interface { GetName() string }'),

  ('ts-013-refinement-to-runtime', 'type_system',
   'Converting refinement types to runtime validation',
   'Refinement types with predicates', 'Runtime checks',
   'Convert refinements to runtime checks; use newtype wrappers with smart constructors',
   '{-@ divide :: Int -> Pos -> Int @-}',
   'fn divide(x: i32, y: i32) -> Result<i32, &str>'),

  ('ts-014-phantom-to-docs', 'type_system',
   'Converting phantom types to non-phantom equivalents',
   'Phantom type parameters', 'Separate wrapper types',
   'Create separate wrapper types; document type constraints',
   'struct Id<T> { value: u64, _phantom: PhantomData<T> }',
   'class UserId { private long value; }'),

  ('ts-015-inference-direction', 'type_system',
   'Converting between local and global type inference',
   'Global type inference', 'Local type inference',
   'Run type inference on source; add explicit annotations',
   'f x = x + 1; g = map f',
   'func f(x int) int { return x + 1 }'),

  ('ts-016-variance-handling', 'type_system',
   'Converting between variance annotation systems',
   'Explicit variance (+/-)', 'Wildcards or invariant',
   'Map variance annotations to wildcards; use bounded type parameters',
   'class Box[+A](val value: A)',
   'static <T> T process(Box<? extends T> box)'),

  -- Memory Model Patterns (12)
  ('mm-001-gc-to-manual', 'memory',
   'Converting from GC to manual malloc/free',
   'Garbage collection', 'Manual memory management',
   'Track allocations and lifetimes; document ownership; use static analysis',
   'return a + b;',
   'char* result = malloc(len); // caller must free'),

  ('mm-002-gc-to-ownership', 'memory',
   'Converting from GC to Rust ownership/borrowing',
   'Garbage collection', 'Ownership with borrow checking',
   'Identify ownership patterns; determine borrow vs move; add lifetimes',
   'for item in items: process(item)',
   'fn process_items(items: &[Item]) -> &[Item]'),

  ('mm-003-shared-to-linear', 'memory',
   'Converting shared mutable state to linear types',
   'Shared mutable state', 'Linear/affine types',
   'Track mutation points; convert mutating methods to value transformers',
   'from.balance -= amount; to.balance += amount;',
   'fn transfer(mut from: Account, mut to: Account) -> (Account, Account)'),

  ('mm-004-mutable-to-immutable', 'memory',
   'Converting mutable-by-default to immutable-by-default',
   'Mutable by default', 'Immutable by default',
   'Identify mutation sites; convert to new value creation; use persistent structures',
   'items.add("a");',
   'items = ["a" | items]'),

  ('mm-005-stack-to-heap', 'memory',
   'Converting stack allocation to heap allocation',
   'Stack-allocated values', 'Heap-allocated (boxed) values',
   'Generally automatic in GC languages; consider escape analysis',
   'fn create_point() -> Point { Point { x: 1, y: 2 } }',
   'Point createPoint() { return new Point(1, 2); }'),

  ('mm-006-refcount-to-gc', 'memory',
   'Converting reference counting to tracing GC',
   'Reference counting (ARC)', 'Tracing garbage collection',
   'Remove weak/unowned markers; GC handles cycles automatically',
   'weak var parent: Node?',
   'Node parent; // GC handles cycles'),

  ('mm-007-gc-to-arc', 'memory',
   'Converting tracing GC to ARC with cycle management',
   'Tracing GC', 'Automatic Reference Counting',
   'Identify cyclic patterns; mark back-references as weak; test for leaks',
   'Node parent; // GC handles cycles',
   'weak var parent: Node?'),

  ('mm-008-deep-to-shallow', 'memory',
   'Converting between deep and shallow copy semantics',
   'Deep copy semantics', 'Shallow/reference copy',
   'Document copy semantics; use appropriate copy methods',
   'let copy = original.clone(); // deep',
   'const copy = [...original]; // shallow'),

  ('mm-009-value-to-reference', 'memory',
   'Converting value types to reference types',
   'Value types (copied)', 'Reference types (aliased)',
   'Document semantic difference; add defensive copies where needed',
   'var b = a; b.x = 10; // a.x still 1',
   'Point b = a; b.x = 10; // a.x also 10'),

  ('mm-010-isolated-to-shared', 'memory',
   'Converting per-process heaps to shared heap',
   'Isolated per-process heaps', 'Shared heap model',
   'Add synchronization for shared data; use concurrent structures',
   'send(parent, {:result, data}) // copied',
   'synchronized(results) { results.add(data); }'),

  ('mm-011-arena-allocation', 'memory',
   'Converting between arena and individual allocation',
   'Arena-based allocation', 'Individual allocation',
   'Group related allocations; use object pools; consider RAII',
   'defer arena.deinit(); // free all at once',
   'for (int i = 0; i < count; i++) free(ptrs[i]);'),

  ('mm-012-copy-on-write', 'memory',
   'Converting between COW and eager copy',
   'Copy-on-write optimization', 'Eager copy',
   'Add explicit clone calls; use Cow<T> for deferred cloning',
   'var b = a; b[0] = 99; // copy happens here',
   'let mut b = a.clone(); b[0] = 99;'),

  -- Effect System Patterns (12)
  ('ef-001-exceptions-to-result', 'effects',
   'Converting exception-based to Result/Either error handling',
   'Exceptions (throw/catch)', 'Result/Either types',
   'Identify throw sites; convert to Result; use ? operator for propagation',
   'throw new UserNotFoundException(id);',
   'db.find(id).ok_or(UserError::NotFound(id.to_string()))'),

  ('ef-002-null-to-option', 'effects',
   'Converting null returns to Option/Maybe types',
   'Null returns', 'Option/Maybe types',
   'Track nullable return points; convert null checks to Option operations',
   'return users.get(id); // null if not found',
   'fn get_user(&self, id: &str) -> Option<&User>'),

  ('ef-003-callbacks-to-async', 'effects',
   'Converting callback-based to async/await',
   'Callbacks', 'Async/await syntax',
   'Identify callback chains; convert to Promise; use async/await',
   'request(url, (err, response) => { ... })',
   'const response = await fetch(url);'),

  ('ef-004-monadic-to-direct', 'effects',
   'Converting monadic effect handling to direct style',
   'Monadic do-notation', 'Direct imperative style',
   'Flatten binds to statements; convert pattern matching to conditionals',
   'do { response <- httpGet url; return (parseUser response) }',
   'response = http_get(url); return parse_user(response)'),

  ('ef-005-implicit-to-explicit', 'effects',
   'Converting implicit side effects to explicit tracking',
   'Implicit side effects', 'Explicit effect types',
   'Identify all side effects; lift to effect type; separate pure and effectful',
   'def process(data): print(f"Processing"); return data.upper()',
   'process :: String -> IO String'),

  ('ef-006-global-to-pure', 'effects',
   'Converting global state to pure functions',
   'Global mutable state', 'Explicit state passing',
   'Identify global state access; thread state through parameters; use State monad',
   'global counter; def increment(): global counter; counter += 1',
   'def increment(counter), do: {counter + 1, counter + 1}'),

  ('ef-007-checked-to-unchecked', 'effects',
   'Converting checked to unchecked exceptions',
   'Checked exceptions', 'Unchecked exceptions',
   'Remove throws declarations; document error conditions',
   'public void readFile(String path) throws IOException',
   'fun readFile(path: String) // no throws needed'),

  ('ef-008-tuples-to-exceptions', 'effects',
   'Converting tagged tuples to exceptions',
   '{:ok, value}/{:error, reason} patterns', 'Exception handling',
   'Convert :error tuples to raises; convert pattern matching to try-except',
   'case File.read(path) do {:ok, content} -> ...',
   'try: content = open(path).read() except IOError:'),

  ('ef-009-lazy-to-strict', 'effects',
   'Converting lazy to strict evaluation',
   'Lazy evaluation (thunks)', 'Strict/eager evaluation',
   'Identify lazy patterns; convert to iterators/generators; bound infinite structures',
   'naturals = [0..]; take 5 naturals',
   'naturals = List.range { start: At 0, end: Before 5 }'),

  ('ef-010-strict-to-lazy', 'effects',
   'Converting strict to lazy evaluation',
   'Strict evaluation', 'Lazy evaluation with thunks',
   'Be aware of space leaks; use seq/deepseq when needed; use strict data types',
   'result = expensive(); // evaluated immediately',
   'result <- expensive; result `seq` putStrLn "Got it"'),

  ('ef-011-sync-to-async', 'effects',
   'Converting synchronous to asynchronous code',
   'Synchronous blocking', 'Asynchronous non-blocking',
   'Identify blocking operations; convert to async equivalents; handle backpressure',
   'for url in urls: results.append(requests.get(url))',
   'return Promise.all(urls.map(url => fetch(url)));'),

  ('ef-012-errorcodes-to-result', 'effects',
   'Converting integer error codes to Result types',
   'Integer error codes', 'Rich Result/Either types',
   'Map error codes to enum variants; create descriptive error types',
   'if (!f) return -1; return 0;',
   'fn read_file(path: &str) -> Result<String, io::Error>'),

  -- Concurrency Patterns (14)
  ('cc-001-actors-to-threads', 'concurrency',
   'Converting actor-based to thread-based concurrency',
   'Actor model (mailboxes, isolation)', 'Threads with shared memory',
   'Convert mailbox to queue; use locks/atomics; convert messages to method calls',
   'receive do :increment -> loop(count + 1) end',
   'private final AtomicInteger count = new AtomicInteger();'),

  ('cc-002-threads-to-actors', 'concurrency',
   'Converting threads to actor processes',
   'Shared-memory threads', 'Isolated actor processes',
   'Identify shared state; wrap in GenServer; convert synchronized to messages',
   'synchronized void transfer(Account to, int amount)',
   'GenServer.call(from_pid, {:withdraw, amount})'),

  ('cc-003-green-to-os', 'concurrency',
   'Converting green threads to OS threads',
   'Lightweight green threads', 'OS-level threads',
   'Use thread pools; consider virtual threads; batch work for efficiency',
   'for i := 0; i < 10000; i++ { go process(i) }',
   'ExecutorService pool = Executors.newFixedThreadPool(100);'),

  ('cc-004-csp-to-async', 'concurrency',
   'Converting CSP channels to async/await',
   'CSP-style channels', 'Async/await patterns',
   'Convert channels to Promises; use async queues; convert select to Promise.race',
   'ch := make(chan int); go func() { ch <- 42 }()',
   'const result = await new Promise(resolve => setTimeout(() => resolve(42), 0));'),

  ('cc-005-shared-to-messages', 'concurrency',
   'Converting shared memory to message passing',
   'Shared memory concurrency', 'Message passing',
   'Identify shared state; wrap in Agent/GenServer; convert mutations to messages',
   'synchronized void update(int v) { this.value = v; }',
   'Agent.update(__MODULE__, fn _ -> value end)'),

  ('cc-006-locks-to-stm', 'concurrency',
   'Converting locks/mutex to STM',
   'Lock-based synchronization', 'Software Transactional Memory',
   'Identify atomic boundaries; convert to STM transactions; remove explicit locks',
   'synchronized void transfer(...) { from.balance -= amount; }',
   'transfer from to amount = do { writeTVar from (fromBal - amount) }'),

  ('cc-007-async-to-callbacks', 'concurrency',
   'Converting async/await to callbacks',
   'Async/await syntax', 'Callback-based patterns',
   'Convert await points to callbacks; handle error propagation',
   'async function fetchData() { return await fetch(url); }',
   'function fetchData(callback) { fetch(url).then(data => callback(null, data)); }'),

  ('cc-008-futures-to-blocking', 'concurrency',
   'Converting Futures/Promises to blocking calls',
   'Future/Promise-based', 'Synchronous blocking',
   'Add blocking calls at async boundaries; handle timeouts',
   'val future: Future[User] = fetchUser(id)',
   'User user = fetchUserBlocking(id); // blocks'),

  ('cc-009-supervision-to-exceptions', 'concurrency',
   'Converting OTP supervision to exception handling',
   'OTP supervision trees', 'Exception-based recovery',
   'Convert restart strategies to restart loops; use circuit breakers',
   'Supervisor.start_link(children, strategy: :one_for_one)',
   'while (true) { try { worker.run(); } catch (e) { worker = new Worker(); } }'),

  ('cc-010-single-to-multi', 'concurrency',
   'Converting single-threaded to multi-threaded',
   'Single-threaded event loop', 'Multi-threaded execution',
   'Identify shared state; add synchronization; use thread-safe structures',
   'state.count++; // safe in single thread',
   'AtomicInteger count = new AtomicInteger(0);'),

  ('cc-011-parallel-to-sequential', 'concurrency',
   'Converting parallel collections to sequential',
   'Parallel collection operations', 'Sequential iteration',
   'Convert to sequential loop; document performance implications',
   'list.parallelStream().map(this::process).collect()',
   'for (int i = 0; i < count; i++) result[i] = process(items[i]);'),

  ('cc-012-reactive-to-pull', 'concurrency',
   'Converting reactive streams to pull-based',
   'Reactive push-based streams', 'Pull-based iteration',
   'Convert operators to loop operations; handle backpressure manually',
   'Flowable.fromIterable(items).map(this::transform).subscribe()',
   'for item in items: transformed = transform(item)'),

  ('cc-013-coroutines-to-statemachine', 'concurrency',
   'Converting coroutines to state machines',
   'Coroutine-based code', 'Explicit state machines',
   'Identify yield/await points; create state enum; store locals in context',
   'async def fetch(): data = await fetch(); return await process(data)',
   'enum State { FETCHING, PROCESSING, DONE }; int step(Context* ctx)'),

  ('cc-014-virtual-to-pool', 'concurrency',
   'Converting virtual threads to thread pools',
   'Virtual/lightweight threads', 'Traditional thread pools',
   'Use bounded thread pool; consider work-stealing; monitor utilization',
   'scope.fork(() -> fetchUser(id)); scope.join();',
   'ExecutorService pool = Executors.newFixedThreadPool(10);');

-- ============================================================================
-- Semantic Gaps (key gaps from gap-classification.md and family-pairs.md)
-- ============================================================================

-- ML-FP to Systems gaps (4: Very Hard)
INSERT OR REPLACE INTO semantic_gaps
  (from_family_id, to_family_id, gap_category, concept, description, severity, mitigation, automation_level)
SELECT
  (SELECT id FROM families WHERE name = 'ml-fp'),
  (SELECT id FROM families WHERE name = 'systems'),
  'lossy', 'Higher-kinded types',
  'HKT (Functor, Monad abstractions) cannot be directly represented in Systems languages',
  'high', 'Monomorphize to concrete types; defunctionalize abstractions', 'partial'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'ml-fp'),
  (SELECT id FROM families WHERE name = 'systems'),
  'lossy', 'Type classes',
  'Open type classes with retroactive conformance have no direct equivalent',
  'high', 'Trait impl at definition site (Rust), templates (C++)', 'partial'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'ml-fp'),
  (SELECT id FROM families WHERE name = 'systems'),
  'runtime', 'Lazy evaluation',
  'Systems languages are strict; lazy semantics require explicit thunks',
  'high', 'Explicit thunks, lazy crate (Rust), reorder evaluation', 'partial'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'ml-fp'),
  (SELECT id FROM families WHERE name = 'systems'),
  'runtime', 'GC to ownership',
  'GC memory model must be converted to ownership/borrowing (Rust) or manual (C)',
  'critical', 'Lifetime analysis; ownership design patterns', 'none'

-- Systems to ML-FP gaps (3: Hard)
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'systems'),
  (SELECT id FROM families WHERE name = 'ml-fp'),
  'lossy', 'Pointer arithmetic',
  'Direct pointer manipulation has no equivalent in safe ML-FP',
  'high', 'Abstract to indices, iterators, safe indexing', 'partial'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'systems'),
  (SELECT id FROM families WHERE name = 'ml-fp'),
  'structural', 'Mutation patterns',
  'Mutable state must become immutable with state threading',
  'medium', 'State monad, explicit state passing, STRef', 'partial'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'systems'),
  (SELECT id FROM families WHERE name = 'ml-fp'),
  'structural', 'Loop to recursion',
  'Imperative loops must become recursion or higher-order functions',
  'medium', 'Use fold/map/filter; tail-recursive loops', 'full'

-- Dynamic to ML-FP gaps (3: Hard)
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'dynamic'),
  (SELECT id FROM families WHERE name = 'ml-fp'),
  'lossy', 'Monkey patching',
  'Runtime type modification not possible with closed types',
  'high', 'Use type classes, extension methods, redesign with ADTs', 'none'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'dynamic'),
  (SELECT id FROM families WHERE name = 'ml-fp'),
  'semantic', 'Duck typing',
  'Implicit structural typing must become explicit interfaces',
  'medium', 'Define protocols/traits, extract interfaces from usage', 'partial'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'dynamic'),
  (SELECT id FROM families WHERE name = 'ml-fp'),
  'semantic', 'None/null semantics',
  'None/null must be explicitly wrapped in Option/Maybe',
  'medium', 'Analyze nullability, convert null checks to Option operations', 'partial'

-- Dynamic to Systems gaps (4: Very Hard)
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'dynamic'),
  (SELECT id FROM families WHERE name = 'systems'),
  'lossy', 'Runtime metaprogramming',
  'No runtime reflection in most Systems languages (C/Rust)',
  'high', 'Code generation, macros, static analysis', 'partial'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'dynamic'),
  (SELECT id FROM families WHERE name = 'systems'),
  'runtime', 'GC to ownership',
  'GC must be converted to ownership (Rust) or manual memory (C)',
  'critical', 'Lifetime analysis, ownership patterns', 'none'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'dynamic'),
  (SELECT id FROM families WHERE name = 'systems'),
  'semantic', 'Integer overflow',
  'Python arbitrary precision becomes fixed-width with overflow risk',
  'high', 'Use num_bigint (Rust), GMP (C), checked arithmetic', 'partial'

-- BEAM to ML-FP gaps (3: Hard)
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'beam'),
  (SELECT id FROM families WHERE name = 'ml-fp'),
  'lossy', 'Hot code reload',
  'BEAM hot code reload has no equivalent in ML-FP languages',
  'high', 'Design for restart; accept cold deploy model', 'none'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'beam'),
  (SELECT id FROM families WHERE name = 'ml-fp'),
  'lossy', 'Process isolation',
  'Per-process heaps and isolation have no direct equivalent',
  'high', 'Actor libraries, STM, explicit isolation boundaries', 'partial'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'beam'),
  (SELECT id FROM families WHERE name = 'ml-fp'),
  'runtime', 'Process-based thinking',
  'Actor model with mailboxes must become pure functions with explicit state',
  'high', 'State monad, STM, extract state types', 'partial'

-- BEAM to Systems gaps (4: Very Hard)
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'beam'),
  (SELECT id FROM families WHERE name = 'systems'),
  'lossy', 'Actor model',
  'Lightweight processes with mailboxes must become threads',
  'critical', 'Thread pools, async runtime, message queues', 'none'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'beam'),
  (SELECT id FROM families WHERE name = 'systems'),
  'lossy', 'Supervision trees',
  'OTP supervision for fault tolerance has no direct equivalent',
  'high', 'Circuit breakers, restart loops, exception handling', 'partial'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'beam'),
  (SELECT id FROM families WHERE name = 'systems'),
  'runtime', 'Per-process GC',
  'Per-process garbage collection becomes shared heap with synchronization',
  'high', 'Add locks, use concurrent data structures', 'partial'

-- LISP to ML-FP gaps (3: Hard)
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'lisp'),
  (SELECT id FROM families WHERE name = 'ml-fp'),
  'lossy', 'Macros',
  'Lisp macros must be expanded before translation; no equivalent',
  'high', 'Inline macro expansions, use Template Haskell if needed', 'partial'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'lisp'),
  (SELECT id FROM families WHERE name = 'ml-fp'),
  'lossy', 'Code-as-data',
  'Homoiconicity not representable in non-homoiconic languages',
  'high', 'AST libraries, quoted expressions where available', 'none'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'lisp'),
  (SELECT id FROM families WHERE name = 'ml-fp'),
  'semantic', 'Dynamic type assumptions',
  'Runtime type checking must become compile-time type checking',
  'medium', 'Type inference, use ADTs for heterogeneous data', 'partial'

-- Managed-OOP to Systems gaps (3: Hard)
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'managed-oop'),
  (SELECT id FROM families WHERE name = 'systems'),
  'runtime', 'GC to ownership',
  'JVM GC must be converted to ownership (Rust) or manual (C)',
  'critical', 'Lifetime analysis, ownership patterns, RAII', 'none'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'managed-oop'),
  (SELECT id FROM families WHERE name = 'systems'),
  'lossy', 'Type erasure',
  'Java generic type erasure loses runtime type info',
  'medium', 'Monomorphize, use type tokens for reflection', 'partial'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'managed-oop'),
  (SELECT id FROM families WHERE name = 'systems'),
  'structural', 'Inheritance flattening',
  'Deep inheritance hierarchies must be flattened',
  'medium', 'Composition over inheritance, trait objects', 'partial'

-- Apple to Systems gaps (3: Hard)
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'apple'),
  (SELECT id FROM families WHERE name = 'systems'),
  'runtime', 'ARC to ownership',
  'ARC automatic memory must become ownership (Rust) or manual (C)',
  'high', 'Map Rc/Arc to Swift patterns, design ownership model', 'partial'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'apple'),
  (SELECT id FROM families WHERE name = 'systems'),
  'semantic', 'Force unwrapping',
  'Swift force unwrap (!) can crash; must handle safely',
  'medium', 'Use optional chaining, guard let, if let', 'full'

-- Logic to others (5: Extreme)
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'logic'),
  (SELECT id FROM families WHERE name = 'ml-fp'),
  'lossy', 'Unification',
  'Logic unification has no direct equivalent; must use pattern matching + equality',
  'critical', 'LogicT monad, miniKanren libraries, explicit search', 'none'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'logic'),
  (SELECT id FROM families WHERE name = 'ml-fp'),
  'lossy', 'Backtracking',
  'Automatic backtracking search must become explicit',
  'critical', 'List monad, generators, explicit search algorithms', 'none'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'logic'),
  (SELECT id FROM families WHERE name = 'systems'),
  'lossy', 'Logic variables',
  'Unbound logic variables have no Systems equivalent',
  'critical', 'State threading, explicit variable binding', 'none'

-- Procedural to ML-FP gaps (4: Very Hard)
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'procedural'),
  (SELECT id FROM families WHERE name = 'ml-fp'),
  'structural', 'Imperative to functional',
  'Imperative control flow must become functional composition',
  'high', 'Convert loops to folds, mutation to immutable, GOTO to structured', 'partial'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'procedural'),
  (SELECT id FROM families WHERE name = 'ml-fp'),
  'lossy', 'Fixed-point decimal',
  'COBOL fixed-point decimal precision may be lost',
  'high', 'Use Decimal types, document precision requirements', 'partial'

-- Semantic gaps from gap-classification.md (negative patterns)
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'systems'),
  (SELECT id FROM families WHERE name = 'systems'),
  'runtime', 'Use-After-Free',
  'C to Rust: accessing memory after free leads to undefined behavior',
  'critical', 'Use ownership system correctly, avoid unsafe', 'partial'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'systems'),
  (SELECT id FROM families WHERE name = 'systems'),
  'idiomatic', 'Overusing Rc/Arc',
  'C++ to Rust: avoid shared_ptr mindset, prefer borrowing',
  'medium', 'Start with borrowing, add Rc/Arc only when needed', 'partial'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'dynamic'),
  (SELECT id FROM families WHERE name = 'systems'),
  'idiomatic', 'Over-cloning',
  'TypeScript to Rust: cloning everything to satisfy borrow checker',
  'medium', 'Learn to work with references, clone only small data', 'partial'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'ml-fp'),
  (SELECT id FROM families WHERE name = 'ml-fp'),
  'semantic', 'Lazy vs Strict infinite lists',
  'Haskell to Roc: infinite lazy lists not possible in strict language',
  'high', 'Use finite ranges, Stream types, explicit bounds', 'partial'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'ml-fp'),
  (SELECT id FROM families WHERE name = 'ml-fp'),
  'semantic', 'Either direction confusion',
  'F# to Haskell: Ok/Error mapping to Right/Left (Right is success)',
  'low', 'Remember "Right is right" mnemonic', 'full'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'lisp'),
  (SELECT id FROM families WHERE name = 'beam'),
  'runtime', 'Atom table exhaustion',
  'Clojure to Erlang: dynamic keyword creation can exhaust atom table',
  'high', 'Avoid dynamic atom creation, use binaries for dynamic data', 'partial'
UNION ALL SELECT
  (SELECT id FROM families WHERE name = 'beam'),
  (SELECT id FROM families WHERE name = 'dynamic'),
  'semantic', 'String vs Binary confusion',
  'Elixir to Erlang: strings and binaries have different semantics',
  'medium', 'Use binaries consistently, document encoding', 'partial'
;

-- ============================================================================
-- Family Conversion Difficulty (81 entries from 9x9 severity-matrix.md)
-- ============================================================================

-- Create difficulty matrix using CASE expressions for each family pair
INSERT OR REPLACE INTO family_conversion_difficulty
  (from_family_id, to_family_id, difficulty, notes)
SELECT f1.id, f2.id,
  CASE
    -- ML-FP row
    WHEN f1.name = 'ml-fp' AND f2.name = 'ml-fp' THEN 2
    WHEN f1.name = 'ml-fp' AND f2.name = 'beam' THEN 3
    WHEN f1.name = 'ml-fp' AND f2.name = 'lisp' THEN 2
    WHEN f1.name = 'ml-fp' AND f2.name = 'systems' THEN 4
    WHEN f1.name = 'ml-fp' AND f2.name = 'dynamic' THEN 2
    WHEN f1.name = 'ml-fp' AND f2.name = 'managed-oop' THEN 3
    WHEN f1.name = 'ml-fp' AND f2.name = 'apple' THEN 3
    WHEN f1.name = 'ml-fp' AND f2.name = 'logic' THEN 4
    WHEN f1.name = 'ml-fp' AND f2.name = 'procedural' THEN 4
    -- BEAM row
    WHEN f1.name = 'beam' AND f2.name = 'ml-fp' THEN 3
    WHEN f1.name = 'beam' AND f2.name = 'beam' THEN 2
    WHEN f1.name = 'beam' AND f2.name = 'lisp' THEN 2
    WHEN f1.name = 'beam' AND f2.name = 'systems' THEN 4
    WHEN f1.name = 'beam' AND f2.name = 'dynamic' THEN 2
    WHEN f1.name = 'beam' AND f2.name = 'managed-oop' THEN 3
    WHEN f1.name = 'beam' AND f2.name = 'apple' THEN 3
    WHEN f1.name = 'beam' AND f2.name = 'logic' THEN 5
    WHEN f1.name = 'beam' AND f2.name = 'procedural' THEN 4
    -- LISP row
    WHEN f1.name = 'lisp' AND f2.name = 'ml-fp' THEN 3
    WHEN f1.name = 'lisp' AND f2.name = 'beam' THEN 2
    WHEN f1.name = 'lisp' AND f2.name = 'lisp' THEN 2
    WHEN f1.name = 'lisp' AND f2.name = 'systems' THEN 4
    WHEN f1.name = 'lisp' AND f2.name = 'dynamic' THEN 2
    WHEN f1.name = 'lisp' AND f2.name = 'managed-oop' THEN 3
    WHEN f1.name = 'lisp' AND f2.name = 'apple' THEN 3
    WHEN f1.name = 'lisp' AND f2.name = 'logic' THEN 4
    WHEN f1.name = 'lisp' AND f2.name = 'procedural' THEN 4
    -- Systems row
    WHEN f1.name = 'systems' AND f2.name = 'ml-fp' THEN 3
    WHEN f1.name = 'systems' AND f2.name = 'beam' THEN 4
    WHEN f1.name = 'systems' AND f2.name = 'lisp' THEN 3
    WHEN f1.name = 'systems' AND f2.name = 'systems' THEN 2
    WHEN f1.name = 'systems' AND f2.name = 'dynamic' THEN 2
    WHEN f1.name = 'systems' AND f2.name = 'managed-oop' THEN 2
    WHEN f1.name = 'systems' AND f2.name = 'apple' THEN 3
    WHEN f1.name = 'systems' AND f2.name = 'logic' THEN 5
    WHEN f1.name = 'systems' AND f2.name = 'procedural' THEN 2
    -- Dynamic row
    WHEN f1.name = 'dynamic' AND f2.name = 'ml-fp' THEN 3
    WHEN f1.name = 'dynamic' AND f2.name = 'beam' THEN 3
    WHEN f1.name = 'dynamic' AND f2.name = 'lisp' THEN 2
    WHEN f1.name = 'dynamic' AND f2.name = 'systems' THEN 4
    WHEN f1.name = 'dynamic' AND f2.name = 'dynamic' THEN 2
    WHEN f1.name = 'dynamic' AND f2.name = 'managed-oop' THEN 2
    WHEN f1.name = 'dynamic' AND f2.name = 'apple' THEN 3
    WHEN f1.name = 'dynamic' AND f2.name = 'logic' THEN 4
    WHEN f1.name = 'dynamic' AND f2.name = 'procedural' THEN 2
    -- Managed-OOP row
    WHEN f1.name = 'managed-oop' AND f2.name = 'ml-fp' THEN 3
    WHEN f1.name = 'managed-oop' AND f2.name = 'beam' THEN 3
    WHEN f1.name = 'managed-oop' AND f2.name = 'lisp' THEN 3
    WHEN f1.name = 'managed-oop' AND f2.name = 'systems' THEN 3
    WHEN f1.name = 'managed-oop' AND f2.name = 'dynamic' THEN 2
    WHEN f1.name = 'managed-oop' AND f2.name = 'managed-oop' THEN 2
    WHEN f1.name = 'managed-oop' AND f2.name = 'apple' THEN 2
    WHEN f1.name = 'managed-oop' AND f2.name = 'logic' THEN 5
    WHEN f1.name = 'managed-oop' AND f2.name = 'procedural' THEN 2
    -- Apple row
    WHEN f1.name = 'apple' AND f2.name = 'ml-fp' THEN 3
    WHEN f1.name = 'apple' AND f2.name = 'beam' THEN 4
    WHEN f1.name = 'apple' AND f2.name = 'lisp' THEN 3
    WHEN f1.name = 'apple' AND f2.name = 'systems' THEN 3
    WHEN f1.name = 'apple' AND f2.name = 'dynamic' THEN 2
    WHEN f1.name = 'apple' AND f2.name = 'managed-oop' THEN 2
    WHEN f1.name = 'apple' AND f2.name = 'apple' THEN 2
    WHEN f1.name = 'apple' AND f2.name = 'logic' THEN 5
    WHEN f1.name = 'apple' AND f2.name = 'procedural' THEN 3
    -- Logic row
    WHEN f1.name = 'logic' AND f2.name = 'ml-fp' THEN 4
    WHEN f1.name = 'logic' AND f2.name = 'beam' THEN 4
    WHEN f1.name = 'logic' AND f2.name = 'lisp' THEN 3
    WHEN f1.name = 'logic' AND f2.name = 'systems' THEN 5
    WHEN f1.name = 'logic' AND f2.name = 'dynamic' THEN 4
    WHEN f1.name = 'logic' AND f2.name = 'managed-oop' THEN 5
    WHEN f1.name = 'logic' AND f2.name = 'apple' THEN 5
    WHEN f1.name = 'logic' AND f2.name = 'logic' THEN 2
    WHEN f1.name = 'logic' AND f2.name = 'procedural' THEN 4
    -- Procedural row
    WHEN f1.name = 'procedural' AND f2.name = 'ml-fp' THEN 4
    WHEN f1.name = 'procedural' AND f2.name = 'beam' THEN 4
    WHEN f1.name = 'procedural' AND f2.name = 'lisp' THEN 3
    WHEN f1.name = 'procedural' AND f2.name = 'systems' THEN 2
    WHEN f1.name = 'procedural' AND f2.name = 'dynamic' THEN 3
    WHEN f1.name = 'procedural' AND f2.name = 'managed-oop' THEN 3
    WHEN f1.name = 'procedural' AND f2.name = 'apple' THEN 3
    WHEN f1.name = 'procedural' AND f2.name = 'logic' THEN 5
    WHEN f1.name = 'procedural' AND f2.name = 'procedural' THEN 2
    ELSE 3  -- Default fallback
  END,
  CASE
    WHEN f1.name = f2.name THEN 'Same family: syntax and idiom differences'
    WHEN f1.name IN ('logic') OR f2.name IN ('logic') THEN 'Paradigm mismatch with logic programming'
    WHEN f1.name = 'dynamic' AND f2.name = 'systems' THEN 'Memory + type system challenges'
    WHEN f1.name = 'ml-fp' AND f2.name = 'systems' THEN 'HKT + memory model challenges'
    WHEN f1.name = 'beam' AND f2.name = 'systems' THEN 'Actor model + memory challenges'
    ELSE 'From Phase 3 severity matrix analysis'
  END
FROM families f1
CROSS JOIN families f2
WHERE f1.name IN ('ml-fp', 'beam', 'lisp', 'systems', 'dynamic', 'managed-oop', 'apple', 'logic', 'procedural')
  AND f2.name IN ('ml-fp', 'beam', 'lisp', 'systems', 'dynamic', 'managed-oop', 'apple', 'logic', 'procedural');

-- ============================================================================
-- Decision Points (16 entries from decision-points.md)
-- ============================================================================

INSERT OR REPLACE INTO decision_points
  (name, description, options, guidance)
VALUES
  ('error-handling-strategy',
   'Choose how to handle errors when converting between exception and result-based languages',
   '["result_either", "exceptions_panic", "error_returns_go", "mixed"]',
   'Match target language idioms: Result<T,E> for Rust, Either for Haskell, (value, error) for Go. If source uses exceptions for control flow, restructure logic first.'),

  ('error-checking-policy',
   'Choose policy for checking error returns in Go conversions',
   '["always_check", "must_wrapper", "errgroup"]',
   'Always check err != nil in production code. Use must_ prefix only in tests. Use errgroup for concurrent error aggregation.'),

  ('null-unwrapping-strategy',
   'Choose how to handle optional/nullable value unwrapping',
   '["optional_chaining", "guard_let", "if_let", "nil_coalescing", "force_unwrap"]',
   'Use optional chaining for chains, guard let for early exit, if let for conditional. Never use force unwrap (!) unless 100% certain. Match target idiom.'),

  ('null-representation',
   'Choose representation for null/None values in TypeScript conversions',
   '["undefined", "null", "semantic_distinction"]',
   'Use undefined for optional parameters, null for JSON compatibility and explicit absence. Pick one convention and be consistent within codebase.'),

  ('concurrency-state-model',
   'Choose state model when converting process-based to pure functional',
   '["explicit_state_passing", "platform_state", "immutable_snapshots", "actor_library"]',
   'For Elixir to Roc: extract state type, pass explicitly. For GenServer, convert to function parameters. Use platform capabilities for IO-heavy code.'),

  ('lazy-strict-evaluation',
   'Choose strategy for converting lazy to strict evaluation',
   '["finite_bounds", "lazy_list_stream", "iterator_pattern"]',
   'If source uses infinite lists, add explicit bounds. Use LazyList/Stream where available. Convert take n on infinite to finite range.'),

  ('otp-distribution-strategy',
   'Choose architecture when converting OTP distributed systems',
   '["akka_net", "orleans", "async_await", "message_queues"]',
   'Cannot automate; requires architecture review. Consider Orleans for virtual actors, Akka.NET for actor model, message broker for microservices.'),

  ('memory-ownership-strategy',
   'Choose ownership strategy for Rust conversions',
   '["borrowing", "owned", "box", "rc_arc", "clone"]',
   'Start with borrowing (&T), add ownership only when needed. Use Box for recursion. Use Arc only for cross-thread sharing. Clone acceptable for small types (<64 bytes).'),

  ('lifetime-annotation-strategy',
   'Choose lifetime strategy when converting GC languages to Rust',
   '["return_owned", "return_box", "explicit_lifetimes", "static_lifetime"]',
   'If returning data created in function, return owned. If returning subset of input, use lifetime annotation. Use Box for large returns.'),

  ('dynamic-to-static-types',
   'Choose type representation when converting dynamic to static typing',
   '["sum_types_adt", "generics", "any_object", "union_types"]',
   'If source has fixed set of types, use sum type/sealed trait. If always homogeneous, use generic. Avoid Any except for FFI/interop.'),

  ('advanced-type-features',
   'Choose strategy for advanced type features (GADTs, Type Families, DataKinds)',
   '["simplify_basic", "runtime_checks", "phantom_types", "manual_encoding"]',
   'Cannot automate; flag for manual review. If using GADTs for invariants, add runtime checks. If using type families, use explicit type parameters.'),

  ('either-direction-convention',
   'Choose convention for Result/Either mapping between languages',
   '["right_is_success", "explicit_error_type", "mtl_transformers"]',
   'Remember "Right is right" - Right = success, Left = error in Haskell. Map F# Ok to Right, Error to Left. Consider custom error types for clarity.'),

  ('integer-precision-strategy',
   'Choose integer type strategy when source has arbitrary precision',
   '["fixed_i64", "unsigned_u64", "bigint", "checked_arithmetic"]',
   'If source uses integers < 2^63, use i64. If doing big number math, use BigInt. If overflow is catastrophic, use checked_* arithmetic.'),

  ('mutable-to-immutable-collections',
   'Choose strategy for converting mutable collections to immutable',
   '["rebinding", "atoms_refs", "fold_reduce", "transducers"]',
   'If mutation is local, rebind with let. If mutation is shared, use language ref type (atom, ref). If building collection, use fold/reduce.'),

  ('naming-convention-transform',
   'Choose naming convention transformation strategy',
   '["follow_target", "preserve_source", "configurable_mapping"]',
   'Follow target convention: PascalCase for types, camelCase for methods (Scala/Java), snake_case (Rust/Python). SCREAMING_SNAKE for constants.'),

  ('object-slicing-prevention',
   'Choose strategy to prevent object slicing in C++ conversions',
   '["pass_by_reference", "pass_by_pointer", "smart_pointers", "abstract_base"]',
   'If function uses virtual methods, pass by reference/pointer. Use unique_ptr for ownership transfer, shared_ptr for shared. Consider making base abstract.');

COMMIT;

-- ============================================================================
-- Verification Queries
-- ============================================================================

SELECT 'gap_patterns' as tbl, COUNT(*) as cnt FROM gap_patterns
UNION ALL SELECT 'semantic_gaps', COUNT(*) FROM semantic_gaps
UNION ALL SELECT 'decision_points', COUNT(*) FROM decision_points
UNION ALL SELECT 'family_conversion_difficulty', COUNT(*) FROM family_conversion_difficulty
UNION ALL SELECT 'families', COUNT(*) FROM families;

-- Summary of difficulty distribution
SELECT
  'Difficulty Distribution' as metric,
  SUM(CASE WHEN difficulty = 2 THEN 1 ELSE 0 END) as easy,
  SUM(CASE WHEN difficulty = 3 THEN 1 ELSE 0 END) as hard,
  SUM(CASE WHEN difficulty = 4 THEN 1 ELSE 0 END) as very_hard,
  SUM(CASE WHEN difficulty = 5 THEN 1 ELSE 0 END) as extreme
FROM family_conversion_difficulty;

-- Gap categories
SELECT
  gap_category,
  COUNT(*) as count,
  GROUP_CONCAT(DISTINCT severity) as severities
FROM semantic_gaps
GROUP BY gap_category
ORDER BY count DESC;
