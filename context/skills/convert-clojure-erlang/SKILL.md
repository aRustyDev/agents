---
name: convert-clojure-erlang
description: Convert Clojure code to idiomatic Erlang. Use when migrating Clojure projects to Erlang, translating JVM-based functional code to BEAM, or refactoring Clojure codebases to leverage Erlang's fault tolerance and actor model. Extends meta-convert-dev with Clojure-to-Erlang specific patterns.
---

# Convert Clojure to Erlang

Convert Clojure code to idiomatic Erlang, translating from JVM/Lisp-based functional programming to BEAM/Prolog-style functional programming with actors.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Clojure persistent data structures → Erlang immutable data
- **Idiom translations**: Lisp-style functional → Prolog-style functional
- **Concurrency model**: STM + core.async → Actor model (OTP processes)
- **Error handling**: Exceptions → Let-it-crash philosophy
- **REPL workflow**: REPL-driven development translation patterns (9th pillar)
- **Runtime platform**: JVM → BEAM VM migration

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Clojure language fundamentals - see `lang-clojure-dev`
- Erlang language fundamentals - see `lang-erlang-dev`
- Reverse conversion (Erlang → Clojure) - see `convert-erlang-clojure`
- ClojureScript to Erlang - handle as two-step: ClojureScript → Clojure → Erlang

---

## Quick Reference

| Clojure | Erlang | Notes |
|---------|--------|-------|
| `(def x 42)` | `X = 42.` | Variables are immutable in both |
| `(defn f [x] body)` | `f(X) -> Body.` | Function definition |
| `{:key "value"}` | `#{key => <<"value">>}` | Maps (keywords → atoms, strings → binaries) |
| `[1 2 3]` | `[1, 2, 3]` | Lists (vectors → lists) |
| `#{:a :b}` | `sets:from_list([a, b])` | Sets |
| `(atom 0)` | `spawn(fun() -> loop(0) end)` | Mutable state → Process |
| `(swap! a inc)` | `Pid ! increment` | State update |
| `@a` | `Pid ! {self(), get}; receive {Pid, V} -> V end` | State read |
| `(dosync ...)` | `gen_server:call(...)` | Transaction → Synchronous call |
| `(future ...)` | `spawn(fun() -> ... end)` | Async execution |
| `(promise)` | Message passing pattern | Promise-like behavior |

---

## When Converting Code

1. **Analyze Clojure semantics** - Understand STM, lazy sequences, JVM interop
2. **Map concurrency first** - STM/refs/atoms/agents → gen_server/processes
3. **Preserve functional purity** - Both are functional, maintain referential transparency
4. **Adopt Erlang idioms** - Pattern matching, guards, let-it-crash
5. **Handle laziness explicitly** - Clojure's lazy seqs → Erlang generators/streams
6. **Test equivalence** - Property-based testing with PropEr matching test.check

---

## Type System Mapping

### Primitive Types

| Clojure | Erlang | Notes |
|---------|--------|-------|
| `nil` | `undefined` or `nil` atom | Erlang convention: `undefined` |
| `true`/`false` | `true`/`false` | Boolean atoms |
| `42` | `42` | Integers (arbitrary precision in Clojure → big integers in Erlang) |
| `3.14` | `3.14` | Floats |
| `:keyword` | `atom` | Keywords become atoms |
| `"string"` | `<<"binary">>` or `"list"` | Prefer binaries for efficiency |
| `\c` | `$c` or `<<"c">>` | Character → integer or binary |
| Symbol | Atom | Both are interned identifiers |

### Collection Types

| Clojure | Erlang | Notes |
|---------|--------|-------|
| `[1 2 3]` | `[1, 2, 3]` | Vectors → Lists (note: O(1) vs O(n) append) |
| `'(1 2 3)` | `[1, 2, 3]` | Lists → Lists (direct mapping) |
| `{:a 1 :b 2}` | `#{a => 1, b => 2}` | Maps → Maps |
| `#{:a :b :c}` | `sets:from_list([a, b, c])` or `#{a, b, c}` (MapSet pattern) | Sets |
| Lazy seq | Generator fun or `lists:seq/2` | Explicit laziness needed |
| `(range)` | `lists:seq(0, ...)` or generator | Infinite sequences require explicit handling |
| `(iterate f x)` | Generator function | Create custom generator |

### Composite Types

| Clojure | Erlang | Notes |
|---------|--------|-------|
| `defrecord` | `-record(...)` or map with type tag | Records or typed maps |
| `deftype` | Module with constructor | Encapsulation via module |
| `defprotocol` | `-behavior(...)` callback module | Polymorphism |
| Namespace | Module | Direct mapping |
| Var | Process or ETS table | For mutable global state |

---

## Idiom Translation

### Pattern: Function Definition

**Clojure:**
```clojure
(defn factorial
  "Calculates factorial of n"
  [n]
  (if (<= n 1)
    1
    (* n (factorial (dec n)))))
```

**Erlang:**
```erlang
% Calculates factorial of n
factorial(N) when N =< 1 -> 1;
factorial(N) -> N * factorial(N - 1).
```

**Why this translation:**
- Erlang uses guards (`when`) instead of explicit `if`
- Pattern matching in function clauses is more idiomatic than conditionals
- Multiple function clauses replace Clojure's single function with conditional body

---

### Pattern: Map Operations

**Clojure:**
```clojure
(defn update-user [user]
  (-> user
      (assoc :updated-at (System/currentTimeMillis))
      (update :age inc)
      (dissoc :temp-field)))
```

**Erlang:**
```erlang
update_user(User) ->
    User1 = maps:put(updated_at, erlang:system_time(millisecond), User),
    User2 = maps:update_with(age, fun(Age) -> Age + 1 end, User1),
    maps:remove(temp_field, User2).

% Or with pattern matching
update_user(#{age := Age} = User) ->
    User#{
        updated_at => erlang:system_time(millisecond),
        age => Age + 1
    }.
```

**Why this translation:**
- Threading macro `->` becomes sequential variable binding
- `assoc` → `maps:put` or map update syntax
- `update` → `maps:update_with` or pattern match + update
- `dissoc` → `maps:remove`

---

### Pattern: Collection Processing

**Clojure:**
```clojure
(defn process-users [users]
  (->> users
       (filter :active)
       (map #(update % :name str/upper-case))
       (take 10)
       (group-by :department)))
```

**Erlang:**
```erlang
process_users(Users) ->
    Active = lists:filter(fun(#{active := A}) -> A end, Users),
    Uppercased = lists:map(
        fun(#{name := Name} = U) ->
            U#{name => string:uppercase(Name)}
        end,
        Active
    ),
    TopTen = lists:sublist(Uppercased, 10),
    group_by(department, TopTen).

group_by(Key, List) ->
    lists:foldl(
        fun(#{Key := Val} = Item, Acc) ->
            maps:update_with(Val, fun(Items) -> [Item | Items] end, [Item], Acc)
        end,
        #{},
        List
    ).
```

**Why this translation:**
- Threading last `->>` becomes explicit function composition
- `filter`, `map`, `take` map to `lists:filter/2`, `lists:map/2`, `lists:sublist/2`
- `group-by` requires custom implementation (no stdlib equivalent)
- Clojure's lazy evaluation becomes eager in Erlang

---

### Pattern: Destructuring

**Clojure:**
```clojure
(defn greet [{:keys [name age] :or {age 0}}]
  (str "Hello " name ", you are " age))

(let [[first second & rest] items]
  (process first second rest))
```

**Erlang:**
```erlang
greet(#{name := Name, age := Age}) ->
    lists:flatten(io_lib:format("Hello ~s, you are ~p", [Name, Age]));
greet(#{name := Name}) ->
    greet(#{name => Name, age => 0}).

process_items([First, Second | Rest]) ->
    do_process(First, Second, Rest).
```

**Why this translation:**
- Map destructuring in function arguments is similar
- Default values require separate function clause
- List destructuring `[H|T]` is similar to Clojure's `[first & rest]`

---

### Pattern: Recursion and Accumulation

**Clojure:**
```clojure
(defn sum [coll]
  (reduce + 0 coll))

(defn sum-recursive [coll]
  (loop [items coll acc 0]
    (if (empty? items)
      acc
      (recur (rest items) (+ acc (first items))))))
```

**Erlang:**
```erlang
% Using fold
sum(Coll) ->
    lists:foldl(fun(X, Acc) -> X + Acc end, 0, Coll).

% Using tail recursion
sum_recursive(Coll) ->
    sum_recursive(Coll, 0).

sum_recursive([], Acc) -> Acc;
sum_recursive([H|T], Acc) ->
    sum_recursive(T, Acc + H).
```

**Why this translation:**
- `reduce` → `lists:foldl`
- `loop/recur` → tail-recursive function with accumulator
- Both optimize tail calls, so performance is similar

---

### Pattern: Lazy Sequences

**Clojure:**
```clojure
(defn fibonacci []
  (map first (iterate (fn [[a b]] [b (+ a b)]) [0 1])))

(take 10 (fibonacci))
```

**Erlang:**
```erlang
% Generator pattern
fibonacci() ->
    fun Loop(A, B) ->
        fun() -> {A, Loop(B, A + B)} end
    end(0, 1).

take(0, _Generator) -> [];
take(N, Generator) ->
    {Value, Next} = Generator(),
    [Value | take(N - 1, Next)].

% Usage
Fib = fibonacci(),
take(10, Fib).
```

**Why this translation:**
- Clojure's lazy sequences don't have direct equivalent
- Generator pattern (function returning function) provides laziness
- Explicit `take` function to realize values
- Erlang processes can also model infinite sequences

---

## Concurrency Model Translation

### STM (Refs) → gen_server

**Clojure:**
```clojure
(def account-a (ref 100))
(def account-b (ref 200))

(defn transfer [from to amount]
  (dosync
    (alter from - amount)
    (alter to + amount)))

(transfer account-a account-b 50)
```

**Erlang:**
```erlang
% Using gen_server for coordinated state
-module(account_server).
-behaviour(gen_server).

start_link(Initial) ->
    gen_server:start_link(?MODULE, Initial, []).

transfer(From, To, Amount) ->
    % Withdraw from source
    ok = gen_server:call(From, {withdraw, Amount}),
    try
        % Deposit to destination
        ok = gen_server:call(To, {deposit, Amount})
    catch
        error:Reason ->
            % Rollback on failure
            gen_server:call(From, {deposit, Amount}),
            {error, Reason}
    end.

handle_call({withdraw, Amount}, _From, Balance) when Balance >= Amount ->
    {reply, ok, Balance - Amount};
handle_call({withdraw, _Amount}, _From, Balance) ->
    {reply, {error, insufficient_funds}, Balance};
handle_call({deposit, Amount}, _From, Balance) ->
    {reply, ok, Balance + Amount}.
```

**Why this translation:**
- STM transactions become explicit message passing
- `dosync` coordination becomes manual two-phase approach or single coordinator
- Erlang emphasizes explicit rollback vs automatic retry
- Alternative: Use a single coordinator gen_server managing both accounts

---

### Atoms → Process Mailbox

**Clojure:**
```clojure
(def counter (atom 0))

(swap! counter inc)
(swap! counter + 5)
@counter  ; => 6
```

**Erlang:**
```erlang
% Process-based counter
start_counter(Initial) ->
    spawn(fun() -> counter_loop(Initial) end).

counter_loop(Count) ->
    receive
        {From, increment} ->
            From ! {ok, Count + 1},
            counter_loop(Count + 1);
        {From, {add, N}} ->
            From ! {ok, Count + N},
            counter_loop(Count + N);
        {From, get} ->
            From ! {ok, Count},
            counter_loop(Count);
        stop ->
            ok
    end.

% Client functions
increment(Pid) ->
    Pid ! {self(), increment},
    receive {ok, NewValue} -> NewValue end.

add(Pid, N) ->
    Pid ! {self(), {add, N}},
    receive {ok, NewValue} -> NewValue end.

get_value(Pid) ->
    Pid ! {self(), get},
    receive {ok, Value} -> Value end.
```

**Why this translation:**
- Atoms are lightweight in Clojure but require process in Erlang
- Message passing replaces direct state mutation
- `swap!` becomes send-receive pattern
- `@atom` (deref) becomes query message

---

### core.async Channels → Erlang Processes/Messages

**Clojure:**
```clojure
(require '[clojure.core.async :as async])

(defn producer [ch]
  (async/go
    (dotimes [i 10]
      (async/>! ch i))
    (async/close! ch)))

(defn consumer [ch]
  (async/go-loop []
    (when-let [value (async/<! ch)]
      (println "Got:" value)
      (recur))))

(let [ch (async/chan 10)]
  (producer ch)
  (consumer ch))
```

**Erlang:**
```erlang
producer(ConsumerPid) ->
    spawn(fun() ->
        lists:foreach(
            fun(I) ->
                ConsumerPid ! {value, I}
            end,
            lists:seq(0, 9)
        ),
        ConsumerPid ! done
    end).

consumer() ->
    spawn(fun() -> consumer_loop() end).

consumer_loop() ->
    receive
        {value, Value} ->
            io:format("Got: ~p~n", [Value]),
            consumer_loop();
        done ->
            ok
    end.

% Usage
Consumer = consumer(),
producer(Consumer).
```

**Why this translation:**
- Channels become direct message passing between processes
- `go` blocks become spawned processes
- `<!` (take) becomes `receive`
- `>!` (put) becomes `!` (send)
- Channel closing becomes sentinel message (`done`)

---

## Error Handling Translation

### Exceptions → Let-It-Crash

**Clojure:**
```clojure
(defn process-data [data]
  (try
    (validate-data data)
    (transform-data data)
    (save-data data)
    (catch Exception e
      (log-error e)
      {:error (.getMessage e)})))
```

**Erlang (Anti-pattern - too defensive):**
```erlang
% DON'T DO THIS - too defensive
process_data(Data) ->
    try
        validate_data(Data),
        Transformed = transform_data(Data),
        save_data(Transformed)
    catch
        error:Reason ->
            log_error(Reason),
            {error, Reason}
    end.
```

**Erlang (Idiomatic - let it crash):**
```erlang
% DO THIS - let supervisor handle failures
process_data(Data) ->
    validate_data(Data),  % Crash if invalid
    Transformed = transform_data(Data),  % Crash if transform fails
    save_data(Transformed).  % Crash if save fails

% Supervisor will restart the worker on crash
init([]) ->
    SupFlags = #{
        strategy => one_for_one,
        intensity => 5,
        period => 60
    },
    ChildSpecs = [
        #{
            id => worker,
            start => {worker, start_link, []},
            restart => permanent,
            shutdown => 5000,
            type => worker
        }
    ],
    {ok, {SupFlags, ChildSpecs}}.
```

**Why this translation:**
- Clojure's exceptions become crashes in Erlang
- Try-catch only for expected errors, not exceptional conditions
- Supervisors handle process failure and restart
- Defensive programming discouraged in favor of supervision trees

---

### Error Tuples Pattern

**Clojure:**
```clojure
(defn find-user [id users]
  (if-let [user (first (filter #(= id (:id %)) users))]
    {:ok user}
    {:error :not-found}))
```

**Erlang:**
```erlang
find_user(Id, Users) ->
    case lists:keyfind(Id, #user.id, Users) of
        {user, Id, _, _} = User ->
            {ok, User};
        false ->
            {error, not_found}
    end.

% Or with list comprehension
find_user(Id, Users) ->
    case [U || #{id := UserId} = U <- Users, UserId =:= Id] of
        [User | _] -> {ok, User};
        [] -> {error, not_found}
    end.
```

**Why this translation:**
- Both use tagged tuples for error handling
- Erlang's pattern matching makes error handling cleaner
- `{ok, Value}` and `{error, Reason}` are Erlang conventions

---

## REPL-Driven Development Translation

Both Clojure and Erlang are REPL-centric languages, making workflow translation smoother than compiled → REPL conversions.

### Development Workflow Comparison

| Clojure Workflow | Erlang Equivalent | Translation Notes |
|------------------|-------------------|-------------------|
| Start REPL (`lein repl`) | Start shell (`erl` or `rebar3 shell`) | Both provide interactive environments |
| Send form to REPL (editor integration) | Compile module (`c(module)`) | Erlang reloads entire modules |
| Hot reload namespace | Hot code loading (`c:l(module)`) | Erlang's hot swapping is production-ready |
| REPL-driven design | REPL-driven design | Both support incremental development |
| `(doc fn)` | `h(module)` or `module:module_info()` | Documentation lookup |
| `(source fn)` | Decompile with `erlang:load_module/2` | Less common in Erlang |

### Interactive Development Example

**Clojure:**
```clojure
;; In REPL
user=> (defn process-user [user]
         (-> user
             (update :name str/upper-case)
             (assoc :processed true)))

user=> (process-user {:name "alice" :age 30})
;; => {:name "ALICE", :age 30, :processed true}

;; Refine in REPL
user=> (defn process-user [user]
         (-> user
             (update :name str/upper-case)
             (assoc :processed-at (System/currentTimeMillis))))

;; Test immediately
user=> (process-user {:name "alice"})
```

**Erlang:**
```erlang
% In shell
1> c(user_processor).
{ok,user_processor}

2> user_processor:process_user(#{name => "alice", age => 30}).
#{name => "ALICE", age => 30, processed => true}

% Edit user_processor.erl, then reload
3> c(user_processor).
{ok,user_processor}

4> user_processor:process_user(#{name => "alice"}).
#{name => "ALICE",
  processed_at => 1704067200000}
```

**Translation notes:**
- Clojure allows redefining individual functions in REPL
- Erlang recompiles entire modules
- Both support rapid iteration and testing
- Erlang's hot code loading works in production (Clojure requires restart)

### REPL Testing Patterns

**Clojure:**
```clojure
;; Quick test in REPL
(defn validate-email [email]
  (re-matches #".+@.+\..+" email))

;; Test interactively
user=> (validate-email "test@example.com")
;; => "test@example.com"

user=> (validate-email "invalid")
;; => nil
```

**Erlang:**
```erlang
% Quick test in shell
validate_email(Email) ->
    case re:run(Email, ".+@.+\\..+") of
        {match, _} -> {ok, Email};
        nomatch -> {error, invalid_email}
    end.

% Test interactively
1> c(validator).
{ok,validator}

2> validator:validate_email(<<"test@example.com">>).
{ok,<<"test@example.com">>}

3> validator:validate_email(<<"invalid">>).
{error,invalid_email}
```

---

## Module System Translation

**Clojure:**
```clojure
(ns myapp.user-service
  "User service with CRUD operations"
  (:require [clojure.string :as str]
            [myapp.database :as db]
            [myapp.validation :refer [validate-email]]))

(defn create-user [user-data]
  (let [validated (validate-email (:email user-data))]
    (db/insert :users validated)))
```

**Erlang:**
```erlang
-module(user_service).
-export([create_user/1]).

% No docstring at module level, use comments
% User service with CRUD operations

create_user(UserData) ->
    Email = maps:get(email, UserData),
    case validation:validate_email(Email) of
        {ok, ValidEmail} ->
            database:insert(users, ValidEmail);
        {error, Reason} ->
            {error, Reason}
    end.
```

**Translation notes:**
- Namespaces → Modules (one-to-one mapping)
- `:require` → module calls (always qualified)
- `:refer` → direct function calls (no import mechanism, use full module name)
- Private functions: prefix with internal convention or don't export

---

## Macros and Metaprogramming

### Clojure Macros → Erlang Parse Transforms

**Clojure:**
```clojure
(defmacro unless [condition & body]
  `(if (not ~condition)
     (do ~@body)))

(unless false
  (println "This runs"))
```

**Erlang:**
```erlang
% Parse transforms are more complex, typically use macros instead
-define(UNLESS(Cond, Body),
    case (not Cond) of
        true -> Body;
        false -> ok
    end).

% Usage
?UNLESS(false, io:format("This runs~n")).

% For true metaprogramming, use parse transforms (advanced)
% See lang-erlang-dev for parse transform examples
```

**Translation notes:**
- Clojure macros are more powerful and easier to write
- Erlang macros are textual substitution (C-style)
- Complex metaprogramming requires parse transforms (AST manipulation)
- Most Clojure macro use cases can be solved with higher-order functions in Erlang

---

## Build System and Dependencies

### project.clj → rebar.config

**Clojure (Leiningen):**
```clojure
(defproject myapp "0.1.0-SNAPSHOT"
  :description "My Clojure application"
  :dependencies [[org.clojure/clojure "1.11.1"]
                 [ring/ring-core "1.10.0"]
                 [cheshire "5.12.0"]]
  :main myapp.core)
```

**Erlang (Rebar3):**
```erlang
{erl_opts, [debug_info]}.

{deps, [
    {cowboy, "2.10.0"},  % Ring equivalent for Erlang
    {jsx, "3.1.0"}       % JSON library (Cheshire equivalent)
]}.

{relx, [
    {release, {myapp, "0.1.0"}, [
        myapp,
        sasl
    ]},
    {mode, dev}
]}.
```

### deps.edn → rebar.config

**Clojure (tools.deps):**
```clojure
{:deps {org.clojure/clojure {:mvn/version "1.11.1"}
        ring/ring-core {:mvn/version "1.10.0"}
        cheshire/cheshire {:mvn/version "5.12.0"}}}
```

**Erlang (Rebar3):**
```erlang
{deps, [
    {cowboy, "2.10.0"},
    {jsx, "3.1.0"}
]}.
```

---

## Testing Strategy Translation

### test.check → PropEr

**Clojure:**
```clojure
(require '[clojure.test.check :as tc]
         '[clojure.test.check.generators :as gen]
         '[clojure.test.check.properties :as prop])

(def prop-reverse
  (prop/for-all [v (gen/vector gen/small-integer)]
    (= v (reverse (reverse v)))))

(tc/quick-check 100 prop-reverse)
```

**Erlang:**
```erlang
-include_lib("proper/include/proper.hrl").

prop_reverse() ->
    ?FORALL(List, list(integer()),
            lists:reverse(lists:reverse(List)) =:= List).

% Run
proper:quickcheck(prop_reverse(), [{numtests, 100}]).
```

### clojure.test → EUnit

**Clojure:**
```clojure
(ns myapp.core-test
  (:require [clojure.test :refer [deftest is testing]]
            [myapp.core :as core]))

(deftest addition-test
  (testing "Basic addition"
    (is (= 4 (core/add 2 2)))
    (is (= 0 (core/add -1 1)))))
```

**Erlang:**
```erlang
-module(core_tests).
-include_lib("eunit/include/eunit.hrl").

addition_test() ->
    ?assertEqual(4, core:add(2, 2)),
    ?assertEqual(0, core:add(-1, 1)).
```

---

## Common Patterns

### Polymorphism: Protocols → Behaviors

**Clojure:**
```clojure
(defprotocol Storage
  (save [this data])
  (load [this id]))

(defrecord FileStorage [path]
  Storage
  (save [this data] (spit (:path this) data))
  (load [this id] (slurp (str (:path this) "/" id))))

(defrecord DbStorage [conn]
  Storage
  (save [this data] (db/insert (:conn this) data))
  (load [this id] (db/query (:conn this) id)))
```

**Erlang:**
```erlang
% Define behavior
-module(storage).
-callback save(State :: term(), Data :: term()) -> {ok, term()} | {error, term()}.
-callback load(State :: term(), Id :: term()) -> {ok, term()} | {error, term()}.

% File storage implementation
-module(file_storage).
-behaviour(storage).
-export([save/2, load/2]).

save(#{path := Path}, Data) ->
    file:write_file(Path, term_to_binary(Data)).

load(#{path := Path}, Id) ->
    Filename = filename:join(Path, Id),
    case file:read_file(Filename) of
        {ok, Binary} -> {ok, binary_to_term(Binary)};
        Error -> Error
    end.

% DB storage implementation
-module(db_storage).
-behaviour(storage).
-export([save/2, load/2]).

save(#{conn := Conn}, Data) ->
    database:insert(Conn, Data).

load(#{conn := Conn}, Id) ->
    database:query(Conn, Id).
```

---

## Performance Considerations

### Lazy Evaluation

**Issue:** Clojure's lazy sequences are evaluated on-demand; Erlang is eager by default.

**Impact:** Memory usage and performance characteristics differ.

**Solution:**
```erlang
% Use generator pattern for lazy evaluation
lazy_range(Start, End) when Start > End ->
    fun() -> done end;
lazy_range(Start, End) ->
    fun() -> {Start, lazy_range(Start + 1, End)} end.

take_lazy(0, _Gen) -> [];
take_lazy(_, Gen) when is_function(Gen, 0) ->
    case Gen() of
        done -> [];
        {Value, Next} -> [Value | take_lazy(N - 1, Next)]
    end.
```

### Persistent Data Structures

Both Clojure and Erlang use persistent (immutable) data structures, but implementations differ:

- Clojure: Hash Array Mapped Tries (HAMT) for vectors and maps
- Erlang: Balanced trees for ordered sets, hash tables for maps

**Performance:**
- Clojure vectors: O(log32 n) access and update
- Erlang lists: O(n) access, O(1) prepend
- Both maps: O(log n) average

**Translation guideline:**
- Clojure vector → Erlang list (accept O(n) or use arrays for random access)
- Frequent appends: Build reversed list, then reverse once at end

---

## Common Pitfalls

### 1. Atom Table Exhaustion

**Pitfall:** Converting Clojure keywords to Erlang atoms dynamically

```erlang
% BAD - can exhaust atom table
process_json(Json) ->
    maps:map(
        fun(K, V) -> {list_to_atom(binary_to_list(K)), V} end,
        Json
    ).

% GOOD - keep keys as binaries or use known atoms
process_json(Json) ->
    % Keep keys as binaries, or whitelist known atoms
    Json.
```

### 2. String vs Binary Confusion

**Pitfall:** Clojure strings become Erlang lists by default (inefficient)

```erlang
% BAD - string as list
"hello" = [$h, $e, $l, $l, $o].  % Inefficient

% GOOD - use binaries
<<"hello">>.  % Efficient
```

### 3. STM Coordination Assumptions

**Pitfall:** Assuming automatic conflict resolution like Clojure's STM

```erlang
% NO automatic retry in Erlang
% Must handle conflicts explicitly or use gen_server for coordination
```

### 4. Lazy Sequence Realization

**Pitfall:** Assuming lazy evaluation (Clojure default)

```erlang
% Erlang is eager - realize sequences immediately
% Use generators for large or infinite sequences
```

### 5. Namespace Confusion

**Pitfall:** Expecting Clojure-style namespace aliasing

```erlang
% NO automatic aliasing
% Must use full module names: module:function()
% Or use -import (rarely used in Erlang)
```

---

## Tooling

| Tool | Purpose | Notes |
|------|---------|-------|
| `rebar3` | Build tool | Equivalent to Leiningen/tools.deps |
| `erlang.mk` | Alternative build | Makefile-based build system |
| `dialyzer` | Static analysis | Type checking for Erlang |
| `PropEr` | Property testing | Equivalent to test.check |
| `Common Test` | Integration testing | More comprehensive than EUnit |
| `observer` | Runtime inspection | GUI tool for debugging, profiling |
| `recon` | Production debugging | Runtime inspection and debugging |

---

## Examples

### Example 1: Simple - Function with Pattern Matching

**Before (Clojure):**
```clojure
(defn greet
  ([name] (greet name "Hello"))
  ([name greeting]
   (str greeting ", " name "!")))

(greet "Alice")          ;; => "Hello, Alice!"
(greet "Bob" "Hi")       ;; => "Hi, Bob!"
```

**After (Erlang):**
```erlang
greet(Name) ->
    greet(Name, "Hello").

greet(Name, Greeting) ->
    lists:flatten(io_lib:format("~s, ~s!", [Greeting, Name])).

% Usage
greet("Alice").          % => "Hello, Alice!"
greet("Bob", "Hi").      % => "Hi, Bob!"
```

---

### Example 2: Medium - Map Processing with Error Handling

**Before (Clojure):**
```clojure
(defn validate-user [user]
  (let [errors (cond-> []
                 (empty? (:name user)) (conj :name-required)
                 (< (:age user 0) 18) (conj :age-too-young)
                 (not (re-matches #".+@.+" (:email user "")))
                   (conj :invalid-email))]
    (if (empty? errors)
      {:ok user}
      {:error errors})))

(defn create-user [user-data]
  (let [{:keys [ok error]} (validate-user user-data)]
    (if ok
      (db/insert ok)
      {:error error})))
```

**After (Erlang):**
```erlang
validate_user(User) ->
    Errors = validate_user_fields(User, []),
    case Errors of
        [] -> {ok, User};
        _ -> {error, Errors}
    end.

validate_user_fields(#{name := Name, age := Age, email := Email} = User, Errors) ->
    Errors1 = case Name of
        <<>> -> [name_required | Errors];
        _ -> Errors
    end,
    Errors2 = case Age of
        A when A < 18 -> [age_too_young | Errors1];
        _ -> Errors1
    end,
    case re:run(Email, ".+@.+") of
        {match, _} -> Errors2;
        nomatch -> [invalid_email | Errors2]
    end;
validate_user_fields(_, Errors) ->
    [missing_fields | Errors].

create_user(UserData) ->
    case validate_user(UserData) of
        {ok, User} ->
            database:insert(User);
        {error, Errors} ->
            {error, Errors}
    end.
```

---

### Example 3: Complex - Concurrent Worker Pool with Supervision

**Before (Clojure):**
```clojure
(require '[clojure.core.async :as async])

(defn worker [id tasks results]
  (async/go-loop []
    (when-let [task (async/<! tasks)]
      (try
        (let [result (process-task task)]
          (async/>! results {:worker id :result result}))
        (catch Exception e
          (async/>! results {:worker id :error (.getMessage e)})))
      (recur))))

(defn start-worker-pool [n-workers]
  (let [tasks (async/chan 100)
        results (async/chan 100)
        workers (doall (map #(worker % tasks results) (range n-workers)))]
    {:tasks tasks
     :results results
     :workers workers}))

(defn submit-task [pool task]
  (async/>!! (:tasks pool) task))

(defn get-result [pool]
  (async/<!! (:results pool)))

;; Usage
(def pool (start-worker-pool 5))
(submit-task pool {:type :compute :data [1 2 3]})
(get-result pool)
```

**After (Erlang):**
```erlang
-module(worker_pool).
-behaviour(supervisor).

%% API
-export([start_link/1, submit_task/2, get_results/1]).

%% Supervisor callbacks
-export([init/1]).

%% Worker functions
-export([worker_loop/2]).

%%% API Functions

start_link(NumWorkers) ->
    supervisor:start_link({local, ?MODULE}, ?MODULE, NumWorkers).

submit_task(Task, ResultsPid) ->
    % Get random worker
    Workers = supervisor:which_children(?MODULE),
    {_, WorkerPid, _, _} = lists:nth(rand:uniform(length(Workers)), Workers),
    WorkerPid ! {task, Task, ResultsPid}.

get_results(ResultsPid) ->
    receive
        {result, Result} -> {ok, Result};
        {error, Reason} -> {error, Reason}
    after 5000 ->
        {error, timeout}
    end.

%%% Supervisor Callbacks

init(NumWorkers) ->
    SupFlags = #{
        strategy => one_for_one,
        intensity => 10,
        period => 60
    },

    WorkerSpecs = [
        #{
            id => {worker, Id},
            start => {?MODULE, worker_loop, [Id, self()]},
            restart => permanent,
            shutdown => 5000,
            type => worker
        } || Id <- lists:seq(1, NumWorkers)
    ],

    {ok, {SupFlags, WorkerSpecs}}.

%%% Worker Functions

worker_loop(Id, SupervisorPid) ->
    receive
        {task, Task, ResultsPid} ->
            try process_task(Task) of
                Result ->
                    ResultsPid ! {result, #{worker => Id, result => Result}},
                    worker_loop(Id, SupervisorPid)
            catch
                error:Reason ->
                    ResultsPid ! {error, #{worker => Id, error => Reason}},
                    worker_loop(Id, SupervisorPid)
            end;
        stop ->
            ok
    end.

process_task(#{type := compute, data := Data}) ->
    % Process task
    lists:sum(Data).

%%% Usage Example

% Start pool
{ok, PoolPid} = worker_pool:start_link(5).

% Submit task
ResultsPid = spawn(fun() ->
    receive
        {result, R} -> io:format("Got result: ~p~n", [R])
    end
end),

worker_pool:submit_task(#{type => compute, data => [1,2,3]}, ResultsPid).
```

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `convert-clojure-elixir` - Similar conversion (JVM LISP → BEAM LISP)
- `convert-clojure-haskell` - Dynamic FP → Static FP patterns
- `convert-python-erlang` - Imperative → Actor model patterns
- `lang-clojure-dev` - Clojure development patterns
- `lang-erlang-dev` - Erlang development patterns

Cross-cutting pattern skills:
- `patterns-concurrency-dev` - Async, channels, processes across languages
- `patterns-serialization-dev` - JSON, validation across languages
- `patterns-metaprogramming-dev` - Macros, parse transforms across languages
