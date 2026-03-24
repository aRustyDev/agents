---
name: convert-erlang-fsharp
description: Bidirectional conversion between Erlang and Fsharp. Use when migrating projects between these languages in either direction. Extends meta-convert-dev with Erlang↔Fsharp specific patterns.
---

# Erlang to F# Conversion

## Overview

This skill guides the conversion of Erlang code to idiomatic F# while maintaining functional programming principles, concurrent programming patterns, and fault-tolerance capabilities. F# provides strong functional programming support with .NET integration.

## Key Language Differences

### Type Systems
- **Erlang**: Dynamic typing with pattern matching
- **F#**: Static typing with type inference, algebraic data types

### Concurrency Models
- **Erlang**: Actor model with lightweight processes, message passing
- **F#**: MailboxProcessor (similar to actors), async workflows, Task Parallel Library

### Runtime Environment
- **Erlang**: BEAM VM with hot code swapping, distributed computing
- **F#**: .NET CLR with async/await, comprehensive standard library

---

## Quick Reference

| Erlang | F# | Notes |
|--------|-----|-------|
| `atom()` | `string` or discriminated union | Atoms become strings or DU cases |
| `integer()` | `int` or `int64` | Fixed-size integers |
| `float()` | `float` | 64-bit double |
| `binary()` | `byte[]` | Byte arrays |
| `list()` | `'a list` | Immutable lists |
| `tuple()` | `'a * 'b` | Product types |
| `map()` | `Map<'k,'v>` | Immutable maps |
| `pid()` | `MailboxProcessor<'T>` | Actor-style processing |
| `fun()` | `'a -> 'b` | First-class functions |

---

## Core Conversion Patterns

### 1. Module and Function Definitions

**Erlang:**
```erlang
-module(calculator).
-export([add/2, multiply/2]).

add(X, Y) -> X + Y.
multiply(X, Y) -> X * Y.
```

**F#:**
```fsharp
module Calculator =
    let add x y = x + y
    let multiply x y = x * y
```

### 2. Pattern Matching

**Erlang:**
```erlang
factorial(0) -> 1;
factorial(N) when N > 0 -> N * factorial(N - 1).
```

**F#:**
```fsharp
let rec factorial n =
    match n with
    | 0 -> 1
    | n when n > 0 -> n * factorial (n - 1)
    | _ -> failwith "Negative input not allowed"
```

### 3. Records and Types

**Erlang:**
```erlang
-record(person, {name, age, email}).

create_person(Name, Age, Email) ->
    #person{name=Name, age=Age, email=Email}.
```

**F#:**
```fsharp
type Person = {
    Name: string
    Age: int
    Email: string
}

let createPerson name age email =
    { Name = name; Age = age; Email = email }
```

### 4. Lists and Comprehensions

**Erlang:**
```erlang
double_list(List) -> [X * 2 || X <- List].
filter_even(List) -> [X || X <- List, X rem 2 =:= 0].
```

**F#:**
```fsharp
let doubleList list =
    list |> List.map ((*) 2)

let filterEven list =
    list |> List.filter (fun x -> x % 2 = 0)
```

### 5. Actor Model / Process Communication

**Erlang:**
```erlang
-module(counter).

start() ->
    spawn(fun() -> loop(0) end).

increment(Pid) ->
    Pid ! {increment, self()},
    receive
        {ok, NewValue} -> NewValue
    end.

loop(Count) ->
    receive
        {increment, From} ->
            NewCount = Count + 1,
            From ! {ok, NewCount},
            loop(NewCount)
    end.
```

**F#:**
```fsharp
module Counter =
    type Message =
        | Increment of AsyncReplyChannel<int>

    type CounterAgent() =
        let agent = MailboxProcessor.Start(fun inbox ->
            let rec loop count = async {
                let! msg = inbox.Receive()
                match msg with
                | Increment(reply) ->
                    let newCount = count + 1
                    reply.Reply(newCount)
                    return! loop newCount
            }
            loop 0
        )

        member _.Increment() = agent.PostAndReply(Increment)

    let start() = CounterAgent()
```

### 6. gen_server Pattern

**Erlang:**
```erlang
-module(my_server).
-behaviour(gen_server).

handle_call(get_count, _From, State = #{count := Count}) ->
    {reply, Count, State};
handle_call({increment, N}, _From, State = #{count := Count}) ->
    NewState = State#{count := Count + N},
    {reply, ok, NewState}.
```

**F#:**
```fsharp
module MyServer =
    type Message =
        | GetCount of AsyncReplyChannel<int>
        | Increment of int * AsyncReplyChannel<unit>

    type State = { Count: int }

    type ServerAgent() =
        let agent = MailboxProcessor.Start(fun inbox ->
            let rec loop state = async {
                let! msg = inbox.Receive()
                match msg with
                | GetCount(reply) ->
                    reply.Reply(state.Count)
                    return! loop state
                | Increment(n, reply) ->
                    let newState = { Count = state.Count + n }
                    reply.Reply()
                    return! loop newState
            }
            loop { Count = 0 }
        )

        member _.GetCount() = agent.PostAndReply(GetCount)
        member _.Increment(n) = agent.PostAndReply(fun ch -> Increment(n, ch))
```

### 7. Error Handling

**Erlang:**
```erlang
safe_divide(_, 0) -> {error, division_by_zero};
safe_divide(X, Y) -> {ok, X / Y}.
```

**F#:**
```fsharp
type DivisionError = DivisionByZero

let safeDivide x y =
    match y with
    | 0 -> Error DivisionByZero
    | _ -> Ok (x / y)

// Or using Option
let safeDivide' x y =
    match y with
    | 0 -> None
    | _ -> Some (x / y)
```

### 8. Binary Pattern Matching

**Erlang:**
```erlang
parse_header(<<Type:8, Length:16, Rest/binary>>) ->
    {Type, Length, Rest}.
```

**F#:**
```fsharp
let parseHeader (bytes: byte[]) =
    if bytes.Length < 3 then
        None
    else
        let type' = bytes.[0]
        let length = (uint16 bytes.[1] <<< 8) ||| uint16 bytes.[2]
        let rest = bytes.[3..]
        Some (type', length, rest)
```

### 9. ETS Tables to .NET Collections

**Erlang:**
```erlang
store(Key, Value) ->
    ets:insert(my_table, {Key, Value}).

lookup(Key) ->
    case ets:lookup(my_table, Key) of
        [{Key, Value}] -> {ok, Value};
        [] -> {error, not_found}
    end.
```

**F#:**
```fsharp
module MyTable =
    open System.Collections.Concurrent

    let private table = ConcurrentDictionary<string, obj>()

    let store key value =
        table.[key] <- value

    let lookup key =
        match table.TryGetValue(key) with
        | true, value -> Some value
        | false, _ -> None
```

---

## Common Libraries and Equivalents

| Erlang | F# / .NET Equivalent |
|--------|---------------------|
| gen_server | MailboxProcessor, Akka.NET actors |
| supervisor | Custom supervision, Akka.NET |
| ETS | System.Collections.Concurrent |
| httpc | System.Net.Http, FSharp.Data.Http |
| jsx (JSON) | System.Text.Json, FSharp.Json |
| cowboy (HTTP) | ASP.NET Core, Giraffe, Suave |
| lager (logging) | Serilog, NLog |

---

## Best Practices

### 1. Embrace Static Typing
- Use F#'s type system to catch errors at compile time
- Define explicit types for domain models
- Use discriminated unions for state machines

### 2. Preserve Functional Patterns
- Keep functions pure where possible
- Use immutable data structures
- Leverage F# pipeline operators (|>)

### 3. Adapt Concurrency Models
- Use MailboxProcessor for actor-like behavior
- Consider Akka.NET for complex distributed systems
- Use async workflows for I/O-bound operations

### 4. Error Handling
- Prefer Option and Result types over exceptions
- Use computation expressions for error propagation
- Reserve exceptions for truly exceptional cases

---

## Migration Strategy

### Step 1: Analyze Erlang Codebase
- Identify module structure and dependencies
- Map OTP behaviors (gen_server, supervisor)
- Document message-passing patterns

### Step 2: Design F# Architecture
- Plan module organization
- Design type hierarchy for records and unions
- Choose concurrency approach

### Step 3: Convert Core Logic
- Start with pure functions and data structures
- Convert pattern matching and recursion
- Translate list operations

### Step 4: Implement Concurrency
- Replace spawn/receive with MailboxProcessor
- Convert gen_server to agent-based patterns
- Add async workflows for I/O operations

### Step 5: Testing and Validation
- Port EUnit tests to FsUnit or xUnit
- Test concurrent behaviors
- Performance testing and optimization

---

## See Also

- `lang-erlang-dev` - Erlang development patterns
- `lang-fsharp-dev` - F# development patterns
- `meta-convert-dev` - General conversion methodology
