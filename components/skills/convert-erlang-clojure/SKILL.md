---
name: convert-erlang-clojure
description: Convert Erlang code to idiomatic Clojure. Use when migrating Erlang/OTP applications to Clojure/JVM, translating BEAM processes to JVM concurrency, or refactoring distributed systems from OTP to Clojure patterns. Extends meta-convert-dev with Erlang-to-Clojure specific patterns.
---

# Convert Erlang to Clojure

Convert Erlang code to idiomatic Clojure. This skill extends `meta-convert-dev` with Erlang-to-Clojure specific type mappings, idiom translations, and tooling for translating from BEAM/OTP patterns to JVM/Clojure patterns.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Erlang types → Clojure types (atoms, binaries, tuples)
- **Idiom translations**: OTP behaviors → Clojure state management patterns
- **Error handling**: Let it crash philosophy → Explicit error handling with maps
- **Concurrency patterns**: Lightweight processes → core.async or atoms/agents
- **Platform translation**: BEAM/OTP → JVM runtime and libraries

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Erlang language fundamentals - see `lang-erlang-dev`
- Clojure language fundamentals - see `lang-clojure-dev`
- Reverse conversion (Clojure → Erlang) - see `convert-clojure-erlang`
- Production deployment strategies - see deployment-specific skills

---

## Quick Reference

| Erlang | Clojure | Notes |
|--------|---------|-------|
| `atom` | `:keyword` | Erlang atoms → Clojure keywords |
| `{ok, Value}` | `{:ok value}` | Tuple → map with keyword keys |
| `[H\|T]` | `[h & t]` | List destructuring syntax differs |
| `#{key => value}` | `{:key value}` | Maps with different syntax |
| `spawn(Fun)` | `(future ...)` or `(go ...)` | Process → future/go block |
| `Pid ! Message` | `(>! ch message)` | Message send → channel put |
| `receive ... end` | `(<! ch)` | Message receive → channel take |
| `gen_server` | `(atom state)` + functions | Behavior → stateful atom |
| `supervisor` | Manual restart logic | No direct equivalent |
| `binary()` | `byte-array` | Binaries → byte arrays |

---

## When Converting Code

1. **Analyze source thoroughly** before writing target - understand OTP supervision trees
2. **Map types first** - create type equivalence table for domain models
3. **Preserve semantics** over syntax similarity - embrace JVM platform differences
4. **Adopt target idioms** - don't write "Erlang code in Clojure syntax"
5. **Handle edge cases** - nil safety, error paths, state management
6. **Test equivalence** - same inputs → same outputs
7. **Plan concurrency model** - processes → futures/core.async/agents

---

## Type System Mapping

### Primitive Types

| Erlang | Clojure | Notes |
|--------|---------|-------|
| `integer()` | `Long` (default) or `Integer` | JVM integers, arbitrary precision with BigInt |
| `float()` | `Double` | JVM floating point |
| `atom` | `:keyword` | Erlang atoms → Clojure keywords |
| `boolean()` | `Boolean` (true/false) | Direct mapping |
| `binary()` | `byte-array` or `String` | Depends on usage (bytes vs text) |
| `list()` | `[]` (vector) or `'()` (list) | Vectors more idiomatic |
| `tuple()` | `[]` (vector) or `{}` (map) | Depends on structure |
| `pid()` | `Future` or `Agent` or channel | Process reference → JVM concurrency primitive |
| `reference()` | `atom` with UUID or object reference | No direct equivalent |
| `fun()` | `(fn ...)` | Functions are first-class in both |

### Collection Types

| Erlang | Clojure | Notes |
|--------|---------|-------|
| `[H\|T]` (list) | `[h & t]` (vector) or `(h & t)` (list) | Vector destructuring preferred |
| `[]` (empty list) | `[]` or `'()` | Empty vector or list |
| `{A, B}` (tuple) | `[a b]` (vector) | 2-element tuple → vector |
| `{A, B, C}` | `[a b c]` | Multi-element tuple → vector |
| `#{K => V}` (map) | `{:k v}` (hash-map) | Map syntax differs |
| `#{}` (empty map) | `{}` | Empty map |
| `sets:new()` | `#{}` (hash-set) | Set syntax |
| `array` | `[]` (vector) | Erlang arrays → Clojure vectors |
| `queue` | `clojure.lang.PersistentQueue` | Queue data structure |

### Composite Types

| Erlang | Clojure | Notes |
|--------|---------|-------|
| `-record(user, {name, age})` | `{:name "" :age 0}` (map) or `defrecord` | Records → maps (idiomatic) or defrecord (performance) |
| `{ok, Value}` | `{:ok value}` | Tagged tuple → map |
| `{error, Reason}` | `{:error reason}` | Error tuple → map |
| `-type user() :: #user{}` | `(s/def ::user ...)` with spec | Type specs → clojure.spec |
| `-opaque type()` | No direct equivalent | Use protocols for encapsulation |

---

## Idiom Translation

### Pattern: Atoms to Keywords

Erlang atoms are interned strings used for constants. Clojure keywords serve the same purpose.

**Erlang:**
```erlang
-define(STATUS_OK, ok).
-define(STATUS_ERROR, error).

process_result(ok) -> "Success";
process_result(error) -> "Failure";
process_result(Unknown) -> io:format("Unknown: ~p~n", [Unknown]).

% Pattern matching with atoms
case Status of
    ok -> handle_success();
    error -> handle_error();
    _ -> handle_unknown()
end.
```

**Clojure:**
```clojure
(def status-ok :ok)
(def status-error :error)

(defn process-result [status]
  (case status
    :ok "Success"
    :error "Failure"
    (str "Unknown: " status)))

;; Pattern matching with case
(case status
  :ok (handle-success)
  :error (handle-error)
  (handle-unknown))

;; Or with cond
(cond
  (= status :ok) (handle-success)
  (= status :error) (handle-error)
  :else (handle-unknown))
```

**Why this translation:**
- Keywords are idiomatic for enum-like values in Clojure
- Both are interned and compared by identity
- Keywords can be used as functions for map access

---

### Pattern: Tuples to Vectors or Maps

Erlang tuples are used for fixed-size collections. Clojure uses vectors for positional data and maps for tagged/structured data.

**Erlang:**
```erlang
% Tuples for structured data
User = {user, "Alice", 30, "alice@example.com"}.

% Pattern matching tuples
{user, Name, Age, Email} = User.

% Tagged tuples for result types
{ok, Value} = fetch_data(Key).
{error, Reason} = fetch_data(BadKey).

% Nested tuples
Response = {ok, {user, "Bob", 25}}.
```

**Clojure:**
```clojure
;; Option 1: Vector for positional data (simple tuples)
(def user [:user "Alice" 30 "alice@example.com"])

;; Destructuring vectors
(let [[tag name age email] user]
  (println name age))

;; Option 2: Map for structured data (idiomatic)
(def user {:type :user
           :name "Alice"
           :age 30
           :email "alice@example.com"})

;; Destructuring maps
(let [{:keys [name age email]} user]
  (println name age))

;; Tagged tuples → maps with :ok/:error keys
(def result {:ok value})
(def error-result {:error reason})

;; Pattern matching with map destructuring
(defn handle-result [result]
  (if (:ok result)
    (process (:ok result))
    (log-error (:error result))))

;; Nested structures
(def response {:ok {:type :user :name "Bob" :age 25}})
```

**Why this translation:**
- Maps are more idiomatic for structured data in Clojure
- Keywords as keys provide self-documenting code
- Destructuring works naturally with both vectors and maps
- Maps scale better for optional or evolving schemas

---

### Pattern: List Processing and Pattern Matching

Erlang's list pattern matching is central to the language. Clojure has similar capabilities with destructuring.

**Erlang:**
```erlang
% List pattern matching in function heads
sum([]) -> 0;
sum([H|T]) -> H + sum(T).

length([]) -> 0;
length([_|T]) -> 1 + length(T).

% Multiple elements
process_list([]) -> done;
process_list([Single]) -> {single, Single};
process_list([First, Second]) -> {pair, First, Second};
process_list([First, Second | Rest]) -> {list, First, Second, Rest}.

% List comprehension
Squares = [X*X || X <- [1,2,3,4,5]].
Evens = [X || X <- [1,2,3,4,5,6], X rem 2 == 0].
```

**Clojure:**
```clojure
;; Recursive list processing with loop/recur (tail-call optimized)
(defn sum [lst]
  (loop [remaining lst acc 0]
    (if (empty? remaining)
      acc
      (recur (rest remaining) (+ acc (first remaining))))))

;; Or idiomatically with reduce
(defn sum [lst]
  (reduce + lst))

(defn length-of [lst]
  (if (empty? lst)
    0
    (inc (length-of (rest lst)))))

;; Pattern matching with destructuring
(defn process-list [lst]
  (cond
    (empty? lst) :done
    (= 1 (count lst)) {:single (first lst)}
    (= 2 (count lst)) {:pair (first lst) (second lst)}
    :else (let [[first second & rest] lst]
            {:list first second :rest rest})))

;; List comprehension with for
(def squares (for [x [1 2 3 4 5]]
                (* x x)))

(def evens (for [x [1 2 3 4 5 6]
                 :when (even? x)]
             x))

;; Or with map/filter
(def squares (map #(* % %) [1 2 3 4 5]))
(def evens (filter even? [1 2 3 4 5 6]))
```

**Why this translation:**
- `loop/recur` provides tail-call optimization similar to Erlang
- Higher-order functions (map, filter, reduce) are more idiomatic
- Destructuring provides pattern matching capabilities
- `for` comprehensions similar to Erlang list comprehensions

---

### Pattern: Maps

Both Erlang and Clojure have map data structures, but with different syntax.

**Erlang:**
```erlang
% Creating maps
User = #{name => "Alice", age => 30}.
User2 = #{name := "Bob", age := 25}.  % := for matching

% Accessing values
#{name := Name} = User.
Age = maps:get(age, User).
Email = maps:get(email, User, "no-email").

% Updating maps
User3 = User#{age := 31}.
User4 = User#{email => "alice@example.com"}.

% Map functions
maps:keys(User).
maps:values(User).
maps:is_key(name, User).
maps:merge(User, #{city => "NYC"}).
```

**Clojure:**
```clojure
;; Creating maps
(def user {:name "Alice" :age 30})

;; Accessing values
(let [{:keys [name]} user]
  name)  ; "Alice"

(get user :age)  ; 30
(:age user)  ; 30 (keywords are functions)
(user :age)  ; 30 (maps are functions)
(get user :email "no-email")  ; "no-email" (default)

;; Updating maps
(assoc user :age 31)  ; {:name "Alice" :age 31}
(assoc user :email "alice@example.com")

;; Map functions
(keys user)  ; (:name :age)
(vals user)  ; ("Alice" 30)
(contains? user :name)  ; true
(merge user {:city "NYC"})

;; Nested updates
(assoc-in {:user {:name "Alice"}} [:user :age] 30)
(update-in {:user {:count 0}} [:user :count] inc)
```

**Why this translation:**
- Similar map semantics in both languages
- Clojure keywords as keys are idiomatic
- Both support immutable updates (return new map)
- Clojure's assoc-in/update-in for nested structures

---

## Concurrency Mental Model

### BEAM Processes → JVM Concurrency

The most significant paradigm shift when converting from Erlang to Clojure is the concurrency model.

| Erlang Model | Clojure Approach | Conceptual Translation |
|--------------|------------------|------------------------|
| Lightweight processes | futures, core.async go blocks, agents | Process → concurrent computation |
| Message passing (!) | core.async channels, swap!/send | Send message → put to channel or update state |
| Selective receive | core.async alts!, case on channel | Receive pattern matching → channel selection |
| Process links | Manual error handling | Links → explicit error propagation |
| Supervisors | Manual restart logic or libraries | Supervision → application-level retry |
| gen_server | atom + functions | Stateful server → stateful atom with pure functions |
| gen_statem | atom with state machine | State machine → atom with state + case |

---

### Pattern: Erlang Processes → Clojure Futures/Go Blocks

Erlang processes are lightweight and communicate via message passing. Clojure has multiple concurrency options.

**Erlang:**
```erlang
% Spawn a process
Pid = spawn(fun() -> loop(0) end).

% Send message
Pid ! {self(), increment}.

% Receive message
receive
    {From, increment} ->
        From ! {self(), Count + 1};
    {From, get} ->
        From ! {self(), Count}
end.

% Complete example: simple counter process
-module(counter).
-export([start/0, increment/1, get_value/1, loop/1]).

start() ->
    spawn(?MODULE, loop, [0]).

increment(Pid) ->
    Pid ! {self(), increment},
    receive
        {Pid, Value} -> Value
    end.

get_value(Pid) ->
    Pid ! {self(), get},
    receive
        {Pid, Value} -> Value
    end.

loop(Count) ->
    receive
        {From, increment} ->
            NewCount = Count + 1,
            From ! {self(), NewCount},
            loop(NewCount);
        {From, get} ->
            From ! {self(), Count},
            loop(Count)
    end.
```

**Clojure (with Atoms - Simpler):**
```clojure
;; Use atom for shared state (most idiomatic for simple cases)
(def counter (atom 0))

(defn increment []
  (swap! counter inc))

(defn get-value []
  @counter)

;; Usage:
(increment)  ; => 1
(get-value)  ; => 1
```

**Clojure (with core.async - Process-like):**
```clojure
(require '[clojure.core.async :as async :refer [go chan >! <! >!! <!!]])

;; Create channel for communication
(defn start-counter []
  (let [ch (chan)]
    (go
      (loop [count 0]
        (let [msg (<! ch)]
          (case (:type msg)
            :increment
            (do
              (>! (:reply-ch msg) (inc count))
              (recur (inc count)))

            :get
            (do
              (>! (:reply-ch msg) count)
              (recur count))))))
    ch))

(defn increment [counter-ch]
  (let [reply-ch (chan)]
    (>!! counter-ch {:type :increment :reply-ch reply-ch})
    (<!! reply-ch)))

(defn get-value [counter-ch]
  (let [reply-ch (chan)]
    (>!! counter-ch {:type :get :reply-ch reply-ch})
    (<!! reply-ch)))

;; Usage:
(def counter (start-counter))
(increment counter)  ; => 1
(get-value counter)  ; => 1
```

**Clojure (with Agents - Asynchronous):**
```clojure
;; Agents for asynchronous state updates
(def counter (agent 0))

(defn increment []
  (send counter inc)
  (await counter)
  @counter)

(defn get-value []
  @counter)
```

**Why this translation:**
- Atoms: Simplest for synchronous state management
- core.async: Most similar to Erlang process model
- Agents: Good for asynchronous updates
- No direct equivalent to Erlang's supervision trees

---

### Pattern: gen_server → Atom + Functions

Erlang's gen_server behavior provides structured state management. Clojure uses atoms with pure functions.

**Erlang:**
```erlang
-module(kv_store).
-behaviour(gen_server).

-export([start_link/0, put/2, get/1, delete/1]).
-export([init/1, handle_call/3, handle_cast/2, handle_info/2, terminate/2, code_change/3]).

%%% API

start_link() ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [], []).

put(Key, Value) ->
    gen_server:call(?MODULE, {put, Key, Value}).

get(Key) ->
    gen_server:call(?MODULE, {get, Key}).

delete(Key) ->
    gen_server:cast(?MODULE, {delete, Key}).

%%% Callbacks

init([]) ->
    {ok, #{}}.

handle_call({put, Key, Value}, _From, State) ->
    NewState = maps:put(Key, Value, State),
    {reply, ok, NewState};

handle_call({get, Key}, _From, State) ->
    Value = maps:get(Key, State, undefined),
    {reply, Value, State};

handle_call(_Request, _From, State) ->
    {reply, ok, State}.

handle_cast({delete, Key}, State) ->
    NewState = maps:remove(Key, State),
    {noreply, NewState};

handle_cast(_Msg, State) ->
    {noreply, State}.

handle_info(_Info, State) ->
    {noreply, State}.

terminate(_Reason, _State) ->
    ok.

code_change(_OldVsn, State, _Extra) ->
    {ok, State}.
```

**Clojure:**
```clojure
(ns kv-store)

;; State stored in atom
(defonce store (atom {}))

;; Pure update functions
(defn put-kv [state key value]
  (assoc state key value))

(defn get-kv [state key]
  (get state key))

(defn delete-kv [state key]
  (dissoc state key))

;; Public API - modifies atom
(defn put [key value]
  (swap! store put-kv key value)
  :ok)

(defn get-value [key]
  (get-kv @store key))

(defn delete [key]
  (swap! store delete-kv key)
  nil)

;; Usage:
(put :name "Alice")  ; => :ok
(get-value :name)    ; => "Alice"
(delete :name)       ; => nil
(get-value :name)    ; => nil
```

**Why this translation:**
- Atoms provide atomic, synchronous state updates
- Pure functions for state transformations (testable)
- swap! ensures atomic compare-and-swap operations
- Simpler than gen_server but loses some structure

---

### Pattern: Supervisor → Manual Restart Logic

Erlang supervisors automatically restart failed processes. Clojure requires manual error handling.

**Erlang:**
```erlang
-module(my_supervisor).
-behaviour(supervisor).

-export([start_link/0, init/1]).

start_link() ->
    supervisor:start_link({local, ?MODULE}, ?MODULE, []).

init([]) ->
    SupFlags = #{
        strategy => one_for_one,
        intensity => 5,
        period => 60
    },

    ChildSpecs = [
        #{
            id => worker1,
            start => {worker, start_link, []},
            restart => permanent,
            shutdown => 5000,
            type => worker
        }
    ],

    {ok, {SupFlags, ChildSpecs}}.
```

**Clojure:**
```clojure
;; Manual restart logic with future
(defn supervised-worker [work-fn]
  (future
    (try
      (work-fn)
      (catch Exception e
        (println "Worker failed:" (.getMessage e))
        (Thread/sleep 1000)
        ;; Restart by calling recursively
        (supervised-worker work-fn)))))

;; Or with core.async and restart policy
(defn start-supervised-worker [work-fn]
  (let [control-ch (chan)]
    (go-loop [restarts 0]
      (let [worker-ch (go
                        (try
                          (work-fn)
                          (catch Exception e
                            {:error e})))]
        (let [result (<! worker-ch)]
          (if (:error result)
            (if (< restarts 5)
              (do
                (println "Restarting worker, attempt" (inc restarts))
                (<! (async/timeout 1000))
                (recur (inc restarts)))
              (println "Max restarts exceeded"))
            (println "Worker completed successfully")))))
    control-ch))

;; Using a library like component or mount for lifecycle management
(require '[com.stuartsierra.component :as component])

(defrecord Worker [state]
  component/Lifecycle
  (start [this]
    (println "Starting worker")
    (assoc this :state (atom {})))
  (stop [this]
    (println "Stopping worker")
    (assoc this :state nil)))

(defn create-system []
  (component/system-map
    :worker (map->Worker {})))
```

**Why this translation:**
- No built-in supervision in Clojure
- Use libraries like Component, Mount, or Integrant for lifecycle
- Implement custom restart logic for critical components
- JVM thread pools provide some fault isolation

---

## Error Handling

### Erlang Let it Crash → Clojure Explicit Handling

Erlang's "let it crash" philosophy relies on supervisors to restart failed processes. Clojure requires more explicit error handling.

**Comparison:**

| Aspect | Erlang | Clojure |
|--------|--------|---------|
| Philosophy | Let it crash, supervisor restarts | Explicit error handling |
| Error propagation | Process crash → supervisor notified | Exception throw → catch or propagate |
| Error representation | `{error, Reason}` tuples | `{:error reason}` maps or exceptions |
| Retry logic | Supervisor restart policies | Manual retry with try/catch |
| State recovery | Supervisor re-initializes | Manual state reset or use stateless functions |

**Erlang:**
```erlang
% Let it crash - no defensive code
process_data(Data) ->
    validate(Data),     % Crash if invalid
    transform(Data),    % Crash if fails
    save(Data).        % Crash if fails

% With explicit error handling (less idiomatic)
process_data_safe(Data) ->
    try
        validate(Data),
        transform(Data),
        save(Data),
        {ok, success}
    catch
        error:Reason -> {error, Reason}
    end.

% Supervisor handles restarts
supervisor_init() ->
    SupFlags = #{strategy => one_for_one, intensity => 5, period => 60},
    ChildSpecs = [#{id => worker, start => {worker, start_link, []}}],
    {ok, {SupFlags, ChildSpecs}}.
```

**Clojure:**
```clojure
;; Explicit error handling with try/catch
(defn process-data [data]
  (try
    (validate data)
    (transform data)
    (save data)
    {:ok :success}
    (catch Exception e
      {:error (.getMessage e)})))

;; Using :ok/:error maps pattern (more functional)
(defn validate [data]
  (if (valid? data)
    {:ok data}
    {:error "Invalid data"}))

(defn process-data-functional [data]
  (let [validation (validate data)]
    (if (:ok validation)
      (let [transformed (transform (:ok validation))]
        (if (:ok transformed)
          (save (:ok transformed))
          transformed))
      validation)))

;; Monadic approach with helper
(defn >>= [result f]
  (if (:ok result)
    (f (:ok result))
    result))

(defn process-data-monadic [data]
  (>>= (validate data)
       (fn [valid-data]
         (>>= (transform valid-data)
              (fn [transformed-data]
                (save transformed-data))))))

;; With retry logic
(defn with-retry [f max-retries]
  (loop [attempt 0]
    (let [result (try
                   {:ok (f)}
                   (catch Exception e
                     {:error e}))]
      (if (:ok result)
        (:ok result)
        (if (< attempt max-retries)
          (do
            (Thread/sleep 1000)
            (recur (inc attempt)))
          (throw (:error result)))))))
```

**Why this translation:**
- Clojure requires explicit error handling patterns
- `:ok`/`:error` maps preserve functional style
- No built-in supervision, must implement retry logic
- Exceptions for truly exceptional cases

---

## Common Pitfalls

### 1. Expecting Process Isolation

**Problem:** Erlang processes provide isolation. JVM threads share memory.

```clojure
;; BAD: Shared mutable state across threads
(def counter 0)

(defn increment []
  (def counter (inc counter)))  ; Race condition!

;; Multiple threads calling increment will have race conditions
```

**Fix:** Use atoms for thread-safe updates

```clojure
;; GOOD: Atomic state updates
(def counter (atom 0))

(defn increment []
  (swap! counter inc))  ; Atomic compare-and-swap
```

### 2. Missing Supervision/Restart Logic

**Problem:** Erlang supervisors automatically restart. Clojure doesn't.

```clojure
;; BAD: No error recovery
(future
  (process-forever))  ; If it crashes, it's gone
```

**Fix:** Implement explicit restart logic

```clojure
;; GOOD: Restart on failure
(defn supervised-process [work-fn]
  (future
    (loop []
      (try
        (work-fn)
        (catch Exception e
          (println "Process failed, restarting:" (.getMessage e))
          (Thread/sleep 1000)
          (recur))))))
```

### 3. Over-using core.async

**Problem:** Using core.async when simpler alternatives exist.

```clojure
;; BAD: Overcomplicated for simple state
(def state-ch (chan))

(go-loop [state {}]
  (let [msg (<! state-ch)]
    (recur (update-state state msg))))

(defn update [f]
  (>!! state-ch {:op :update :fn f}))
```

**Fix:** Use atoms for simple state management

```clojure
;; GOOD: Simple atom for state
(def state (atom {}))

(defn update-state [f]
  (swap! state f))
```

### 4. Forgetting JVM Memory Model

**Problem:** Erlang has immutable data by default, but JVM Java objects are mutable.

```clojure
;; BAD: Mutating Java objects
(let [date (java.util.Date.)]
  (.setTime date 0)  ; Mutation!
  date)
```

**Fix:** Use immutable Clojure data structures

```clojure
;; GOOD: Immutable data
(let [instant (java.time.Instant/now)]
  instant)  ; java.time types are immutable
```

### 5. Ignoring Binary/String Differences

**Problem:** Erlang binaries vs Clojure strings/byte-arrays.

```erlang
% Erlang: binary pattern matching
<<Header:4/binary, Payload/binary>> = Data.
```

```clojure
;; Clojure: no built-in binary pattern matching
;; Must use java.nio.ByteBuffer or manual slicing
(let [data (byte-array [1 2 3 4 5 6 7 8])
      header (java.util.Arrays/copyOfRange data 0 4)
      payload (java.util.Arrays/copyOfRange data 4 (alength data))]
  [header payload])
```

---

## Tooling

| Tool | Purpose | Notes |
|------|---------|-------|
| rebar3 (Erlang) | Build tool | No direct equivalent; use Leiningen or CLI |
| Leiningen | Clojure build tool | Project management, dependencies |
| tools.deps/CLI | Modern Clojure CLI | deps.edn for dependencies |
| EUnit/Common Test | Erlang testing | See clojure.test, Midje |
| clojure.test | Built-in testing | Unit testing framework |
| test.check | Property-based testing | Similar to PropEr |
| Dialyzer | Erlang type checker | clojure.spec for runtime validation |
| clojure.spec | Runtime validation | Validates data shapes |
| Observer (Erlang) | Process monitoring | JConsole, VisualVM for JVM |
| REPL (both) | Interactive development | Both support REPL-driven workflow |

---

## Examples

### Example 1: Simple - Tuple Pattern Matching to Map Destructuring

Convert Erlang tuple pattern matching to Clojure map destructuring.

**Before (Erlang):**
```erlang
-module(user).
-export([display_user/1, update_age/2]).

% Tuple-based user
% {user, Name, Age, Email}

display_user({user, Name, Age, Email}) ->
    io:format("User: ~s, Age: ~p, Email: ~s~n", [Name, Age, Email]).

update_age({user, Name, Age, Email}, NewAge) ->
    {user, Name, NewAge, Email}.

% Usage
User = {user, "Alice", 30, "alice@example.com"},
display_user(User),
UpdatedUser = update_age(User, 31).
```

**After (Clojure):**
```clojure
(ns user)

;; Map-based user (idiomatic)
(defn display-user [{:keys [name age email]}]
  (println (str "User: " name ", Age: " age ", Email: " email)))

(defn update-age [user new-age]
  (assoc user :age new-age))

;; Usage
(def user {:name "Alice" :age 30 :email "alice@example.com"})
(display-user user)
(def updated-user (update-age user 31))

;; With spec validation
(require '[clojure.spec.alpha :as s])

(s/def ::name string?)
(s/def ::age pos-int?)
(s/def ::email (s/and string? #(re-matches #".+@.+\..+" %)))
(s/def ::user (s/keys :req-un [::name ::age ::email]))

(defn create-user [name age email]
  (let [user {:name name :age age :email email}]
    (if (s/valid? ::user user)
      {:ok user}
      {:error (s/explain-str ::user user)})))
```

---

### Example 2: Medium - List Processing with Recursion

Convert recursive list processing from Erlang to Clojure.

**Before (Erlang):**
```erlang
-module(list_utils).
-export([map/2, filter/2, sum/1, reverse/1]).

% Map function over list
map(_, []) -> [];
map(F, [H|T]) -> [F(H) | map(F, T)].

% Filter list by predicate
filter(_, []) -> [];
filter(Pred, [H|T]) ->
    case Pred(H) of
        true -> [H | filter(Pred, T)];
        false -> filter(Pred, T)
    end.

% Sum list elements
sum([]) -> 0;
sum([H|T]) -> H + sum(T).

% Reverse a list
reverse(List) -> reverse(List, []).
reverse([], Acc) -> Acc;
reverse([H|T], Acc) -> reverse(T, [H|Acc]).

% Usage
Numbers = [1,2,3,4,5],
Doubled = map(fun(X) -> X * 2 end, Numbers),
Evens = filter(fun(X) -> X rem 2 == 0 end, Numbers),
Total = sum(Numbers),
Reversed = reverse(Numbers).
```

**After (Clojure):**
```clojure
(ns list-utils)

;; Recursive implementations (for learning)
(defn my-map [f lst]
  (if (empty? lst)
    '()
    (cons (f (first lst))
          (my-map f (rest lst)))))

(defn my-filter [pred lst]
  (cond
    (empty? lst) '()
    (pred (first lst)) (cons (first lst)
                             (my-filter pred (rest lst)))
    :else (my-filter pred (rest lst))))

(defn my-sum [lst]
  (if (empty? lst)
    0
    (+ (first lst) (my-sum (rest lst)))))

;; Tail-recursive reverse (loop/recur for tail call optimization)
(defn my-reverse [lst]
  (loop [remaining lst acc '()]
    (if (empty? remaining)
      acc
      (recur (rest remaining) (cons (first remaining) acc)))))

;; Idiomatic Clojure (use built-in functions)
(defn process-numbers [numbers]
  (let [doubled (map #(* % 2) numbers)
        evens (filter even? numbers)
        total (reduce + numbers)
        reversed (reverse numbers)]
    {:doubled doubled
     :evens evens
     :total total
     :reversed reversed}))

;; Usage
(def numbers [1 2 3 4 5])
(process-numbers numbers)
;; => {:doubled (2 4 6 8 10)
;;     :evens (2 4)
;;     :total 15
;;     :reversed (5 4 3 2 1)}

;; Using transducers for efficiency
(defn process-efficiently [numbers]
  (into []
        (comp (map #(* % 2))
              (filter even?))
        numbers))

(process-efficiently [1 2 3 4 5])
;; => [4 8] (doubled AND even)
```

---

### Example 3: Complex - gen_server to Atom-based State Management

Convert a complete gen_server to Clojure with atoms and core.async.

**Before (Erlang):**
```erlang
-module(chat_room).
-behaviour(gen_server).

-export([start_link/0, join/2, leave/1, send_message/2, get_users/0]).
-export([init/1, handle_call/3, handle_cast/2, handle_info/2, terminate/2, code_change/3]).

-record(state, {
    users = #{} :: #{pid() => binary()}
}).

%%% API

start_link() ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [], []).

join(Pid, Username) ->
    gen_server:call(?MODULE, {join, Pid, Username}).

leave(Pid) ->
    gen_server:cast(?MODULE, {leave, Pid}).

send_message(FromPid, Message) ->
    gen_server:cast(?MODULE, {message, FromPid, Message}).

get_users() ->
    gen_server:call(?MODULE, get_users).

%%% Callbacks

init([]) ->
    {ok, #state{}}.

handle_call({join, Pid, Username}, _From, State) ->
    Users = State#state.users,
    case maps:is_key(Pid, Users) of
        true ->
            {reply, {error, already_joined}, State};
        false ->
            monitor(process, Pid),
            NewUsers = maps:put(Pid, Username, Users),
            broadcast({user_joined, Username}, NewUsers),
            {reply, ok, State#state{users = NewUsers}}
    end;

handle_call(get_users, _From, State) ->
    Users = maps:values(State#state.users),
    {reply, {ok, Users}, State};

handle_call(_Request, _From, State) ->
    {reply, ok, State}.

handle_cast({leave, Pid}, State) ->
    Users = State#state.users,
    case maps:get(Pid, Users, undefined) of
        undefined ->
            {noreply, State};
        Username ->
            NewUsers = maps:remove(Pid, Users),
            broadcast({user_left, Username}, NewUsers),
            {noreply, State#state{users = NewUsers}}
    end;

handle_cast({message, FromPid, Message}, State) ->
    Users = State#state.users,
    case maps:get(FromPid, Users, undefined) of
        undefined ->
            {noreply, State};
        Username ->
            broadcast({message, Username, Message}, Users),
            {noreply, State}
    end;

handle_cast(_Msg, State) ->
    {noreply, State}.

handle_info({'DOWN', _Ref, process, Pid, _Reason}, State) ->
    % Handle user disconnect
    Users = State#state.users,
    case maps:get(Pid, Users, undefined) of
        undefined ->
            {noreply, State};
        Username ->
            NewUsers = maps:remove(Pid, Users),
            broadcast({user_left, Username}, NewUsers),
            {noreply, State#state{users = NewUsers}}
    end;

handle_info(_Info, State) ->
    {noreply, State}.

terminate(_Reason, _State) ->
    ok.

code_change(_OldVsn, State, _Extra) ->
    {ok, State}.

%%% Internal

broadcast(Event, Users) ->
    maps:foreach(
        fun(Pid, _Username) ->
            Pid ! Event
        end,
        Users
    ).
```

**After (Clojure):**
```clojure
(ns chat-room
  (:require [clojure.core.async :as async :refer [go go-loop chan >! <! >!! <!! close!]]))

;; State management with atom
(defonce state (atom {:users {}}))

;; Pure state transformation functions
(defn add-user [state user-id username]
  (assoc-in state [:users user-id] {:username username :channel (chan)}))

(defn remove-user [state user-id]
  (update state :users dissoc user-id))

(defn get-user [state user-id]
  (get-in state [:users user-id]))

(defn get-all-users [state]
  (vals (:users state)))

;; Event broadcasting
(defn broadcast [event]
  (let [users (get-all-users @state)]
    (doseq [user users]
      (when-let [ch (:channel user)]
        (go (>! ch event))))))

;; Public API
(defn join [user-id username]
  (if (get-user @state user-id)
    {:error :already-joined}
    (do
      (swap! state add-user user-id username)
      (broadcast {:type :user-joined :username username})
      {:ok :joined})))

(defn leave [user-id]
  (when-let [user (get-user @state user-id)]
    (swap! state remove-user user-id)
    (when-let [ch (:channel user)]
      (close! ch))
    (broadcast {:type :user-left :username (:username user)})))

(defn send-message [user-id message]
  (if-let [user (get-user @state user-id)]
    (do
      (broadcast {:type :message :username (:username user) :message message})
      {:ok :sent})
    {:error :not-joined}))

(defn get-users []
  (map :username (get-all-users @state)))

;; Client message listener
(defn listen-for-messages [user-id callback]
  (when-let [user (get-user @state user-id)]
    (when-let [ch (:channel user)]
      (go-loop []
        (when-let [event (<! ch)]
          (callback event)
          (recur))))))

;; Usage example
(comment
  ;; Join chat room
  (join "user-1" "Alice")  ; => {:ok :joined}
  (join "user-2" "Bob")    ; => {:ok :joined}

  ;; Set up message listener
  (listen-for-messages "user-1"
    (fn [event]
      (println "Event received:" event)))

  ;; Send message
  (send-message "user-1" "Hello everyone!")
  ;; All users receive: {:type :message :username "Alice" :message "Hello everyone!"}

  ;; Get users
  (get-users)  ; => ("Alice" "Bob")

  ;; Leave
  (leave "user-2")  ; Broadcasts {:type :user-left :username "Bob"}
)
```

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `convert-elm-clojure` - Similar functional paradigm conversion
- `lang-erlang-dev` - Erlang development patterns
- `lang-clojure-dev` - Clojure development patterns

Cross-cutting pattern skills:
- `patterns-concurrency-dev` - Processes, actors, async patterns across languages
- `patterns-serialization-dev` - Binary protocols, JSON, EDN across languages
- `patterns-metaprogramming-dev` - Parse transforms vs macros across languages
