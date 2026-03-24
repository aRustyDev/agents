---
name: convert-python-erlang
description: Convert Python code to idiomatic Erlang. Use when migrating Python projects to Erlang, translating Python patterns to idiomatic Erlang, or refactoring Python codebases for fault-tolerance, distributed computing, and concurrency. Extends meta-convert-dev with Python-to-Erlang specific patterns.
---

# Convert Python to Erlang

Convert Python code to idiomatic Erlang. This skill extends `meta-convert-dev` with Python-to-Erlang specific type mappings, idiom translations, and tooling for transforming dynamic, garbage-collected Python code into functional, concurrent, fault-tolerant Erlang.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Python types → Erlang types (dynamic → dynamic with pattern matching)
- **Idiom translations**: Python patterns → idiomatic Erlang
- **Error handling**: Exceptions → let it crash + supervision
- **Async patterns**: asyncio → processes + message passing
- **Concurrency model**: Threading/asyncio → lightweight processes + OTP
- **Class hierarchy**: OOP → functional + behavior modules

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Python language fundamentals - see `lang-python-dev`
- Erlang language fundamentals - see `lang-erlang-dev`
- Reverse conversion (Erlang → Python) - see `convert-erlang-python`

---

## Quick Reference

| Python | Erlang | Notes |
|--------|--------|-------|
| `int` | `integer()` | Arbitrary precision in both |
| `float` | `float()` | IEEE 754 double precision |
| `bool` | `true` / `false` atoms | Erlang booleans are atoms |
| `str` | `binary()` or `string()` | Binary for UTF-8, list of codepoints for string |
| `bytes` | `binary()` | Direct mapping |
| `list[T]` | `list(T)` | Singly-linked lists |
| `tuple` | `tuple()` | Immutable, fixed-size |
| `dict[K, V]` | `map()` or `dict` module | Maps for Erlang 17+, dict for older |
| `set[T]` | `sets` module | Use sets:new() |
| `None` | `undefined` atom | Or use tagged tuples like `{ok, Value}` / `error` |
| `Union[T, U]` | Tagged tuples | `{type1, Value}` / `{type2, Value}` |
| `Callable` | `fun()` | Anonymous or named functions |
| `async def` | `spawn()` + process | Async → concurrent process |
| `@dataclass` | `record` or `map` | Records for structured data |
| `Exception` | `throw`/`error`/`exit` | Let it crash philosophy |

## When Converting Code

1. **Analyze source thoroughly** before writing target
2. **Map types first** - create type equivalence table
3. **Embrace immutability** - all data is immutable in Erlang
4. **Preserve semantics** over syntax similarity
5. **Adopt Erlang idioms** - don't write "Python code in Erlang syntax"
6. **Think in processes** - replace threads/async with lightweight processes
7. **Let it crash** - replace defensive exception handling with supervision
8. **Pattern match** - use pattern matching instead of if/else chains
9. **Test equivalence** - same inputs → same outputs

---

## Type System Mapping

### Primitive Types

| Python | Erlang | Notes |
|--------|--------|-------|
| `int` | `integer()` | Both have arbitrary precision |
| `float` | `float()` | IEEE 754 double precision |
| `bool` | `true` / `false` | Atoms, not a separate type |
| `str` | `binary()` | UTF-8 binary: `<<"hello">>` |
| `str` | `string()` | List of codepoints: `"hello"` = `[104,101,108,108,111]` |
| `bytes` | `binary()` | Raw binary data |
| `bytearray` | `binary()` | Immutable in Erlang |
| `None` | `undefined` | Atom, or use option pattern |

**Critical Note on Strings**: Erlang has two string representations:
1. **Binaries** (`<<"text">>`): More memory-efficient, preferred for UTF-8 text
2. **Lists** (`"text"`): Lists of integers (codepoints), legacy representation

Use binaries for modern Erlang code.

### Collection Types

| Python | Erlang | Notes |
|--------|--------|-------|
| `list[T]` | `list(T)` | Singly-linked, immutable |
| `tuple` | `tuple()` | Fixed-size, immutable, pattern matchable |
| `dict[K, V]` | `map()` | Modern maps (Erlang 17+): `#{key => value}` |
| `dict[K, V]` | `dict` module | Legacy dict module |
| `set[T]` | `sets` module | `sets:new()`, `sets:add_element()` |
| `frozenset[T]` | `sets` module | All Erlang collections are immutable |
| `collections.deque` | `queue` module | `queue:new()`, FIFO operations |
| `collections.OrderedDict` | `map()` | Maps maintain insertion order (Erlang 18+) |
| `collections.defaultdict` | `maps:get(Key, Map, Default)` | Use default parameter |
| `collections.Counter` | `map()` | Map with integer values |

### Composite Types

| Python | Erlang | Notes |
|--------|--------|-------|
| `class` (data) | `record` | Compile-time record definition |
| `class` (data) | `map()` | Runtime structured data |
| `class` (behavior) | `behaviour` module | gen_server, gen_statem, etc. |
| `@dataclass` | `-record(name, {fields})` | Record with type specs |
| `typing.Protocol` | `behaviour` | Behavior contracts |
| `typing.TypedDict` | `map()` with type spec | `-type my_map() :: #{field := type()}.` |
| `typing.NamedTuple` | `record` or `tuple` | Record preferred for clarity |
| `enum.Enum` | `atoms` | Use atoms for enumerated values |
| `typing.Literal["a", "b"]` | `atoms` | `a`, `b` as atoms |
| `typing.Union[T, U]` | Tagged tuples | `{ok, Value}` / `{error, Reason}` |
| `typing.Optional[T]` | `Value | undefined` | Or `{ok, Value}` / `error` |
| `typing.Callable[[Args], Ret]` | `fun()` | `fun((Args) -> Ret)` |

### Type Annotations → Type Specs

| Python | Erlang | Notes |
|--------|--------|-------|
| `def f(x: int) -> int` | `-spec f(integer()) -> integer().` | Function type specification |
| `def f(x: T) -> T` | `-spec f(T) -> T when T :: any().` | Generic type variable |
| `x: Any` | `any()` | Top type |
| `x: list[int]` | `[integer()]` | List of integers |
| `x: Optional[int]` | `integer() \| undefined` | Union type |

---

## Idiom Translation

### Pattern 1: None Handling (Option Pattern)

**Python:**
```python
# Optional chaining with walrus operator
if user := get_user(user_id):
    name = user.name
else:
    name = "Anonymous"

# Or simpler
name = user.name if user else "Anonymous"
```

**Erlang:**
```erlang
% Tagged tuple pattern
case get_user(UserId) of
    {ok, User} ->
        Name = maps:get(name, User);
    error ->
        Name = <<"Anonymous">>
end.

% Or with pattern matching in function head
get_user_name(UserId) ->
    case get_user(UserId) of
        {ok, #{name := Name}} -> Name;
        error -> <<"Anonymous">>
    end.
```

**Why this translation:**
- Python uses None/truthy checks; Erlang uses tagged tuples `{ok, Value}` / `error`
- Erlang's pattern matching is more explicit and compile-time checked
- Tagged tuples are the idiomatic Erlang way to represent optional values

### Pattern 2: List Comprehensions

**Python:**
```python
# List comprehension
squared_evens = [x * x for x in numbers if x % 2 == 0]

# Generator expression
total = sum(x * x for x in numbers if x % 2 == 0)
```

**Erlang:**
```erlang
% List comprehension
SquaredEvens = [X * X || X <- Numbers, X rem 2 == 0].

% Fold for aggregation
Total = lists:foldl(
    fun(X, Acc) when X rem 2 == 0 -> Acc + X * X;
       (_, Acc) -> Acc
    end,
    0,
    Numbers
).

% Or filter + map + sum
Total = lists:sum(
    lists:map(
        fun(X) -> X * X end,
        lists:filter(fun(X) -> X rem 2 == 0 end, Numbers)
    )
).
```

**Why this translation:**
- Erlang list comprehensions are syntactically similar to Python's
- Use `||` instead of `for`, guards instead of `if`
- For aggregation, `lists:foldl/3` is the standard approach
- List operations in Erlang are functional transformations

### Pattern 3: Dictionary Operations

**Python:**
```python
# Get with default
value = config.get("timeout", 30)

# Setdefault pattern
cache.setdefault(key, expensive_compute())

# Dictionary comprehension
squared = {k: v * v for k, v in items.items()}
```

**Erlang:**
```erlang
% Get with default
Value = maps:get(timeout, Config, 30).

% Update only if not present (immutable, returns new map)
NewCache = case maps:is_key(Key, Cache) of
    true -> Cache;
    false -> maps:put(Key, expensive_compute(), Cache)
end.

% Map comprehension (Erlang 18+)
Squared = maps:from_list([{K, V * V} || {K, V} <- maps:to_list(Items)]).

% Or more idiomatically with maps:map/2
Squared = maps:map(fun(_K, V) -> V * V end, Items).
```

**Why this translation:**
- Erlang maps are immutable; operations return new maps
- `maps:get/3` takes default as third parameter
- `maps:map/2` transforms values while preserving keys
- No direct equivalent to setdefault because of immutability

### Pattern 4: String Formatting

**Python:**
```python
# f-strings (Python 3.6+)
message = f"User {user.name} has {count} items"

# format method
message = "User {} has {} items".format(user.name, count)

# % formatting (old style)
message = "User %s has %d items" % (user.name, count)
```

**Erlang:**
```erlang
% io_lib:format/2 (returns iolist, needs flattening for string)
Message = io_lib:format("User ~s has ~p items", [Name, Count]),
FlatMessage = lists:flatten(Message).

% For binaries (more common in modern Erlang)
Message = iolist_to_binary(io_lib:format("User ~s has ~p items", [Name, Count])).

% String concatenation with binaries
Message = <<<<"User ">>/binary, Name/binary, <<" has ">>/binary,
            (integer_to_binary(Count))/binary, <<" items">>/binary>>.
```

**Why this translation:**
- Erlang uses `io_lib:format/2` with format specifiers: `~s` (string), `~p` (any term), `~w` (term), `~.2f` (float)
- Returns an iolist, not a string - flatten or convert to binary
- Binary concatenation is efficient but verbose; use `io_lib:format/2` for readability

### Pattern 5: Duck Typing → Behaviors

**Python:**
```python
# Duck typing - if it has a .read() method, it's file-like
def process_data(file_like):
    data = file_like.read()
    return parse(data)

# Works with files, StringIO, BytesIO, etc.
```

**Erlang:**
```erlang
% Behavior-based - explicit contract
-module(file_processor).

% Define behavior
-callback read(State :: any()) -> {ok, binary()} | {error, term()}.

% Use behavior
process_data(Module, State) ->
    case Module:read(State) of
        {ok, Data} -> parse(Data);
        {error, Reason} -> {error, Reason}
    end.

% Or use process-based abstraction
process_data(Pid) ->
    Pid ! {self(), read},
    receive
        {Pid, {ok, Data}} -> parse(Data);
        {Pid, {error, Reason}} -> {error, Reason}
    end.
```

**Why this translation:**
- Erlang uses explicit behaviors (`-behaviour(gen_server)`) instead of duck typing
- Behavior modules define callbacks that implementing modules must provide
- Process-based abstraction is more common: send messages, receive responses
- Compile-time checking of behavior implementations

### Pattern 6: Context Managers → Process Lifecycle

**Python:**
```python
# with statement for resource management
with open("data.txt") as f:
    data = f.read()
# File automatically closed

# Custom context manager
with lock_held(mutex):
    # Critical section
    pass
# Lock automatically released
```

**Erlang:**
```erlang
% File I/O with automatic cleanup
process_file(Filename) ->
    {ok, File} = file:open(Filename, [read]),
    try
        {ok, Data} = file:read(File, 1024 * 1024),
        process_data(Data)
    after
        file:close(File)
    end.

% Process-based resource management
with_lock(LockPid, Fun) ->
    LockPid ! {self(), acquire},
    receive
        {LockPid, acquired} ->
            try
                Fun()
            after
                LockPid ! {self(), release}
            end
    end.
```

**Why this translation:**
- Erlang uses `try...after` for cleanup guarantees (similar to Python's finally)
- Process-based patterns are common: spawn a process to manage the resource
- Processes can be supervised; if they crash, supervisor handles cleanup
- No __enter__/__exit__ protocol; use explicit try...after blocks

### Pattern 7: Async/Await → Processes and Message Passing

**Python:**
```python
# Async function
async def fetch_user(user_id: int) -> dict:
    await asyncio.sleep(0.1)  # Simulate I/O
    return {"id": user_id, "name": f"User {user_id}"}

# Concurrent execution
async def main():
    users = await asyncio.gather(
        fetch_user(1),
        fetch_user(2),
        fetch_user(3)
    )
    print(users)
```

**Erlang:**
```erlang
% Spawned process
fetch_user(UserId) ->
    timer:sleep(100),  % Simulate I/O
    #{id => UserId, name => iolist_to_binary(io_lib:format("User ~p", [UserId]))}.

% Concurrent execution with processes
main() ->
    Self = self(),
    spawn(fun() -> Self ! {user, 1, fetch_user(1)} end),
    spawn(fun() -> Self ! {user, 2, fetch_user(2)} end),
    spawn(fun() -> Self ! {user, 3, fetch_user(3)} end),

    % Collect results
    Users = [receive {user, Id, User} -> User end || Id <- [1, 2, 3]],
    io:format("~p~n", [Users]).

% Or use a process pool pattern
main() ->
    Tasks = [1, 2, 3],
    Results = pmap(fun fetch_user/1, Tasks),
    io:format("~p~n", [Results]).

pmap(Fun, List) ->
    Parent = self(),
    Pids = [spawn(fun() -> Parent ! {self(), Fun(X)} end) || X <- List],
    [receive {Pid, Result} -> Result end || Pid <- Pids].
```

**Why this translation:**
- Python's async/await creates coroutines; Erlang uses lightweight processes
- Erlang processes are true concurrency primitives (can run on different cores)
- Message passing replaces async callbacks
- No event loop needed - BEAM VM handles scheduling
- Processes are isolated and fault-tolerant

### Pattern 8: Exception Handling → Let It Crash

**Python:**
```python
# Defensive exception handling
def process_data(data):
    try:
        validate(data)
        transformed = transform(data)
        save(transformed)
        return {"status": "success"}
    except ValueError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"status": "error", "message": "Internal error"}
```

**Erlang:**
```erlang
% Let it crash - supervisor will restart
process_data(Data) ->
    validate(Data),      % Crash if invalid
    Transformed = transform(Data),  % Crash if transform fails
    save(Transformed),   % Crash if save fails
    {status, success}.

% Supervisor tree handles failures
-module(my_supervisor).
-behaviour(supervisor).

init([]) ->
    SupFlags = #{
        strategy => one_for_one,
        intensity => 5,
        period => 60
    },
    ChildSpecs = [
        #{
            id => worker,
            start => {worker_module, start_link, []},
            restart => permanent,
            shutdown => 5000,
            type => worker
        }
    ],
    {ok, {SupFlags, ChildSpecs}}.

% Only catch errors at supervision boundaries
handle_request(Data) ->
    try
        process_data(Data)
    catch
        error:Reason -> {error, Reason};
        exit:Reason -> {error, {exit, Reason}}
    end.
```

**Why this translation:**
- Python: defensive programming with try/except everywhere
- Erlang: let processes crash, supervisors restart them
- Errors are expected; design for failure, not defensive coding
- Try/catch only at supervision boundaries or API boundaries
- Supervision trees provide fault isolation and recovery

### Pattern 9: Class Inheritance → Behavior + gen_server

**Python:**
```python
# Class hierarchy
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        raise NotImplementedError

class Dog(Animal):
    def speak(self):
        return f"{self.name} says Woof!"

# Usage
dog = Dog("Buddy")
print(dog.speak())
```

**Erlang:**
```erlang
% Behavior module (defines interface)
-module(animal).
-callback speak(Name :: binary()) -> binary().

% Implementation module
-module(dog).
-behaviour(animal).
-export([speak/1]).

speak(Name) ->
    <<Name/binary, " says Woof!">>.

% Or use gen_server for stateful objects
-module(dog_server).
-behaviour(gen_server).
-export([start_link/1, speak/1]).
-export([init/1, handle_call/3, handle_cast/2]).

start_link(Name) ->
    gen_server:start_link(?MODULE, Name, []).

speak(Pid) ->
    gen_server:call(Pid, speak).

init(Name) ->
    {ok, #{name => Name}}.

handle_call(speak, _From, #{name := Name} = State) ->
    Reply = <<Name/binary, " says Woof!">>,
    {reply, Reply, State}.

handle_cast(_Msg, State) ->
    {noreply, State}.
```

**Why this translation:**
- Erlang has no inheritance; use behaviors for contracts
- Behaviors define callbacks that modules must implement
- For stateful objects, use gen_server (OTP behavior)
- Composition over inheritance is enforced
- Process-based objects can be supervised

### Pattern 10: Decorators → Parse Transforms or Wrapper Functions

**Python:**
```python
# Function decorator
@cache
def expensive_func(x):
    return compute(x)

# Property decorator
class Circle:
    @property
    def area(self):
        return 3.14159 * self.radius ** 2
```

**Erlang:**
```erlang
% No direct decorator equivalent - use wrapper functions
expensive_func(X) ->
    case cache:get(X) of
        {ok, Result} -> Result;
        error ->
            Result = compute(X),
            cache:put(X, Result),
            Result
    end.

% Records don't have methods - use functions
-record(circle, {radius}).

area(#circle{radius = R}) ->
    3.14159 * R * R.

% Or use maps with computed access
circle_area(#{radius := R}) ->
    3.14159 * R * R.

% Parse transforms for compile-time metaprogramming (advanced)
% Similar to decorators but requires compiler hooks
```

**Why this translation:**
- Erlang has no decorators; use explicit wrapper functions
- Parse transforms can modify AST at compile time (advanced, rarely needed)
- Functions are first-class; pass them as arguments for HOF patterns
- Records and maps don't have methods; use module functions instead

---

## Error Handling

### Python Exceptions → Erlang Error Model

| Python | Erlang | When to Use |
|--------|--------|-------------|
| `raise Exception("msg")` | `error({reason, Msg})` | Internal errors, let it crash |
| `raise ValueError("msg")` | `error(badarg)` | Invalid arguments |
| `try...except` | `try...catch` | API boundaries only |
| `try...finally` | `try...after` | Resource cleanup |
| Exception chaining | Nested tuples | `{error, {reason, {cause, SubReason}}}` |

### Exception Translation

**Python:**
```python
try:
    result = risky_operation()
except ValueError as e:
    handle_value_error(e)
except KeyError as e:
    handle_key_error(e)
except Exception as e:
    handle_generic_error(e)
finally:
    cleanup()
```

**Erlang:**
```erlang
try
    Result = risky_operation(),
    process_result(Result)
catch
    error:badarg -> handle_badarg();
    error:{badkey, _} -> handle_badkey();
    error:Reason -> handle_generic_error(Reason);
    exit:Reason -> handle_exit(Reason)
after
    cleanup()
end.
```

---

## Concurrency Patterns

### Threading → Lightweight Processes

**Python:**
```python
import threading

def worker(name, delay):
    time.sleep(delay)
    print(f"Worker {name} done")

threads = [
    threading.Thread(target=worker, args=(f"T{i}", 1))
    for i in range(5)
]

for t in threads:
    t.start()

for t in threads:
    t.join()
```

**Erlang:**
```erlang
worker(Name, Delay) ->
    timer:sleep(Delay),
    io:format("Worker ~s done~n", [Name]).

main() ->
    Pids = [
        spawn(fun() -> worker(io_lib:format("T~p", [I]), 1000) end)
        || I <- lists:seq(1, 5)
    ],

    % Wait for all to complete (using monitors)
    [begin
        Ref = monitor(process, Pid),
        receive
            {'DOWN', Ref, process, Pid, _} -> ok
        end
     end || Pid <- Pids].
```

### Asyncio → gen_server

**Python:**
```python
import asyncio

class Counter:
    def __init__(self):
        self.count = 0

    async def increment(self):
        self.count += 1

    async def get_count(self):
        return self.count

async def main():
    counter = Counter()
    await counter.increment()
    await counter.increment()
    count = await counter.get_count()
    print(f"Count: {count}")
```

**Erlang:**
```erlang
-module(counter).
-behaviour(gen_server).
-export([start_link/0, increment/0, get_count/0]).
-export([init/1, handle_call/3, handle_cast/2]).

start_link() ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [], []).

increment() ->
    gen_server:cast(?MODULE, increment).

get_count() ->
    gen_server:call(?MODULE, get_count).

init([]) ->
    {ok, 0}.

handle_call(get_count, _From, Count) ->
    {reply, Count, Count}.

handle_cast(increment, Count) ->
    {noreply, Count + 1}.

% Usage
main() ->
    {ok, _Pid} = counter:start_link(),
    counter:increment(),
    counter:increment(),
    Count = counter:get_count(),
    io:format("Count: ~p~n", [Count]).
```

---

## Common Pitfalls

1. **Treating Erlang as Object-Oriented**: Erlang is functional. Don't try to recreate class hierarchies. Use behaviors, modules, and processes.

2. **Excessive Try-Catch**: Don't wrap everything in try-catch. Let processes crash and use supervisors for fault recovery.

3. **String Confusion**: Erlang strings are lists of integers. Use binaries (`<<"text">>`) for UTF-8 text in modern code.

4. **Mutable State Mindset**: All data is immutable. Operations return new values. Use processes for mutable state via message passing.

5. **List Concatenation in Loops**: `List ++ Element` creates a new list each time (O(n)). Use cons `[Element | List]` and reverse, or use `lists:reverse/2`.

6. **Ignoring Process Leaks**: Spawned processes live until they exit. Always ensure processes terminate or are linked/monitored.

7. **Not Using Pattern Matching**: Erlang's strength is pattern matching. Use it in function heads, case expressions, and receive clauses.

8. **Forgetting Tail Recursion**: Recursive functions must be tail-recursive to avoid stack overflow. Use accumulator parameters.

9. **Maps vs Records**: Records are compile-time, maps are runtime. Records are faster and type-checked, but less flexible.

10. **Process Bottlenecks**: Single process handling all messages becomes a bottleneck. Design for parallelism with process pools or parallel message handling.

---

## Tooling

| Tool | Purpose | Notes |
|------|---------|-------|
| `rebar3` | Build tool | Standard build tool for Erlang projects |
| `dialyzer` | Static analyzer | Type checking via success typing |
| `eunit` | Unit testing | Built-in unit test framework |
| `common_test` | Integration testing | OTP testing framework |
| `PropEr` | Property-based testing | Similar to Python's Hypothesis |
| `meck` | Mocking library | Mock modules for testing |
| `observer` | GUI profiler | Visual process/memory inspector |
| `dbg` | Tracing | Built-in tracing for debugging |
| `py2erl` | Transpiler | Experimental Python to Erlang compiler |
| `ErlPort` | Python interop | Call Python from Erlang |

---

## Examples

### Example 1: Simple - HTTP Request Handler

**Before (Python):**
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = database.find_user(user_id)
    if user:
        return jsonify(user)
    else:
        return jsonify({"error": "Not found"}), 404

if __name__ == '__main__':
    app.run()
```

**After (Erlang):**
```erlang
% Using Cowboy web server
-module(user_handler).
-export([init/2]).

init(Req0, State) ->
    UserId = cowboy_req:binding(user_id, Req0),
    case database:find_user(binary_to_integer(UserId)) of
        {ok, User} ->
            Req = cowboy_req:reply(200,
                #{<<"content-type">> => <<"application/json">>},
                jsx:encode(User),
                Req0),
            {ok, Req, State};
        error ->
            Req = cowboy_req:reply(404,
                #{<<"content-type">> => <<"application/json">>},
                jsx:encode(#{error => <<"Not found">>}),
                Req0),
            {ok, Req, State}
    end.
```

### Example 2: Medium - Concurrent Data Processing

**Before (Python):**
```python
import asyncio

async def process_item(item):
    # Simulate processing
    await asyncio.sleep(0.1)
    return item * 2

async def process_batch(items):
    tasks = [process_item(item) for item in items]
    results = await asyncio.gather(*tasks)
    return sum(results)

# Usage
items = list(range(1, 11))
result = asyncio.run(process_batch(items))
print(f"Total: {result}")
```

**After (Erlang):**
```erlang
-module(batch_processor).
-export([process_batch/1]).

process_item(Item) ->
    timer:sleep(100),  % Simulate processing
    Item * 2.

process_batch(Items) ->
    Parent = self(),
    Pids = [spawn(fun() ->
                Result = process_item(Item),
                Parent ! {self(), Result}
            end) || Item <- Items],

    % Collect results
    Results = [receive {Pid, Result} -> Result end || Pid <- Pids],
    lists:sum(Results).

% Usage
% 1> Items = lists:seq(1, 10).
% 2> batch_processor:process_batch(Items).
% 110
```

### Example 3: Complex - Stateful Worker Pool with Supervision

**Before (Python):**
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
import queue

class WorkerPool:
    def __init__(self, num_workers=5):
        self.queue = queue.Queue()
        self.workers = []
        self.executor = ThreadPoolExecutor(max_workers=num_workers)

    def start(self):
        for i in range(5):
            future = self.executor.submit(self.worker, i)
            self.workers.append(future)

    def worker(self, worker_id):
        while True:
            try:
                task = self.queue.get(timeout=1)
                result = self.process_task(task)
                print(f"Worker {worker_id}: {result}")
                self.queue.task_done()
            except queue.Empty:
                continue

    def process_task(self, task):
        # Simulate work
        return task * 2

    def submit(self, task):
        self.queue.put(task)

    def shutdown(self):
        self.executor.shutdown(wait=True)

# Usage
pool = WorkerPool(num_workers=5)
pool.start()
for i in range(20):
    pool.submit(i)
```

**After (Erlang):**
```erlang
%% Worker pool supervisor
-module(worker_pool_sup).
-behaviour(supervisor).
-export([start_link/1, init/1]).

start_link(PoolSize) ->
    supervisor:start_link({local, ?MODULE}, ?MODULE, PoolSize).

init(PoolSize) ->
    SupFlags = #{
        strategy => one_for_one,
        intensity => 5,
        period => 60
    },

    Workers = [
        #{
            id => {worker, N},
            start => {worker, start_link, [N]},
            restart => permanent,
            shutdown => 5000,
            type => worker
        } || N <- lists:seq(1, PoolSize)
    ],

    {ok, {SupFlags, Workers}}.

%% Worker gen_server
-module(worker).
-behaviour(gen_server).
-export([start_link/1, submit_task/2]).
-export([init/1, handle_call/3, handle_cast/2, handle_info/2]).

start_link(WorkerId) ->
    gen_server:start_link({local, list_to_atom("worker_" ++ integer_to_list(WorkerId))},
                          ?MODULE, WorkerId, []).

submit_task(WorkerPid, Task) ->
    gen_server:cast(WorkerPid, {task, Task}).

init(WorkerId) ->
    {ok, #{worker_id => WorkerId}}.

handle_cast({task, Task}, #{worker_id := WorkerId} = State) ->
    Result = process_task(Task),
    io:format("Worker ~p: ~p~n", [WorkerId, Result]),
    {noreply, State}.

handle_call(_Request, _From, State) ->
    {reply, ok, State}.

handle_info(_Info, State) ->
    {noreply, State}.

process_task(Task) ->
    Task * 2.

%% Pool manager
-module(pool_manager).
-export([start/1, submit/1]).

start(PoolSize) ->
    worker_pool_sup:start_link(PoolSize).

submit(Task) ->
    % Simple round-robin distribution
    Workers = [list_to_atom("worker_" ++ integer_to_list(N)) || N <- lists:seq(1, 5)],
    Worker = lists:nth(rand:uniform(length(Workers)), Workers),
    worker:submit_task(Worker, Task).

%% Usage
%% 1> pool_manager:start(5).
%% 2> [pool_manager:submit(I) || I <- lists:seq(1, 20)].
```

**Key differences:**
- Python: ThreadPoolExecutor with shared queue
- Erlang: Supervised worker processes with message passing
- Erlang workers are fault-tolerant (supervisor restarts failed workers)
- No shared state; each worker is an isolated process
- Erlang's supervision tree provides automatic recovery

---

## Limitations

Due to gaps in the `lang-erlang-dev` skill (5/8 pillars), external research was required for:
- **Serialization idioms**: JSON encoding/decoding with `jsx`, term serialization
- **Build/dependency management**: rebar3 usage, dependency declaration, release building
- **Metaprogramming details**: Parse transforms (mentioned but limited coverage)

These areas are covered in this skill based on external documentation and community patterns.

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `convert-python-rust` - Python → Rust conversion for performance focus
- `lang-python-dev` - Python development patterns
- `lang-erlang-dev` - Erlang development patterns

Cross-cutting pattern skills:
- `patterns-concurrency-dev` - Process patterns, message passing, supervision across languages
- `patterns-testing-dev` - Unit testing, property-based testing, mocking strategies across languages

---

## References

- [Erlang/OTP Documentation](https://www.erlang.org/doc/)
- [Learn You Some Erlang](https://learnyousomeerlang.com/)
- [Python to Erlang Converter](https://www.codeconvert.ai/python-to-erlang-converter)
- [py2erl - Python to Erlang Compiler](https://github.com/sash-ko/py2erl)
- [ErlPort - Python/Erlang Integration](http://erlport.org/docs/python.html)
- [Erlang for Python Programmers](http://openbookproject.net/py4fun/erlang/erlang.html)
