# Erlang

> Concurrent, functional language designed for building massively scalable, fault-tolerant distributed systems.

## Overview

Erlang is a concurrent, functional programming language developed at Ericsson in the 1980s by Joe Armstrong, Robert Virding, and Mike Williams. It was designed for building telephone switches but evolved into a general-purpose language for any system requiring high availability, fault tolerance, and soft real-time performance.

The language runs on the BEAM virtual machine and implements the actor model through lightweight processes that communicate via message passing. Its "let it crash" philosophy and supervision trees enable systems that can achieve "nine nines" (99.9999999%) availability.

Erlang powers critical infrastructure at WhatsApp, Discord, RabbitMQ, and telecommunications systems worldwide. Its OTP (Open Telecom Platform) library provides battle-tested patterns for building reliable distributed systems.

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | BEAM | Actor model, distributed |
| Secondary Family | FP | Functional, pattern matching |
| Subtype | otp | OTP patterns foundational |

See: [BEAM Family](../language-families/beam.md)

## Version History

| Version | Release | Key Changes for Conversion |
|---------|---------|---------------------------|
| R14 | 2010 | Modern baseline |
| 17.0 | 2014-04 | Maps introduced |
| 20.0 | 2017-06 | Dirty schedulers |
| 23.0 | 2020-05 | Logger module |
| 25.0 | 2022-05 | Selectable features |
| 26.0 | 2023-05 | Maybe expressions |

## Feature Profile

### Type System

- **Strength:** dynamic (runtime typing)
- **Inference:** none (optional specs for Dialyzer)
- **Generics:** runtime (pattern matching, duck typing)
- **Nullability:** explicit (atoms like undefined, error tuples)

### Memory Model

- **Management:** gc (per-process, generational)
- **Mutability:** immutable (all data immutable, single-assignment)
- **Allocation:** per-process heap
- **Process isolation:** complete (share-nothing)

### Control Flow

- **Structured:** if, case, receive, try-catch
- **Effects:** tagged tuples ({ok, Value}, {error, Reason})
- **Async:** processes, spawn, message passing

### Data Types

- **Primitives:** integers (arbitrary precision), floats, atoms
- **Composites:** tuples, lists, maps, records, binaries
- **Collections:** lists, maps, sets (via library)
- **Abstraction:** modules, behaviours

### Metaprogramming

- **Macros:** preprocessor-style (parse transforms for advanced)
- **Reflection:** runtime (erlang module introspection)
- **Code generation:** hot code reloading

## Ecosystem

| Tool | Name | Notes |
|------|------|-------|
| Package Manager | Hex, rebar3 | Hex for packages |
| Build System | rebar3, erlang.mk | rebar3 standard |
| LSP | erlang_ls | Good support |
| Formatter | erlfmt | Official formatter |
| Linter | elvis | Style checker |
| REPL | erl | Built-in shell |
| Test Framework | EUnit, Common Test | Built-in |

## Syntax Patterns

```erlang
%% Module declaration
-module(greeter).
-export([greet/2]).

%% Function definition with guards
greet(Name, Times) when is_binary(Name), is_integer(Times), Times > 0 ->
    binary:copy(<<"Hello, ", Name/binary, "! ">>, Times).

%% Pattern matching in function clauses
process({ok, Value}) -> {success, Value};
process({error, Reason}) -> {failure, Reason};
process(_) -> {failure, unknown}.

%% Anonymous function (fun)
Greet = fun(Name) -> <<"Hello, ", Name/binary, "!">> end.

%% Record definition
-record(user, {id, name, email = undefined}).

%% Creating and updating records
create_user(Id, Name) ->
    #user{id = Id, name = Name}.

set_email(User, Email) ->
    User#user{email = Email}.

%% Pattern matching with case
area(Shape) ->
    case Shape of
        {circle, Radius} -> math:pi() * Radius * Radius;
        {rectangle, Width, Height} -> Width * Height;
        _ -> {error, unknown_shape}
    end.

%% List comprehension
Squares = [X * X || X <- lists:seq(1, 10), X rem 2 == 0].

%% Binary pattern matching
parse_packet(<<Length:32, Payload:Length/binary, Rest/binary>>) ->
    {ok, Payload, Rest};
parse_packet(_) ->
    {error, incomplete}.

%% GenServer behaviour
-behaviour(gen_server).

-export([start_link/1, increment/1, get_value/1]).
-export([init/1, handle_call/3, handle_cast/2]).

start_link(Initial) ->
    gen_server:start_link(?MODULE, Initial, []).

increment(Pid) ->
    gen_server:cast(Pid, increment).

get_value(Pid) ->
    gen_server:call(Pid, get_value).

init(Initial) ->
    {ok, Initial}.

handle_cast(increment, Count) ->
    {noreply, Count + 1}.

handle_call(get_value, _From, Count) ->
    {reply, Count, Count}.

%% Process spawning
start_worker() ->
    spawn(fun() -> worker_loop() end).

worker_loop() ->
    receive
        {work, Task} ->
            Result = do_work(Task),
            worker_loop();
        stop ->
            ok
    end.

%% Supervisor
-behaviour(supervisor).

-export([start_link/0, init/1]).

start_link() ->
    supervisor:start_link({local, ?MODULE}, ?MODULE, []).

init([]) ->
    SupFlags = #{
        strategy => one_for_one,
        intensity => 5,
        period => 10
    },
    Children = [
        #{id => worker,
          start => {my_worker, start_link, []},
          restart => permanent,
          type => worker}
    ],
    {ok, {SupFlags, Children}}.

%% Error handling with try-catch
safe_divide(A, B) ->
    try
        A / B
    catch
        error:badarith -> {error, division_by_zero}
    end.

%% Receive with timeout
wait_for_message(Timeout) ->
    receive
        {message, Data} -> {ok, Data}
    after
        Timeout -> {error, timeout}
    end.
```

## Semantic Gaps

| Gap | Severity | Workaround |
|-----|----------|------------|
| No static types | moderate | Use Dialyzer, specs |
| Syntax can be terse/unusual | moderate | Learn idioms, use Elixir for friendlier syntax |
| Records are compile-time only | minor | Use maps for dynamic structures |
| No standard package manager history | minor | Use Hex (now standard) |
| Prolog-inspired syntax unfamiliar | moderate | Reference documentation, practice |

## Convert-* Coverage

| Direction | Count | Skills |
|-----------|-------|--------|
| As Source | 4 | erlang-fsharp, erlang-haskell, erlang-roc, erlang-scala |
| As Target | 4 | python-erlang, clojure-erlang, elixir-erlang, elm-erlang |

**Note:** OTP patterns (GenServer, Supervisor) are central to conversions.

## Idiomatic Patterns

### Tagged Tuples → Result/Either

```erlang
%% Erlang: tagged tuple
{ok, Value}
{error, Reason}

%% IR equivalent: Result type
%% Ok(value) | Err(reason)
```

### Behaviours → Interfaces/Traits

```erlang
%% Erlang: behaviour
-behaviour(gen_server).
-callback init(Args) -> {ok, State}.

%% IR equivalent: trait/interface
%% trait GenServer { fn init(args: Args) -> State }
```

### Receive → Actor Mailbox

```erlang
%% Erlang: receive
receive
    {msg, Data} -> handle(Data)
after 5000 ->
    timeout
end.

%% IR equivalent: actor receive with timeout
%% select! { msg = recv() => handle(msg), timeout(5s) => timeout }
```

### Process + Supervisor → Actor + Supervision

```erlang
%% Erlang: supervision tree
supervisor:start_child(Sup, ChildSpec).

%% IR equivalent: supervised actor spawn
%% supervisor.spawn_child(worker_actor)
```

## Related Languages

- **Influenced by:** Prolog, Smalltalk, ML
- **Influenced:** Elixir, Gleam, Akka (Scala), Go (goroutines)
- **Compiles to:** BEAM bytecode
- **FFI compatible:** C (NIFs, ports)

## Sources

- [Erlang Documentation](https://www.erlang.org/doc/)
- [OTP Design Principles](https://www.erlang.org/doc/design_principles/)
- [Learn You Some Erlang](https://learnyousomeerlang.com/)
- [Hex Package Manager](https://hex.pm/)

## See Also

- [BEAM Family](../language-families/beam.md)
- [Elixir](elixir.md) - Modern BEAM language
- [Gleam](gleam.md) - Typed BEAM language
- [OTP Documentation](https://www.erlang.org/doc/design_principles/)
