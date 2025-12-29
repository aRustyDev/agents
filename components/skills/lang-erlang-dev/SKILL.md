---
name: lang-erlang-dev
description: Foundational Erlang patterns covering OTP behaviors, fault-tolerant systems, distributed computing, pattern matching, processes, and supervision trees. Use when writing Erlang code, building concurrent systems, working with OTP frameworks, or developing distributed fault-tolerant applications. This is the entry point for Erlang development.
---

# Erlang Fundamentals

Foundational Erlang patterns and core language features for building fault-tolerant, distributed systems. This skill serves as both a reference for common patterns and an index to specialized Erlang skills.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   Erlang Skill Hierarchy                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                  ┌─────────────────────┐                        │
│                  │  lang-erlang-dev    │ ◄── You are here       │
│                  │   (foundation)      │                        │
│                  └──────────┬──────────┘                        │
│                             │                                   │
│            ┌────────────────┼────────────────┐                  │
│            │                │                │                  │
│            ▼                ▼                ▼                  │
│    ┌──────────────┐  ┌──────────┐   ┌──────────────┐          │
│    │   erlang     │  │   otp    │   │ distributed  │          │
│    │  patterns    │  │behaviors │   │   systems    │          │
│    └──────────────┘  └──────────┘   └──────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**This skill covers:**
- Pattern matching and guards
- Processes and message passing
- OTP behaviors (gen_server, gen_statem, supervisor)
- Supervision trees and fault tolerance
- Error handling (let it crash philosophy)
- Erlang Term Storage (ETS)
- Distributed Erlang basics
- BEAM VM fundamentals
- Common Erlang idioms

**This skill does NOT cover (see specialized skills):**
- Advanced OTP patterns → `lang-erlang-patterns-dev`
- Release management and deployment → `lang-erlang-release-dev`
- Performance optimization → `lang-erlang-performance-dev`
- Web frameworks (Cowboy, Phoenix) → framework-specific skills
- Database drivers and ORM → `lang-erlang-database-dev`

---

## Quick Reference

| Task | Syntax |
|------|--------|
| Define module | `-module(module_name).` |
| Export function | `-export([function_name/arity]).` |
| Define function | `function_name(Args) -> Body.` |
| Pattern match | `{ok, Value} = Result` |
| Spawn process | `spawn(Module, Function, Args)` |
| Send message | `Pid ! Message` |
| Receive message | `receive Pattern -> Body end` |
| List comprehension | `[X*2 \|\| X <- List]` |
| Anonymous function | `fun(X) -> X * 2 end` |
| Guard clause | `when is_integer(X)` |

---

## Skill Routing

Use this table to find the right specialized skill:

| When you need to... | Use this skill |
|---------------------|----------------|
| Implement advanced OTP patterns | `lang-erlang-patterns-dev` |
| Build releases with rebar3 | `lang-erlang-release-dev` |
| Optimize performance and profiling | `lang-erlang-performance-dev` |
| Work with Cowboy web server | `web-cowboy-dev` |
| Implement database access | `lang-erlang-database-dev` |

---

## Pattern Matching

### Basic Patterns

```erlang
% Variable binding
X = 42.
{ok, Value} = {ok, 100}.

% List patterns
[Head | Tail] = [1, 2, 3, 4].  % Head = 1, Tail = [2, 3, 4]
[First, Second | Rest] = [a, b, c, d].

% Tuple patterns
{Name, Age, Email} = {"Alice", 30, "alice@example.com"}.

% Map patterns (Erlang 17+)
#{name := Name, age := Age} = #{name => "Bob", age => 25}.

% Binary patterns
<<A:8, B:8, Rest/binary>> = <<1, 2, 3, 4, 5>>.
```

### Function Clauses

```erlang
% Multiple clauses with pattern matching
factorial(0) -> 1;
factorial(N) when N > 0 -> N * factorial(N - 1).

% Pattern matching in function heads
process_result({ok, Data}) ->
    {success, Data};
process_result({error, Reason}) ->
    {failure, Reason};
process_result(unknown) ->
    {failure, unknown_result}.

% List processing
sum([]) -> 0;
sum([H|T]) -> H + sum(T).

length_of([]) -> 0;
length_of([_|T]) -> 1 + length_of(T).
```

### Guards

```erlang
% Type guards
is_valid_age(Age) when is_integer(Age), Age >= 0, Age =< 150 -> true;
is_valid_age(_) -> false.

% Comparison guards
max(X, Y) when X > Y -> X;
max(_, Y) -> Y.

% Multiple guards
process(X, Y) when is_number(X); is_number(Y) ->
    X + Y;
process(X, Y) ->
    {error, not_numbers}.

% Built-in guard BIFs
is_valid(Value) when is_atom(Value) -> atom;
is_valid(Value) when is_list(Value) -> list;
is_valid(Value) when is_tuple(Value) -> tuple;
is_valid(Value) when is_map(Value) -> map;
is_valid(_) -> unknown.
```

---

## Processes and Concurrency

### Spawning Processes

```erlang
% Basic spawn
Pid = spawn(fun() -> loop() end).

% Spawn with module/function/args
Pid = spawn(my_module, my_function, [Arg1, Arg2]).

% Spawn and link (dies together)
Pid = spawn_link(fun() -> worker() end).

% Spawn and monitor
{Pid, Ref} = spawn_monitor(fun() -> task() end).
```

### Message Passing

```erlang
% Send message
Pid ! {self(), hello, "World"}.

% Receive messages
receive
    {From, hello, Msg} ->
        From ! {self(), reply, "Hello " ++ Msg};
    {quit} ->
        ok;
    Other ->
        io:format("Unexpected: ~p~n", [Other])
after 5000 ->
    timeout
end.

% Selective receive
receive
    {Priority, high, Msg} ->
        handle_urgent(Msg);
    {Priority, normal, Msg} ->
        handle_normal(Msg)
end.
```

### Generic Server Loop

```erlang
-module(simple_server).
-export([start/0, loop/1]).

start() ->
    spawn(?MODULE, loop, [#{}]).

loop(State) ->
    receive
        {From, get, Key} ->
            Value = maps:get(Key, State, undefined),
            From ! {self(), Value},
            loop(State);

        {From, put, Key, Value} ->
            NewState = maps:put(Key, Value, State),
            From ! {self(), ok},
            loop(NewState);

        {From, stop} ->
            From ! {self(), stopping},
            ok;

        _ ->
            loop(State)
    end.
```

---

## OTP Behaviors

### gen_server

```erlang
-module(counter_server).
-behaviour(gen_server).

% API
-export([start_link/0, increment/0, get_count/0]).

% gen_server callbacks
-export([init/1, handle_call/3, handle_cast/2, handle_info/2, terminate/2, code_change/3]).

-define(SERVER, ?MODULE).

%%% API Functions

start_link() ->
    gen_server:start_link({local, ?SERVER}, ?MODULE, [], []).

increment() ->
    gen_server:cast(?SERVER, increment).

get_count() ->
    gen_server:call(?SERVER, get_count).

%%% gen_server Callbacks

init([]) ->
    {ok, 0}.  % Initial state: counter = 0

handle_call(get_count, _From, Count) ->
    {reply, Count, Count};

handle_call(_Request, _From, State) ->
    {reply, ok, State}.

handle_cast(increment, Count) ->
    {noreply, Count + 1};

handle_cast(_Msg, State) ->
    {noreply, State}.

handle_info(_Info, State) ->
    {noreply, State}.

terminate(_Reason, _State) ->
    ok.

code_change(_OldVsn, State, _Extra) ->
    {ok, State}.
```

### Supervisor

```erlang
-module(my_supervisor).
-behaviour(supervisor).

-export([start_link/0, init/1]).

start_link() ->
    supervisor:start_link({local, ?MODULE}, ?MODULE, []).

init([]) ->
    SupFlags = #{
        strategy => one_for_one,  % one_for_one, one_for_all, rest_for_one
        intensity => 5,           % Max restarts
        period => 60              % Within period (seconds)
    },

    ChildSpecs = [
        #{
            id => worker1,
            start => {worker_module, start_link, []},
            restart => permanent,     % permanent, temporary, transient
            shutdown => 5000,
            type => worker,
            modules => [worker_module]
        },
        #{
            id => worker2,
            start => {another_worker, start_link, [arg1]},
            restart => permanent,
            shutdown => 5000,
            type => worker,
            modules => [another_worker]
        }
    ],

    {ok, {SupFlags, ChildSpecs}}.
```

### gen_statem

```erlang
-module(door).
-behaviour(gen_statem).

-export([start_link/0, open/0, close/0, lock/0, unlock/0]).
-export([callback_mode/0, init/1, locked/3, unlocked/3, open/3, terminate/3]).

%%% API

start_link() ->
    gen_statem:start_link({local, ?MODULE}, ?MODULE, [], []).

open() -> gen_statem:cast(?MODULE, open).
close() -> gen_statem:cast(?MODULE, close).
lock() -> gen_statem:cast(?MODULE, lock).
unlock() -> gen_statem:cast(?MODULE, unlock).

%%% Callbacks

callback_mode() ->
    state_functions.

init([]) ->
    {ok, locked, #{}}.

%% State: locked
locked(cast, unlock, Data) ->
    {next_state, unlocked, Data};
locked(_EventType, _Event, Data) ->
    {keep_state, Data}.

%% State: unlocked
unlocked(cast, lock, Data) ->
    {next_state, locked, Data};
unlocked(cast, open, Data) ->
    {next_state, open, Data};
unlocked(_EventType, _Event, Data) ->
    {keep_state, Data}.

%% State: open
open(cast, close, Data) ->
    {next_state, unlocked, Data};
open(_EventType, _Event, Data) ->
    {keep_state, Data}.

terminate(_Reason, _State, _Data) ->
    ok.
```

---

## Error Handling

### Let It Crash Philosophy

```erlang
% Bad: Defensive programming
process_data(Data) ->
    try
        validate(Data),
        transform(Data),
        save(Data)
    catch
        error:Reason -> {error, Reason}
    end.

% Good: Let supervisor restart on failure
process_data(Data) ->
    validate(Data),      % Crash if invalid
    transform(Data),     % Crash if transform fails
    save(Data).         % Crash if save fails
```

### Try-Catch

```erlang
% Standard try-catch
divide(A, B) ->
    try A / B of
        Result -> {ok, Result}
    catch
        error:badarith -> {error, division_by_zero};
        error:Reason -> {error, Reason}
    end.

% Try-catch with after
process_file(Filename) ->
    {ok, File} = file:open(Filename, [read]),
    try
        do_work(File)
    catch
        error:Reason -> {error, Reason}
    after
        file:close(File)
    end.
```

### Exit Signals and Links

```erlang
% Trapping exits
process_flag(trap_exit, true),
Pid = spawn_link(fun() -> risky_operation() end),
receive
    {'EXIT', Pid, normal} ->
        ok;
    {'EXIT', Pid, Reason} ->
        io:format("Process died: ~p~n", [Reason])
end.

% Monitoring (one-way)
Pid = spawn(fun() -> worker() end),
Ref = monitor(process, Pid),
receive
    {'DOWN', Ref, process, Pid, Reason} ->
        io:format("Process down: ~p~n", [Reason])
end.
```

---

## Data Structures

### Lists

```erlang
% List operations
List = [1, 2, 3, 4, 5].
[H|T] = List.  % H = 1, T = [2,3,4,5]

% List comprehensions
Squares = [X*X || X <- [1,2,3,4,5]].  % [1,4,9,16,25]
Evens = [X || X <- [1,2,3,4,5,6], X rem 2 == 0].  % [2,4,6]

% Nested comprehensions
Pairs = [{X, Y} || X <- [1,2,3], Y <- [a,b]].
% [{1,a},{1,b},{2,a},{2,b},{3,a},{3,b}]

% Common list functions
length([1,2,3]).         % 3
lists:reverse([1,2,3]).  % [3,2,1]
lists:sort([3,1,2]).     % [1,2,3]
lists:map(fun(X) -> X*2 end, [1,2,3]).  % [2,4,6]
lists:filter(fun(X) -> X > 2 end, [1,2,3,4]).  % [3,4]
lists:foldl(fun(X, Acc) -> X + Acc end, 0, [1,2,3]).  % 6
```

### Maps

```erlang
% Creating maps
Map1 = #{name => "Alice", age => 30}.
Map2 = #{name := "Bob", age := 25}.  % := for matching

% Accessing values
#{name := Name} = Map1.  % Name = "Alice"
Age = maps:get(age, Map1).  % 30
Email = maps:get(email, Map1, "no-email").  % "no-email" (default)

% Updating maps
Map3 = Map1#{age := 31}.  % Update existing key
Map4 = Map1#{email => "alice@example.com"}.  % Add new key

% Map operations
maps:keys(Map1).      % [name, age]
maps:values(Map1).    % ["Alice", 30]
maps:size(Map1).      % 2
maps:is_key(name, Map1).  % true
maps:remove(age, Map1).   % #{name => "Alice"}
maps:merge(Map1, #{city => "NYC"}).
```

### Tuples

```erlang
% Creating tuples
Person = {person, "Alice", 30, "alice@example.com"}.

% Pattern matching
{person, Name, Age, Email} = Person.

% Tagged tuples (records alternative)
{ok, Value} = {ok, 42}.
{error, Reason} = {error, not_found}.

% Tuple operations
tuple_size(Person).  % 4
element(2, Person).  % "Alice"
setelement(3, Person, 31).  % {person, "Alice", 31, "alice@example.com"}
```

### Records

```erlang
% Define record
-record(person, {
    name :: string(),
    age :: integer(),
    email :: string()
}).

% Create record
Person = #person{name="Alice", age=30, email="alice@example.com"}.

% Access fields
Name = Person#person.name.  % "Alice"

% Update record
Person2 = Person#person{age=31}.

% Pattern match record
#person{name=Name, age=Age} = Person.
```

---

## ETS (Erlang Term Storage)

```erlang
% Create table
TableId = ets:new(my_table, [set, public, named_table]).
% Table types: set, ordered_set, bag, duplicate_bag

% Insert data
ets:insert(my_table, {key1, value1}).
ets:insert(my_table, [{key2, value2}, {key3, value3}]).

% Lookup data
[{key1, Value}] = ets:lookup(my_table, key1).

% Delete
ets:delete(my_table, key1).

% Iterate
ets:foldl(
    fun({Key, Value}, Acc) ->
        io:format("~p: ~p~n", [Key, Value]),
        Acc
    end,
    [],
    my_table
).

% Match patterns
Pattern = {'$1', '$2'},  % Any key, any value
ets:match(my_table, Pattern).

% Clean up
ets:delete(my_table).
```

---

## Distributed Erlang

### Node Communication

```erlang
% Start distributed node
% $ erl -name node1@hostname -setcookie secret_cookie

% Connect to another node
net_adm:ping('node2@hostname').  % pong | pang

% List connected nodes
nodes().

% Spawn on remote node
Pid = spawn('node2@hostname', Module, Function, Args).

% Send message to remote process
{registered_name, 'node2@hostname'} ! Message.

% RPC call
rpc:call('node2@hostname', Module, Function, Args).
```

### Distributed Example

```erlang
-module(distributed_counter).
-export([start/0, increment/1, get_value/1]).

start() ->
    register(counter, spawn(fun() -> loop(0) end)).

increment(Node) ->
    {counter, Node} ! {self(), increment},
    receive
        {counter, Value} -> Value
    end.

get_value(Node) ->
    {counter, Node} ! {self(), get},
    receive
        {counter, Value} -> Value
    end.

loop(Count) ->
    receive
        {From, increment} ->
            NewCount = Count + 1,
            From ! {counter, NewCount},
            loop(NewCount);
        {From, get} ->
            From ! {counter, Count},
            loop(Count)
    end.
```

---

## Common Patterns

### Timeout Pattern

```erlang
call_with_timeout(Pid, Request, Timeout) ->
    Pid ! {self(), Request},
    receive
        {Pid, Response} -> {ok, Response}
    after Timeout ->
        {error, timeout}
    end.
```

### Worker Pool Pattern

```erlang
-module(worker_pool).
-export([start/1, submit_task/2]).

start(PoolSize) ->
    [spawn(fun() -> worker_loop() end) || _ <- lists:seq(1, PoolSize)].

worker_loop() ->
    receive
        {From, Task} ->
            Result = execute_task(Task),
            From ! {self(), Result},
            worker_loop()
    end.

submit_task(Workers, Task) ->
    Worker = lists:nth(rand:uniform(length(Workers)), Workers),
    Worker ! {self(), Task},
    receive
        {Worker, Result} -> Result
    end.
```

### Pipeline Pattern

```erlang
pipeline(Data, Stages) ->
    lists:foldl(
        fun(Stage, Acc) -> Stage(Acc) end,
        Data,
        Stages
    ).

% Usage
Result = pipeline(
    Input,
    [
        fun validate/1,
        fun transform/1,
        fun enrich/1,
        fun save/1
    ]
).
```

---

## Module Structure

```erlang
-module(my_module).

% Module attributes
-author("Your Name").
-vsn("1.0.0").

% Behavior declarations
-behaviour(gen_server).

% Exports
-export([
    % Public API
    start_link/0,
    stop/0,

    % gen_server callbacks
    init/1,
    handle_call/3,
    handle_cast/2
]).

% Internal exports (for spawn, etc.)
-export([internal_function/1]).

% Type definitions
-type state() :: #{
    count := integer(),
    data := list()
}.

% Record definitions
-record(state, {
    count = 0 :: integer(),
    data = [] :: list()
}).

% Macros
-define(DEFAULT_TIMEOUT, 5000).
-define(SERVER, ?MODULE).

% Include files
-include("common.hrl").
-include_lib("kernel/include/file.hrl").

%%% API Functions

start_link() ->
    gen_server:start_link({local, ?SERVER}, ?MODULE, [], []).

%%% gen_server Callbacks

init([]) ->
    {ok, #state{}}.

%%% Internal Functions

internal_function(Arg) ->
    Arg * 2.
```

---

## Debugging and Tracing

```erlang
% Debug messages
io:format("Debug: ~p~n", [Variable]).

% Process info
process_info(Pid).
process_info(Pid, messages).
process_info(Pid, memory).

% System info
erlang:system_info(process_count).
erlang:system_info(schedulers).

% Basic tracing
dbg:tracer().
dbg:p(all, c).  % Trace all processes, calls
dbg:tpl(Module, Function, Arity, []).
dbg:stop_clear().

% Observer (GUI tool)
% $ erl
% 1> observer:start().
```

---

## Troubleshooting

### Process Not Receiving Messages

1. **Check process is alive**: `is_process_alive(Pid)`
2. **Verify message format**: Ensure sender/receiver patterns match
3. **Check mailbox**: `process_info(Pid, messages)`
4. **Look for selective receive**: Messages might be queued

### Supervisor Keeps Restarting Child

1. **Check init/1 return**: Must be `{ok, State}` or `{ok, State, Timeout}`
2. **Verify start_link**: Must return `{ok, Pid}` or `{ok, Pid, Info}`
3. **Review intensity/period**: May be restarting too frequently
4. **Check logs**: Look for crash reasons

### Pattern Match Failures

1. **Use catch**: Wrap in try-catch to see actual value
2. **Print before match**: `io:format("Value: ~p~n", [Value])`
3. **Check types**: Ensure atoms vs strings vs binaries
4. **Review guards**: Guards fail silently

### Performance Issues

1. **Avoid list concatenation**: Use `++` sparingly, prefer `[H|T]`
2. **Use ETS for shared state**: Don't pass large data in messages
3. **Profile with fprof**: `fprof:apply(Module, Function, Args)`
4. **Check for process bottlenecks**: Use observer to find message queue buildup

---

## Testing

### EUnit (Unit Testing)

```erlang
-module(calculator_tests).
-include_lib("eunit/include/eunit.hrl").

%% Simple test
simple_add_test() ->
    ?assertEqual(5, calculator:add(2, 3)).

%% Test with setup/cleanup
setup_test_() ->
    {setup,
     fun() -> setup() end,           % Setup
     fun(_) -> cleanup() end,        % Cleanup
     fun(_) -> ?assertEqual(42, get_value()) end
    }.

%% Test fixtures (multiple tests with same setup)
calculator_test_() ->
    {foreach,
     fun setup/0,
     fun cleanup/1,
     [
      fun test_addition/1,
      fun test_subtraction/1,
      fun test_multiplication/1
     ]}.

test_addition(_State) ->
    ?_assertEqual(5, calculator:add(2, 3)).

test_subtraction(_State) ->
    ?_assertEqual(1, calculator:subtract(3, 2)).

test_multiplication(_State) ->
    ?_assertEqual(6, calculator:multiply(2, 3)).

%% Assertions
assertions_test() ->
    % Equality
    ?assertEqual(Expected, Actual),
    ?assertNotEqual(NotExpected, Actual),

    % Boolean
    ?assert(true),
    ?assertNot(false),

    % Exceptions
    ?assertException(error, badarith, 1/0),
    ?assertError(badarg, list_to_integer("not_a_number")),
    ?assertThrow(my_exception, throw(my_exception)),
    ?assertExit(normal, exit(normal)),

    % Pattern matching
    ?assertMatch({ok, _}, {ok, 42}),
    ?assertMatch([H|_] when H > 0, [1, 2, 3]).

%% Generator test (multiple test cases)
divide_test_() ->
    [
     ?_assertEqual(2, calculator:divide(6, 3)),
     ?_assertEqual(5, calculator:divide(10, 2)),
     ?_assertError(badarith, calculator:divide(10, 0))
    ].

%% Test descriptions
named_tests_test_() ->
    [
     {"Addition of positive numbers",
      ?_assertEqual(5, calculator:add(2, 3))},
     {"Addition with negative numbers",
      ?_assertEqual(-1, calculator:add(-3, 2))},
     {"Addition with zero",
      ?_assertEqual(5, calculator:add(5, 0))}
    ].
```

### Common Test (Integration Testing)

```erlang
-module(database_SUITE).
-include_lib("common_test/include/ct.hrl").

%% CT callbacks
-export([all/0, groups/0, init_per_suite/1, end_per_suite/1,
         init_per_group/2, end_per_group/2,
         init_per_testcase/2, end_per_testcase/2]).

%% Test cases
-export([test_insert/1, test_query/1, test_delete/1,
         test_transaction/1, test_concurrent_access/1]).

%% Define all test cases
all() ->
    [
     {group, basic_operations},
     {group, advanced_operations}
    ].

%% Define test groups
groups() ->
    [
     {basic_operations, [sequence], [test_insert, test_query, test_delete]},
     {advanced_operations, [parallel], [test_transaction, test_concurrent_access]}
    ].

%% Suite-level setup (runs once)
init_per_suite(Config) ->
    application:start(database),
    [{db_conn, database:connect()} | Config].

end_per_suite(Config) ->
    Conn = ?config(db_conn, Config),
    database:disconnect(Conn),
    application:stop(database),
    ok.

%% Group-level setup
init_per_group(basic_operations, Config) ->
    [{table, create_test_table()} | Config];
init_per_group(advanced_operations, Config) ->
    [{table, create_test_table()}, {pool_size, 10} | Config].

end_per_group(_GroupName, Config) ->
    Table = ?config(table, Config),
    drop_table(Table),
    ok.

%% Test case setup/teardown
init_per_testcase(TestCase, Config) ->
    ct:log("Starting test: ~p", [TestCase]),
    Config.

end_per_testcase(TestCase, _Config) ->
    ct:log("Finished test: ~p", [TestCase]),
    ok.

%% Test cases
test_insert(Config) ->
    Conn = ?config(db_conn, Config),
    {ok, Id} = database:insert(Conn, #{name => "Alice", age => 30}),
    true = is_integer(Id).

test_query(Config) ->
    Conn = ?config(db_conn, Config),
    {ok, Results} = database:query(Conn, "SELECT * FROM users"),
    true = length(Results) > 0.

test_delete(Config) ->
    Conn = ?config(db_conn, Config),
    ok = database:delete(Conn, 1),
    {ok, []} = database:find(Conn, 1).

test_transaction(Config) ->
    Conn = ?config(db_conn, Config),
    ok = database:transaction(Conn, fun() ->
        database:insert(Conn, #{name => "Bob"}),
        database:insert(Conn, #{name => "Charlie"})
    end).

test_concurrent_access(Config) ->
    Conn = ?config(db_conn, Config),
    PoolSize = ?config(pool_size, Config),

    % Spawn concurrent workers
    Pids = [spawn_link(fun() -> worker(Conn) end) || _ <- lists:seq(1, PoolSize)],

    % Wait for all to complete
    [receive {done, Pid} -> ok end || Pid <- Pids],
    ok.

worker(Conn) ->
    database:insert(Conn, #{data => rand:uniform(1000)}),
    self() ! {done, self()}.
```

### PropEr (Property-Based Testing)

```erlang
-module(list_props).
-include_lib("proper/include/proper.hrl").

%% Property: reversing a list twice gives the original list
prop_reverse_twice() ->
    ?FORALL(List, list(integer()),
            lists:reverse(lists:reverse(List)) =:= List).

%% Property: length is preserved after reversing
prop_reverse_length() ->
    ?FORALL(List, list(any()),
            length(lists:reverse(List)) =:= length(List)).

%% Property: appending and reversing
prop_append_reverse() ->
    ?FORALL({L1, L2}, {list(integer()), list(integer())},
            lists:reverse(L1 ++ L2) =:=
            lists:reverse(L2) ++ lists:reverse(L1)).

%% Property with generators
prop_positive_sum() ->
    ?FORALL(List, non_empty(list(positive_integer())),
            lists:sum(List) > 0).

%% Custom generators
id() ->
    ?LET(N, range(1, 1000000), N).

user() ->
    ?LET({Name, Age}, {non_empty(string()), range(0, 150)},
         #{name => Name, age => Age}).

prop_user_validation() ->
    ?FORALL(User, user(),
            validator:is_valid_user(User)).

%% Stateful property testing
prop_counter_stateful() ->
    ?FORALL(Cmds, commands(?MODULE),
            begin
                {ok, Pid} = counter:start_link(),
                {History, State, Result} = run_commands(?MODULE, Cmds),
                counter:stop(Pid),
                ?WHENFAIL(
                    io:format("History: ~p\nState: ~p\nResult: ~p\n",
                             [History, State, Result]),
                    Result =:= ok
                )
            end).
```

### Mocking with Meck

```erlang
-module(user_service_tests).
-include_lib("eunit/include/eunit.hrl").

%% Test with mocking
mock_database_test() ->
    % Setup mock
    meck:new(database, [non_strict]),
    meck:expect(database, find, fun(1) -> {ok, #{id => 1, name => "Alice"}} end),

    % Test
    {ok, User} = user_service:get_user(1),
    ?assertEqual("Alice", maps:get(name, User)),

    % Verify mock was called
    ?assert(meck:called(database, find, [1])),

    % Cleanup
    meck:unload(database).

%% Test with multiple mocks
multiple_mocks_test() ->
    meck:new([database, cache], [non_strict]),

    meck:expect(cache, get, fun(_Key) -> {error, not_found} end),
    meck:expect(database, find, fun(1) -> {ok, #{id => 1}} end),
    meck:expect(cache, put, fun(_Key, _Value) -> ok end),

    % Service should check cache, then database, then update cache
    {ok, User} = user_service:get_user(1),

    ?assert(meck:called(cache, get, [1])),
    ?assert(meck:called(database, find, [1])),
    ?assert(meck:called(cache, put, [1, User])),

    meck:unload([database, cache]).

%% Passthrough mocking (partial mocking)
passthrough_test() ->
    meck:new(mymodule, [passthrough]),

    % Mock only specific function
    meck:expect(mymodule, expensive_function, fun() -> cached_result end),

    % Other functions work normally
    Result = mymodule:normal_function(),

    meck:unload(mymodule).

%% Sequence mocking (different returns per call)
sequence_test() ->
    meck:new(external_api, [non_strict]),

    meck:sequence(external_api, fetch_data, 0, [
        {error, timeout},
        {error, timeout},
        {ok, data}
    ]),

    % First two calls fail, third succeeds
    {error, timeout} = external_api:fetch_data(),
    {error, timeout} = external_api:fetch_data(),
    {ok, data} = external_api:fetch_data(),

    meck:unload(external_api).
```

### Test Fixtures and Setup

```erlang
-module(fixture_examples).
-include_lib("eunit/include/eunit.hrl").

%% Simple setup/cleanup
simple_fixture_test_() ->
    {setup,
     fun() ->
         Pid = setup_server(),
         Pid
     end,
     fun(Pid) ->
         stop_server(Pid)
     end,
     fun(Pid) ->
         [
          ?_assertEqual(ok, call_server(Pid, ping)),
          ?_assertEqual({ok, 42}, call_server(Pid, get_value))
         ]
     end
    }.

%% Foreach (setup for each test)
foreach_fixture_test_() ->
    {foreach,
     fun setup/0,
     fun cleanup/1,
     [
      fun test_case_1/1,
      fun test_case_2/1,
      fun test_case_3/1
     ]
    }.

setup() ->
    {ok, Pid} = my_server:start_link(),
    Pid.

cleanup(Pid) ->
    my_server:stop(Pid).

test_case_1(Pid) ->
    ?_assertEqual(ok, my_server:call(Pid, command1)).

%% Fixtures with state
stateful_fixture_test_() ->
    {foreach,
     fun() ->
         ets:new(test_table, [named_table, public]),
         ets:insert(test_table, {key1, value1}),
         test_table
     end,
     fun(Table) ->
         ets:delete(Table)
     end,
     [
      fun(Table) ->
          ?_assertEqual([{key1, value1}], ets:lookup(Table, key1))
      end
     ]
    }.

%% Nested fixtures
nested_fixture_test_() ->
    {setup,
     fun global_setup/0,
     fun global_cleanup/1,
     {foreach,
      fun per_test_setup/0,
      fun per_test_cleanup/1,
      [
       fun test_with_both_fixtures/1
      ]
     }
    }.
```

---

## Cross-Cutting Patterns

For cross-language comparison and translation patterns, see:

- `patterns-concurrency-dev` - Process patterns, message passing, supervisors
- `patterns-testing-dev` - Unit testing, property-based testing, mocking strategies
- `patterns-metaprogramming-dev` - Parse transforms, macros, behaviors

---

## References

- [Erlang/OTP Documentation](https://www.erlang.org/doc/)
- [Learn You Some Erlang](https://learnyousomeerlang.com/)
- [Erlang Design Principles](https://www.erlang.org/doc/design_principles/des_princ.html)
- [EUnit User's Guide](https://www.erlang.org/doc/apps/eunit/chapter.html)
- [Common Test User's Guide](https://www.erlang.org/doc/apps/common_test/users_guide.html)
- [PropEr Documentation](https://proper-testing.github.io/)
- [Meck GitHub Repository](https://github.com/eproxus/meck)
- `lang-erlang-patterns-dev` - Advanced design patterns
- `lang-erlang-release-dev` - Release management
- `lang-erlang-performance-dev` - Performance optimization
