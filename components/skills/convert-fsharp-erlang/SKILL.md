---
name: convert-fsharp-erlang
description: Convert F# code to idiomatic Erlang. Use when migrating F# projects to Erlang/OTP, translating .NET functional patterns to BEAM/OTP patterns, or refactoring F# codebases to leverage Erlang's fault-tolerance and distribution. Extends meta-convert-dev with F#-to-Erlang specific patterns.
---

# Convert F# to Erlang

Convert F# code to idiomatic Erlang. This skill extends `meta-convert-dev` with F#-to-Erlang specific type mappings, idiom translations, and tooling for migrating functional .NET code to the BEAM VM and OTP framework.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: F# types → Erlang types and records
- **Idiom translations**: F# patterns → idiomatic Erlang/OTP
- **Error handling**: F# Result/Option → Erlang tuples and let-it-crash
- **Concurrency patterns**: F# async/Task → Erlang processes and OTP behaviors
- **Computation expressions**: F# workflows → Erlang gen_server/gen_statem
- **Platform migration**: .NET/CLR → BEAM VM and OTP

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- F# language fundamentals - see `lang-fsharp-dev`
- Erlang language fundamentals - see `lang-erlang-dev`
- Reverse conversion (Erlang → F#) - see `convert-erlang-fsharp`

---

## Quick Reference

| F# | Erlang | Notes |
|------------|------|-------|
| `string` | `binary()` / `list()` | UTF-8 binary or char list |
| `int` | `integer()` | Arbitrary precision |
| `float` | `float()` | IEEE 754 double |
| `bool` | `true` / `false` | Atoms |
| `'a option` | `{ok, Value} \| error` | Tagged tuple |
| `Result<'T,'E>` | `{ok, Value} \| {error, Reason}` | Tagged tuple |
| `'a list` | `list()` | Linked list |
| `'a []` | `tuple()` / `array()` | Fixed-size tuple or array module |
| `Map<'K,'V>` | `map()` / `#{K => V}` | Map literal or maps module |
| `Set<'T>` | `sets:set()` / `ordsets` | Sets module |
| `type Record` | `-record(name, {...})` | Record definition |
| `type Union` | Tagged tuples | Discriminated union via tuples |
| `async { }` | `spawn()` / `gen_server` | Lightweight process |
| `Task<'T>` | `pid()` | Process identifier |
| `seq<'T>` | Lazy list or stream | Process-based streaming |

## When Converting Code

1. **Analyze source thoroughly** before writing target
2. **Map types first** - create type equivalence table
3. **Preserve semantics** over syntax similarity
4. **Adopt Erlang/OTP idioms** - don't write "F# code in Erlang syntax"
5. **Embrace let-it-crash** - replace defensive programming with supervision
6. **Handle edge cases** - null safety, error paths, process lifecycle
7. **Test equivalence** - same inputs → same outputs

---

## Type System Mapping

### Primitive Types

| F# | Erlang | Notes |
|------------|------|-------|
| `string` | `binary()` | UTF-8 binary (most common): `<<"Hello">>` |
| `string` | `string()` | Character list (for compatibility): `"Hello"` |
| `int` | `integer()` | Arbitrary precision integer |
| `int8` / `int16` / `int32` / `int64` | `integer()` | All map to integer(); note in comments |
| `uint8` / `uint16` / `uint32` / `uint64` | `integer()` | Erlang integers are signed; add guards |
| `float` / `double` | `float()` | IEEE 754 double precision |
| `decimal` | `float()` or custom | No native decimal; use library or tuples |
| `bool` | `true` / `false` | Atoms (lowercase) |
| `char` | `integer()` | Unicode codepoint |
| `byte` | `integer()` | 0-255 range |
| `unit` | `ok` | Atom representing success |
| `obj` | `any()` / `term()` | Any Erlang term |

### Option and Result Types

| F# | Erlang | Notes |
|------------|------|-------|
| `None` | `undefined` / `error` | Atom for absence |
| `Some x` | `{ok, X}` | Tagged tuple for presence |
| `'a option` | `{ok, Value} \| error \| undefined` | Common pattern |
| `Ok x` | `{ok, X}` | Success tuple |
| `Error e` | `{error, Reason}` | Error tuple with reason |
| `Result<'T,'E>` | `{ok, Value} \| {error, Reason}` | Standard error pattern |

### Collection Types

| F# | Erlang | Notes |
|------------|------|-------|
| `'a list` | `list()` | Linked list: `[1, 2, 3]` |
| `'a []` (array) | `tuple()` | Fixed-size: `{1, 2, 3}` |
| `'a []` (array) | `array:array()` | Mutable array module |
| `seq<'a>` | Lazy list / `gen_server` | Stream via process |
| `Map<'K,'V>` | `#{K => V}` | Map literal (Erlang 17+) |
| `Map<'K,'V>` | `dict:dict()` | Legacy dict module |
| `Set<'T>` | `sets:set()` | Unordered set |
| `Set<'T>` | `ordsets:ordset()` | Ordered set (list-based) |
| `'a * 'b` (tuple) | `{A, B}` | Tuple literal |
| `'a * 'b * 'c` | `{A, B, C}` | N-tuple |

### Record and Union Types

| F# | Erlang | Notes |
|------------|------|-------|
| `type Person = { Name: string; Age: int }` | `-record(person, {name :: binary(), age :: integer()}).` | Record definition |
| `{ Name = "Alice"; Age = 30 }` | `#person{name = <<"Alice">>, age = 30}` | Record creation |
| `person.Name` | `Person#person.name` | Field access |
| `{ person with Age = 31 }` | `Person#person{age = 31}` | Record update |
| `type Shape = Circle of float \| Rectangle of float * float` | Tagged tuples | `{circle, Radius}` or `{rectangle, Width, Height}` |
| Discriminated union | Pattern matching on tuple tag | Match first element as discriminator |

### Function Types

| F# | Erlang | Notes |
|------------|------|-------|
| `'a -> 'b` | `fun((A) -> B)` | Anonymous function |
| `'a -> 'b -> 'c` | `fun((A, B) -> C)` | Multi-param (uncurried) |
| Curried function | Nested funs | `fun(A) -> fun(B) -> C end end` (uncommon) |
| `Func<'a,'b>` | `fun((A) -> B)` | Function type |
| `Action<'a>` | `fun((A) -> ok)` | Side-effect function |

### Generic Types

| F# | Erlang | Notes |
|------------|------|-------|
| `'a` | `term()` | Any type (runtime polymorphism) |
| `'a list` | `list(A)` | Parameterized type spec |
| `'a option` | `{ok, A} \| error` | Type spec pattern |
| Type constraint | Guard clause | `when is_integer(X)` in function clause |

---

## Idiom Translation

### Pattern 1: Option Handling

**F#:**
```fsharp
let findUser (id: string) : User option =
    users |> List.tryFind (fun u -> u.Id = id)

let name =
    findUser "123"
    |> Option.map (fun u -> u.Name)
    |> Option.defaultValue "Unknown"
```

**Erlang:**
```erlang
-spec find_user(binary()) -> {ok, user()} | error.
find_user(Id) ->
    case lists:search(fun(U) -> maps:get(id, U) =:= Id end, users()) of
        {value, User} -> {ok, User};
        false -> error
    end.

get_name(UserId) ->
    case find_user(UserId) of
        {ok, User} -> maps:get(name, User);
        error -> <<"Unknown">>
    end.
```

**Why this translation:**
- F#'s `Option.map` becomes pattern matching in Erlang
- `Option.defaultValue` becomes the error clause in case expression
- Erlang uses `{ok, Value}` | `error` tuples instead of `Some`/`None`
- Type specs replace F# type annotations

### Pattern 2: Result-Based Error Handling

**F#:**
```fsharp
type Error = DivisionByZero | InvalidInput of string

let divide (x: float) (y: float) : Result<float, Error> =
    if y = 0.0 then Error DivisionByZero
    else Ok (x / y)

let calculate = result {
    let! a = divide 10.0 2.0
    let! b = divide 20.0 4.0
    let! c = divide a b
    return c
}
```

**Erlang:**
```erlang
-type error_reason() :: division_by_zero | {invalid_input, binary()}.

-spec divide(float(), float()) -> {ok, float()} | {error, error_reason()}.
divide(_X, 0.0) ->
    {error, division_by_zero};
divide(X, Y) ->
    {ok, X / Y}.

-spec calculate() -> {ok, float()} | {error, error_reason()}.
calculate() ->
    case divide(10.0, 2.0) of
        {ok, A} ->
            case divide(20.0, 4.0) of
                {ok, B} ->
                    divide(A, B);
                {error, Reason} -> {error, Reason}
            end;
        {error, Reason} -> {error, Reason}
    end.
```

**Why this translation:**
- F# computation expressions become nested case statements
- `Result<'T,'E>` maps to `{ok, Value} | {error, Reason}` tuples
- F# discriminated unions become atoms or tagged tuples
- Pattern matching on error tuples replaces monadic bind

### Pattern 3: List Processing

**F#:**
```fsharp
let result =
    items
    |> List.filter (fun x -> x.Active)
    |> List.map (fun x -> x.Value)
    |> List.sum
```

**Erlang:**
```erlang
calculate_result(Items) ->
    lists:foldl(
        fun(X, Acc) -> Acc + X end,
        0,
        [maps:get(value, X) || X <- Items, maps:get(active, X)]
    ).

% Alternative: using lists module functions
calculate_result_alt(Items) ->
    Active = lists:filter(fun(X) -> maps:get(active, X) end, Items),
    Values = lists:map(fun(X) -> maps:get(value, X) end, Active),
    lists:sum(Values).
```

**Why this translation:**
- F# pipe operator becomes list comprehension or nested function calls
- List comprehension is more idiomatic for filter+map in Erlang
- `lists:sum/1` directly replaces `List.sum`
- Both approaches are valid; comprehension is more concise

### Pattern 4: Record Pattern Matching

**F#:**
```fsharp
type Person = { FirstName: string; LastName: string; Age: int }

let getFullName person =
    match person with
    | { FirstName = f; LastName = l } -> $"{f} {l}"

let isAdult = function
    | { Age = age } when age >= 18 -> true
    | _ -> false
```

**Erlang:**
```erlang
-record(person, {
    first_name :: binary(),
    last_name :: binary(),
    age :: integer()
}).

get_full_name(#person{first_name = F, last_name = L}) ->
    <<F/binary, " ", L/binary>>.

is_adult(#person{age = Age}) when Age >= 18 ->
    true;
is_adult(_) ->
    false.
```

**Why this translation:**
- F# record patterns map to Erlang record patterns
- Guards (`when`) work similarly in both languages
- F# string interpolation becomes binary concatenation
- Function clauses with pattern matching replace match expressions

---

## Paradigm Translation

### Mental Model Shift: .NET Functional → BEAM/OTP

| F# Concept | Erlang/OTP Approach | Key Insight |
|------------------|-------------------|-------------|
| Computation expression | gen_server / process loop | Stateful workflow → process with message loop |
| async/Task | spawn / gen_server | Async operation → lightweight process |
| MailboxProcessor | gen_server | Agent pattern → OTP behavior |
| Mutable state | Process state / ETS | Mutation → process-local state or shared ETS table |
| Exception | Let-it-crash + supervisor | Try/catch → supervision tree restart |
| Type provider | Parse transform / macro | Compile-time metaprogramming |
| Assembly/Module | Application / OTP app | .NET assembly → OTP application |

### Concurrency Mental Model

| F# Pattern | Erlang/OTP Pattern | Conceptual Translation |
|----------------|----------------|------------------------|
| `async { }` | `spawn(fun() -> ... end)` | Async block → process spawn |
| `Async.Parallel` | Multiple spawn + receive | Parallel tasks → concurrent processes |
| `Async.RunSynchronously` | Synchronous call or receive | Block until result |
| `Task.Run` | `spawn/1` | Fire-and-forget task → process |
| `MailboxProcessor` | `gen_server` | Stateful agent → OTP gen_server |
| `MailboxProcessor.Post` | `gen_server:cast/2` | Async message → cast |
| `MailboxProcessor.PostAndReply` | `gen_server:call/2` | Sync request → call |

---

## Error Handling

### F# Error Model → Erlang Error Model

**F# Approach: Railway-Oriented Programming**

```fsharp
type Result<'T, 'E> = Ok of 'T | Error of 'E

let validateAge age =
    if age >= 0 && age <= 120 then Ok age
    else Error "Invalid age"

let createUser name age = result {
    let! validAge = validateAge age
    return { Name = name; Age = validAge }
}
```

**Erlang Approach: Let-It-Crash + Tagged Tuples**

```erlang
% Defensive: return error tuple
-spec validate_age(integer()) -> {ok, integer()} | {error, binary()}.
validate_age(Age) when Age >= 0, Age =< 120 ->
    {ok, Age};
validate_age(_) ->
    {error, <<"Invalid age">>}.

% Let-it-crash: use pattern matching and let supervisor handle failure
-spec create_user(binary(), integer()) -> user().
create_user(Name, Age) when Age >= 0, Age =< 120 ->
    #{name => Name, age => Age}.
    % Invalid age will cause function clause error, caught by supervisor
```

**Key Differences:**

1. **F# uses Result types everywhere** - Explicit error handling in types
2. **Erlang uses let-it-crash** - Supervisors restart failed processes
3. **When to use {ok, _} vs crash**:
   - Use `{ok, Value} | {error, Reason}` for expected errors (user input, network)
   - Use pattern matching + crash for programming errors (invalid state)

### Exception Translation

| F# | Erlang | Strategy |
|------------|------|----------|
| `try...with` | `try...catch` | Rare; prefer `{error, Reason}` tuples |
| `raise` / `failwith` | `error(Reason)` / `exit(Reason)` | Crash the process |
| `try...finally` | `try...after` | Resource cleanup |
| Result type | `{ok, _} \| {error, _}` | Expected errors |
| Option type | `{ok, _} \| error \| undefined` | Absence of value |

**F#:**
```fsharp
try
    let result = riskyOperation()
    result
with
| :? IOException as ex -> Error $"IO error: {ex.Message}"
| ex -> Error $"Unexpected: {ex.Message}"
```

**Erlang:**
```erlang
% Approach 1: Catch and return error tuple
safe_risky_operation() ->
    try risky_operation() of
        Result -> {ok, Result}
    catch
        error:Reason -> {error, {operation_failed, Reason}};
        exit:Reason -> {error, {process_exited, Reason}}
    end.

% Approach 2: Let it crash and supervisor restarts
risky_operation() ->
    % Just do the operation; supervisor will restart on failure
    perform_io(),
    {ok, result}.
```

---

## Concurrency Patterns

### F# Async → Erlang Process

**F# async computation:**
```fsharp
let fetchData url = async {
    printfn $"Fetching {url}..."
    do! Async.Sleep 1000
    return $"Data from {url}"
}

let processUrls urls = async {
    let! results =
        urls
        |> List.map fetchData
        |> Async.Parallel
    return results |> Array.toList
}
```

**Erlang process-based:**
```erlang
fetch_data(Url) ->
    io:format("Fetching ~s...~n", [Url]),
    timer:sleep(1000),
    {ok, iolist_to_binary(["Data from ", Url])}.

process_urls(Urls) ->
    Self = self(),
    % Spawn a process for each URL
    Pids = [spawn(fun() ->
        Result = fetch_data(Url),
        Self ! {result, Url, Result}
    end) || Url <- Urls],

    % Collect results
    collect_results(length(Pids), []).

collect_results(0, Acc) ->
    {ok, lists:reverse(Acc)};
collect_results(N, Acc) ->
    receive
        {result, _Url, Result} ->
            collect_results(N - 1, [Result | Acc])
    after 5000 ->
        {error, timeout}
    end.
```

**Why this translation:**
- F# async blocks map to spawned Erlang processes
- `Async.Parallel` becomes multiple spawn + receive pattern
- Each async operation is a lightweight process
- Results collected via message passing

### MailboxProcessor → gen_server

**F# MailboxProcessor:**
```fsharp
type CounterMsg =
    | Increment
    | GetCount of AsyncReplyChannel<int>

let counter = MailboxProcessor.Start(fun inbox ->
    let rec loop count = async {
        let! msg = inbox.Receive()
        match msg with
        | Increment -> return! loop (count + 1)
        | GetCount channel ->
            channel.Reply count
            return! loop count
    }
    loop 0
)

counter.Post Increment
let count = counter.PostAndReply GetCount
```

**Erlang gen_server:**
```erlang
-module(counter_server).
-behaviour(gen_server).

-export([start_link/0, increment/0, get_count/0]).
-export([init/1, handle_call/3, handle_cast/2, terminate/2, code_change/3]).

start_link() ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [], []).

increment() ->
    gen_server:cast(?MODULE, increment).

get_count() ->
    gen_server:call(?MODULE, get_count).

init([]) ->
    {ok, 0}.  % Initial state

handle_call(get_count, _From, Count) ->
    {reply, Count, Count}.

handle_cast(increment, Count) ->
    {noreply, Count + 1}.

terminate(_Reason, _State) ->
    ok.

code_change(_OldVsn, State, _Extra) ->
    {ok, State}.
```

**Why this translation:**
- F# `MailboxProcessor.Post` → `gen_server:cast` (async)
- F# `PostAndReply` → `gen_server:call` (sync)
- F# discriminated union messages → Erlang atoms/tuples
- gen_server provides supervision, hot code reload, debugging

### Computation Expression → gen_statem

**F# stateful computation:**
```fsharp
type DoorState = Locked | Unlocked
type DoorEvent = Lock | Unlock | Open

let door = MailboxProcessor.Start(fun inbox ->
    let rec locked() = async {
        let! event = inbox.Receive()
        match event with
        | Unlock -> return! unlocked()
        | _ -> return! locked()
    }
    and unlocked() = async {
        let! event = inbox.Receive()
        match event with
        | Lock -> return! locked()
        | Open ->
            printfn "Door opened"
            return! unlocked()
        | _ -> return! unlocked()
    }
    locked()
)
```

**Erlang gen_statem:**
```erlang
-module(door_fsm).
-behaviour(gen_statem).

-export([start_link/0, lock/0, unlock/0, open/0]).
-export([init/1, callback_mode/0, locked/3, unlocked/3, terminate/3]).

start_link() ->
    gen_statem:start_link({local, ?MODULE}, ?MODULE, [], []).

lock() -> gen_statem:cast(?MODULE, lock).
unlock() -> gen_statem:cast(?MODULE, unlock).
open() -> gen_statem:cast(?MODULE, open).

init([]) ->
    {ok, locked, #{}}.

callback_mode() ->
    state_functions.

locked(cast, unlock, Data) ->
    {next_state, unlocked, Data};
locked(cast, _, Data) ->
    {keep_state, Data}.

unlocked(cast, lock, Data) ->
    {next_state, locked, Data};
unlocked(cast, open, Data) ->
    io:format("Door opened~n"),
    {keep_state, Data};
unlocked(cast, _, Data) ->
    {keep_state, Data}.

terminate(_Reason, _State, _Data) ->
    ok.
```

**Why this translation:**
- F# recursive state functions → gen_statem state functions
- State transitions explicit in both
- gen_statem adds supervision, introspection, and hot code reload
- Erlang state machines are first-class OTP pattern

---

## Memory & Platform Differences

### .NET CLR → BEAM VM

| Aspect | F# (.NET/CLR) | Erlang (BEAM) | Migration Strategy |
|--------|---------------|---------------|-------------------|
| Memory model | Garbage collected, shared heap | Process-isolated heaps | Data copying between processes |
| Concurrency | Thread pool, shared memory | Lightweight processes, message passing | Replace threads with processes |
| Mutability | Immutable by default, mutable allowed | Immutable only | Remove mutable state or use ETS |
| Type system | Static, compile-time | Dynamic, runtime + Dialyzer | Use type specs, rely on Dialyzer |
| Distribution | Remote .NET Remoting (rare) | Built-in distributed Erlang | Use distributed Erlang primitives |
| Hot code reload | AppDomain reload (heavy) | Module reload (lightweight) | Leverage OTP code_change callbacks |

### Shared State Translation

**F# mutable state:**
```fsharp
let mutable counter = 0

let increment() =
    counter <- counter + 1
    counter
```

**Erlang alternatives:**

```erlang
% Option 1: Process-local state (gen_server)
-module(counter).
-behaviour(gen_server).
% ... (see gen_server example above)

% Option 2: ETS table (shared, concurrent)
-module(counter_ets).

init() ->
    ets:new(counter, [named_table, public, set]),
    ets:insert(counter, {value, 0}).

increment() ->
    ets:update_counter(counter, value, 1).

get_value() ->
    [{value, V}] = ets:lookup(counter, value),
    V.
```

**When to use each:**
- **gen_server**: Sequential access, state changes are ordered
- **ETS**: Concurrent reads/writes, higher throughput
- **Process dictionary**: Rarely (per-process global variables)

---

## Common Pitfalls

1. **Trying to share state between processes**
   - F# allows shared mutable state via `mutable` or `ref`
   - Erlang processes are isolated; use message passing or ETS
   - **Solution**: Send data via messages or use gen_server for coordination

2. **Expecting static type safety**
   - F# has compile-time type checking
   - Erlang is dynamically typed; Dialyzer provides static analysis but doesn't prevent runtime errors
   - **Solution**: Use type specs (`-spec`), rely on pattern matching and guards, run Dialyzer

3. **Over-using try/catch**
   - F# uses exceptions for control flow
   - Erlang prefers let-it-crash with supervisors
   - **Solution**: Use `{ok, Value} | {error, Reason}` for expected errors, let supervisors handle crashes

4. **Direct port of OOP patterns**
   - F# can interop with C# classes and objects
   - Erlang has no objects; use records, maps, and processes
   - **Solution**: Model objects as records/maps for data, processes for stateful entities

5. **Ignoring process lifecycles**
   - F# Tasks clean up automatically
   - Erlang processes must be explicitly linked/monitored
   - **Solution**: Use supervision trees, link processes, handle EXIT messages

6. **String type mismatch**
   - F# string is always UTF-16
   - Erlang has binaries (UTF-8) and lists (codepoints)
   - **Solution**: Prefer binaries (`<<"Hello">>`) for strings, use `unicode` module for conversions

7. **Expecting LINQ-style laziness**
   - F# `seq<'T>` is lazy
   - Erlang lists are strict; laziness requires process-based streams
   - **Solution**: Use list comprehensions for small data, gen_server or gen_stage for large streams

8. **Missing supervision**
   - F# async errors propagate to caller
   - Erlang crashes should be handled by supervisors
   - **Solution**: Always wrap gen_servers in a supervision tree

---

## Tooling

| Tool | Purpose | Notes |
|------|---------|-------|
| **rebar3** | Build tool and package manager | Equivalent to dotnet CLI |
| **Dialyzer** | Static analysis tool | Type checking via success typing |
| **Erlang shell** | REPL | Interactive testing (like F# Interactive) |
| **Observer** | GUI for process inspection | No direct F# equivalent |
| **recon** | Production debugging | Runtime introspection library |
| **PropEr** | Property-based testing | Similar to FsCheck |
| **Common Test** | Testing framework | Similar to xUnit/NUnit |
| **EUnit** | Unit testing | Simpler than Common Test |
| **erlang.mk** | Alternative build tool | Makefile-based (alternative to rebar3) |
| **relx** | Release management | Bundled with rebar3 |

---

## Build System Migration

### .NET Project → OTP Application

**F# project (.fsproj):**
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>
  <ItemGroup>
    <Compile Include="Types.fs" />
    <Compile Include="Logic.fs" />
    <Compile Include="Program.fs" />
  </ItemGroup>
  <ItemGroup>
    <PackageReference Include="FSharp.Core" Version="8.0.0" />
  </ItemGroup>
</Project>
```

**Erlang rebar3 (rebar.config):**
```erlang
{erl_opts, [debug_info]}.

{deps, [
    % Dependencies from hex.pm
]}.

{relx, [
    {release, {myapp, "0.1.0"},
     [myapp, sasl]},
    {dev_mode, true},
    {include_erts, false}
]}.
```

**Application resource file (src/myapp.app.src):**
```erlang
{application, myapp,
 [{description, "My OTP application"},
  {vsn, "0.1.0"},
  {registered, []},
  {mod, {myapp_app, []}},
  {applications, [kernel, stdlib]},
  {env, []},
  {modules, []},
  {licenses, ["Apache-2.0"]},
  {links, []}
 ]}.
```

**Migration mapping:**
- `.fsproj` → `rebar.config` + `.app.src`
- NuGet packages → hex.pm dependencies
- Assembly entry point → OTP application module
- Build output → `_build/` directory

---

## Examples

### Example 1: Simple - Type and Function Translation

**Before (F#):**
```fsharp
type Point = { X: float; Y: float }

let distance (p1: Point) (p2: Point) : float =
    let dx = p2.X - p1.X
    let dy = p2.Y - p1.Y
    sqrt (dx * dx + dy * dy)

let origin = { X = 0.0; Y = 0.0 }
let point = { X = 3.0; Y = 4.0 }
let dist = distance origin point  // 5.0
```

**After (Erlang):**
```erlang
-module(geometry).
-export([distance/2]).

-record(point, {x :: float(), y :: float()}).

-spec distance(#point{}, #point{}) -> float().
distance(#point{x = X1, y = Y1}, #point{x = X2, y = Y2}) ->
    Dx = X2 - X1,
    Dy = Y2 - Y1,
    math:sqrt(Dx * Dx + Dy * Dy).

% Usage
origin() -> #point{x = 0.0, y = 0.0}.
example() ->
    Origin = origin(),
    Point = #point{x = 3.0, y = 4.0},
    Dist = distance(Origin, Point),  % 5.0
    Dist.
```

### Example 2: Medium - Option and Result Handling

**Before (F#):**
```fsharp
type User = { Id: string; Name: string; Email: string }
type UserError = NotFound | InvalidEmail of string

let validateEmail (email: string) : Result<string, UserError> =
    if email.Contains("@") then Ok email
    else Error (InvalidEmail email)

let findUserById (id: string) : User option =
    // Simulate database lookup
    if id = "123" then Some { Id = id; Name = "Alice"; Email = "alice@example.com" }
    else None

let getUserEmail (id: string) : Result<string, UserError> =
    match findUserById id with
    | Some user ->
        validateEmail user.Email
    | None ->
        Error NotFound
```

**After (Erlang):**
```erlang
-module(user_service).
-export([get_user_email/1]).

-type user() :: #{
    id := binary(),
    name := binary(),
    email := binary()
}.

-type user_error() :: not_found | {invalid_email, binary()}.

-spec validate_email(binary()) -> {ok, binary()} | {error, user_error()}.
validate_email(Email) ->
    case binary:match(Email, <<"@">>) of
        nomatch -> {error, {invalid_email, Email}};
        _ -> {ok, Email}
    end.

-spec find_user_by_id(binary()) -> {ok, user()} | error.
find_user_by_id(<<"123">>) ->
    {ok, #{
        id => <<"123">>,
        name => <<"Alice">>,
        email => <<"alice@example.com">>
    }};
find_user_by_id(_) ->
    error.

-spec get_user_email(binary()) -> {ok, binary()} | {error, user_error()}.
get_user_email(Id) ->
    case find_user_by_id(Id) of
        {ok, User} ->
            Email = maps:get(email, User),
            validate_email(Email);
        error ->
            {error, not_found}
    end.
```

### Example 3: Complex - Async Workflow to gen_server

**Before (F#):**
```fsharp
type Message =
    | Fetch of url: string
    | Process of data: string
    | GetResults of AsyncReplyChannel<string list>

type WorkerState = {
    Results: string list
}

let worker = MailboxProcessor.Start(fun inbox ->
    let rec loop state = async {
        let! msg = inbox.Receive()
        match msg with
        | Fetch url ->
            let! data = async {
                do! Async.Sleep 100  // Simulate network delay
                return $"Data from {url}"
            }
            inbox.Post (Process data)
            return! loop state

        | Process data ->
            let processed = data.ToUpper()
            let newState = { Results = processed :: state.Results }
            return! loop newState

        | GetResults channel ->
            channel.Reply (List.rev state.Results)
            return! loop state
    }
    loop { Results = [] }
)

// Usage
worker.Post (Fetch "http://example.com")
worker.Post (Fetch "http://test.com")
let results = worker.PostAndReply GetResults
```

**After (Erlang):**
```erlang
-module(worker_server).
-behaviour(gen_server).

-export([start_link/0, fetch/1, get_results/0]).
-export([init/1, handle_call/3, handle_cast/2, handle_info/2, terminate/2, code_change/3]).

-record(state, {
    results = [] :: [binary()]
}).

%%% API

start_link() ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [], []).

-spec fetch(binary()) -> ok.
fetch(Url) ->
    gen_server:cast(?MODULE, {fetch, Url}).

-spec get_results() -> {ok, [binary()]}.
get_results() ->
    gen_server:call(?MODULE, get_results).

%%% Callbacks

init([]) ->
    {ok, #state{}}.

handle_call(get_results, _From, State) ->
    Results = lists:reverse(State#state.results),
    {reply, {ok, Results}, State}.

handle_cast({fetch, Url}, State) ->
    % Spawn async fetch process
    Self = self(),
    spawn(fun() ->
        timer:sleep(100),  % Simulate network delay
        Data = iolist_to_binary(["Data from ", Url]),
        gen_server:cast(Self, {process, Data})
    end),
    {noreply, State};

handle_cast({process, Data}, State) ->
    Processed = string:uppercase(Data),
    NewResults = [Processed | State#state.results],
    {noreply, State#state{results = NewResults}}.

handle_info(_Info, State) ->
    {noreply, State}.

terminate(_Reason, _State) ->
    ok.

code_change(_OldVsn, State, _Extra) ->
    {ok, State}.

%%% Usage
% worker_server:start_link().
% worker_server:fetch(<<"http://example.com">>).
% worker_server:fetch(<<"http://test.com">>).
% {ok, Results} = worker_server:get_results().
```

**Translation notes:**
- F# `MailboxProcessor` → Erlang `gen_server`
- F# discriminated union messages → Erlang tuples
- F# `PostAndReply` → `gen_server:call`
- F# `Post` → `gen_server:cast`
- F# `async { }` for network call → `spawn` for concurrent task
- State management identical in concept

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `lang-fsharp-dev` - F# development patterns
- `lang-erlang-dev` - Erlang development patterns
- `convert-elixir-fsharp` - Reverse direction (Elixir is related to Erlang)

Cross-cutting pattern skills (for areas not fully covered by lang-*-dev):
- `patterns-concurrency-dev` - Async, actors, processes across languages
- `patterns-serialization-dev` - JSON, validation, encoding across languages
