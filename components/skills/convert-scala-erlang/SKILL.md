---
name: convert-scala-erlang
description: Convert Scala code to idiomatic Erlang. Use when migrating Scala projects to Erlang/OTP, translating JVM functional patterns to BEAM/OTP patterns, or refactoring Scala codebases to leverage Erlang's fault-tolerance and distribution. Extends meta-convert-dev with Scala-to-Erlang specific patterns.
---

# Convert Scala to Erlang

Convert Scala code to idiomatic Erlang. This skill extends `meta-convert-dev` with Scala-to-Erlang specific type mappings, idiom translations, and tooling for migrating functional JVM code to the BEAM VM and OTP framework.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Scala types → Erlang types and records
- **Idiom translations**: Scala patterns → idiomatic Erlang/OTP
- **Error handling**: Scala Either/Try/Option → Erlang tuples and let-it-crash
- **Concurrency patterns**: Scala Future/Akka → Erlang processes and OTP behaviors
- **Platform migration**: JVM → BEAM VM and OTP
- **Memory model shift**: JVM shared heap → BEAM per-process heaps

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Scala language fundamentals - see `lang-scala-dev`
- Erlang language fundamentals - see `lang-erlang-dev`
- Reverse conversion (Erlang → Scala) - see `convert-erlang-scala`

---

## Quick Reference

| Scala | Erlang | Notes |
|-------|--------|-------|
| `String` | `binary()` / `list()` | UTF-8 binary or char list |
| `Int` | `integer()` | Arbitrary precision in Erlang |
| `Long` | `integer()` | Same as Int in Erlang |
| `Double` | `float()` | IEEE 754 double |
| `Boolean` | `true` / `false` | Atoms |
| `Option[T]` | `{ok, Value} \| error` | Tagged tuple |
| `Some(x)` | `{ok, X}` | Success tuple |
| `None` | `error` / `undefined` | Absence |
| `Either[L,R]` | `{ok, Value} \| {error, Reason}` | Tagged tuple |
| `Right(x)` | `{ok, X}` | Success |
| `Left(e)` | `{error, Reason}` | Error |
| `Try[T]` | `{ok, Value} \| {error, Reason}` | Exception handling |
| `List[T]` | `list()` | Linked list |
| `Vector[T]` | `list()` / `array()` | List or array module |
| `Array[T]` | `tuple()` / `array()` | Fixed-size tuple or array |
| `Map[K,V]` | `#{K => V}` / `maps:map()` | Map literal or maps module |
| `Set[T]` | `sets:set()` / `ordsets` | Sets module |
| `case class` | `-record(name, {...})` | Record definition |
| `sealed trait` | Tagged tuples | Discriminated union |
| `Future[T]` | `pid()` / `gen_server` | Lightweight process |
| `object` | `-module(name).` | Singleton as module |

## When Converting Code

1. **Analyze source thoroughly** before writing target
2. **Map types first** - create type equivalence table
3. **Preserve semantics** over syntax similarity
4. **Adopt Erlang/OTP idioms** - don't write "Scala code in Erlang syntax"
5. **Embrace let-it-crash** - replace defensive programming with supervision
6. **Handle edge cases** - null safety, error paths, process lifecycle
7. **Test equivalence** - same inputs → same outputs

---

## Type System Mapping

### Primitive Types

| Scala | Erlang | Notes |
|-------|--------|-------|
| `String` | `binary()` | UTF-8 binary (most common): `<<"Hello">>` |
| `String` | `string()` | Character list (for compatibility): `"Hello"` |
| `Int` | `integer()` | 32-bit in Scala, arbitrary precision in Erlang |
| `Long` | `integer()` | 64-bit in Scala, arbitrary precision in Erlang |
| `Short` | `integer()` | 16-bit in Scala, arbitrary precision in Erlang |
| `Byte` | `integer()` | 8-bit in Scala, 0-255 in Erlang |
| `Double` | `float()` | IEEE 754 double precision |
| `Float` | `float()` | IEEE 754 single in Scala, double in Erlang |
| `Boolean` | `true` / `false` | Atoms (lowercase) |
| `Char` | `integer()` | Unicode codepoint |
| `Unit` | `ok` | Atom representing success |
| `Any` | `any()` / `term()` | Any Erlang term |
| `Nothing` | N/A | Bottom type, no Erlang equivalent |

### Option and Either Types

| Scala | Erlang | Notes |
|-------|--------|-------|
| `None` | `undefined` / `error` | Atom for absence |
| `Some(x)` | `{ok, X}` | Tagged tuple for presence |
| `Option[T]` | `{ok, Value} \| error \| undefined` | Common pattern |
| `Right(x)` | `{ok, X}` | Success tuple |
| `Left(e)` | `{error, Reason}` | Error tuple with reason |
| `Either[L,R]` | `{ok, Value} \| {error, Reason}` | Standard error pattern |
| `Success(x)` | `{ok, X}` | Try success |
| `Failure(e)` | `{error, Reason}` | Try failure |
| `Try[T]` | `{ok, Value} \| {error, Reason}` | Exception handling |

### Collection Types

| Scala | Erlang | Notes |
|-------|--------|-------|
| `List[T]` | `list()` | Linked list: `[1, 2, 3]` |
| `Vector[T]` | `list()` | No direct equivalent, use list |
| `Array[T]` | `tuple()` | Fixed-size: `{1, 2, 3}` |
| `Array[T]` | `array:array()` | Mutable array module |
| `Seq[T]` | `list()` | Generic sequence → list |
| `LazyList[T]` | Process-based stream | Stream via gen_server |
| `Map[K,V]` | `#{K => V}` | Map literal (Erlang 17+) |
| `Map[K,V]` | `dict:dict()` | Legacy dict module |
| `Set[T]` | `sets:set()` | Unordered set |
| `Set[T]` | `ordsets:ordset()` | Ordered set (list-based) |
| `(A, B)` (tuple) | `{A, B}` | Tuple literal |
| `(A, B, C)` | `{A, B, C}` | N-tuple |
| `Range` | `lists:seq(Start, End)` | Sequence generation |

### Case Classes and Sealed Traits

| Scala | Erlang | Notes |
|-------|--------|-------|
| `case class Person(name: String, age: Int)` | `-record(person, {name :: binary(), age :: integer()}).` | Record definition |
| `Person("Alice", 30)` | `#person{name = <<"Alice">>, age = 30}` | Record creation |
| `person.name` | `Person#person.name` | Field access |
| `person.copy(age = 31)` | `Person#person{age = 31}` | Record update |
| `sealed trait Shape` | Tagged tuples | Discriminated union |
| `case class Circle(r: Double) extends Shape` | `{circle, Radius}` | Tagged tuple variant |
| `case class Rectangle(w: Double, h: Double) extends Shape` | `{rectangle, Width, Height}` | Tagged tuple variant |
| `case object Empty extends Shape` | `empty` | Atom for singleton |

### Function Types

| Scala | Erlang | Notes |
|-------|--------|-------|
| `A => B` | `fun((A) -> B)` | Anonymous function |
| `(A, B) => C` | `fun((A, B) -> C)` | Multi-param function |
| `A => B => C` | `fun((A) -> fun((B) -> C) end end)` | Curried (uncommon in Erlang) |
| `Function1[A,B]` | `fun((A) -> B)` | Function type |
| `() => A` | `fun(() -> A)` | Nullary function |
| `A => Unit` | `fun((A) -> ok)` | Side-effect function |

### Generic Types

| Scala | Erlang | Notes |
|-------|--------|-------|
| `[T]` | `term()` | Any type (runtime polymorphism) |
| `List[T]` | `list(T)` | Parameterized type spec |
| `Option[T]` | `{ok, T} \| error` | Type spec pattern |
| `Either[L,R]` | `{ok, R} \| {error, L}` | Type spec pattern |
| Type bound `T <: Upper` | Guard clause | `when is_record(X, name)` |
| Type bound `T >: Lower` | N/A | No lower bounds in Erlang |

---

## Idiom Translation

### Pattern 1: Option Handling

**Scala:**
```scala
def findUser(id: String): Option[User] =
  users.find(_.id == id)

val name = findUser("123")
  .map(_.name)
  .getOrElse("Unknown")
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
- Scala's `Option.map` becomes pattern matching in Erlang
- `getOrElse` becomes the error clause in case expression
- Erlang uses `{ok, Value}` | `error` tuples instead of `Some`/`None`
- Type specs replace Scala type annotations

### Pattern 2: Either-Based Error Handling

**Scala:**
```scala
sealed trait Error
case object DivisionByZero extends Error
case class InvalidInput(msg: String) extends Error

def divide(x: Double, y: Double): Either[Error, Double] =
  if (y == 0.0) Left(DivisionByZero)
  else Right(x / y)

val result = for {
  a <- divide(10.0, 2.0)
  b <- divide(20.0, 4.0)
  c <- divide(a, b)
} yield c
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
- Scala for-comprehensions become nested case statements
- `Either[L,R]` maps to `{ok, Value} | {error, Reason}` tuples
- Sealed traits become atoms or tagged tuples
- Pattern matching on error tuples replaces monadic bind

### Pattern 3: List Processing

**Scala:**
```scala
val result = items
  .filter(_.active)
  .map(_.value)
  .sum
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
- Scala method chaining becomes list comprehension or nested function calls
- List comprehension is more idiomatic for filter+map in Erlang
- `lists:sum/1` directly replaces `.sum`
- Both approaches are valid; comprehension is more concise

### Pattern 4: Case Class Pattern Matching

**Scala:**
```scala
case class Person(firstName: String, lastName: String, age: Int)

def getFullName(person: Person): String = person match {
  case Person(first, last, _) => s"$first $last"
}

def isAdult(person: Person): Boolean = person match {
  case Person(_, _, age) if age >= 18 => true
  case _ => false
}
```

**Erlang:**
```erlang
-record(person, {
    first_name :: binary(),
    last_name :: binary(),
    age :: integer()
}).

get_full_name(#person{first_name = First, last_name = Last}) ->
    <<First/binary, " ", Last/binary>>.

is_adult(#person{age = Age}) when Age >= 18 ->
    true;
is_adult(_) ->
    false.
```

**Why this translation:**
- Scala case class patterns map to Erlang record patterns
- Guards (`when`) work similarly in both languages
- Scala string interpolation becomes binary concatenation
- Function clauses with pattern matching replace match expressions

### Pattern 5: Sealed Trait / ADT

**Scala:**
```scala
sealed trait Result[+T]
case class Success[T](value: T) extends Result[T]
case class Failure(error: String) extends Result[Nothing]
case object Pending extends Result[Nothing]

def process[T](result: Result[T]): String = result match {
  case Success(value) => s"Got: $value"
  case Failure(error) => s"Error: $error"
  case Pending => "Still waiting..."
}
```

**Erlang:**
```erlang
-type result(T) :: {success, T} | {failure, binary()} | pending.

-spec process(result(term())) -> binary().
process({success, Value}) ->
    iolist_to_binary(io_lib:format("Got: ~p", [Value]));
process({failure, Error}) ->
    <<"Error: ", Error/binary>>;
process(pending) ->
    <<"Still waiting...">>.
```

**Why this translation:**
- Sealed traits become tagged tuples or atoms
- Case objects become atoms
- Pattern matching translates directly
- Type parameters in Scala become type variables in specs

### Pattern 6: Singleton Object

**Scala:**
```scala
object MathUtils {
  val PI = 3.14159

  def square(x: Int): Int = x * x

  def cube(x: Int): Int = x * x * x
}

// Usage
val result = MathUtils.square(5)
```

**Erlang:**
```erlang
-module(math_utils).
-export([square/1, cube/1]).

-define(PI, 3.14159).

square(X) -> X * X.

cube(X) -> X * X * X.

% Usage
Result = math_utils:square(5).
```

**Why this translation:**
- Scala objects become Erlang modules
- Public methods become exported functions
- Constants become macros or module attributes
- Fully qualified calls use module:function syntax

---

## Paradigm Translation

### Mental Model Shift: JVM → BEAM

| Scala Concept | Erlang Approach | Key Insight |
|---------------|-----------------|-------------|
| Shared mutable state | Isolated process state | Each process has private memory |
| Class with methods | Record + module functions | Data and behavior separated |
| Inheritance | Protocol implementation | Favor behaviors over hierarchies |
| Thread pool | Lightweight processes | Millions of processes, not threads |
| Synchronized blocks | Message passing | No shared memory, communicate via messages |
| Exception handling | Let-it-crash + supervision | Failures are isolated and handled by supervisors |
| Static typing | Dynamic with dialyzer | Runtime flexibility with static analysis |

### Concurrency Mental Model

| Scala Pattern | Erlang Pattern | Conceptual Translation |
|---------------|----------------|------------------------|
| `Future[T]` | `spawn/1` + message passing | Async computation → lightweight process |
| `Promise[T]` | Process mailbox | Future completion → message receipt |
| `Await.result` | `receive ... end` | Blocking wait → selective receive |
| Akka Actor | `gen_server` behavior | Stateful actor → OTP behavior |
| Akka `receive` | `handle_call/handle_cast` | Message handling → callback functions |
| Akka Supervisor | OTP `supervisor` | Fault tolerance → supervision tree |
| `ExecutionContext` | Scheduler | Thread pool → BEAM scheduler |
| Thread-safe collections | Process dictionary / ETS | Shared state → process-local or ETS |

---

## Error Handling

### Scala Try/Either → Erlang Tuples and Let-it-Crash

**Scala defensive style:**
```scala
def parseAndProcess(input: String): Try[Int] = Try {
  val num = input.toInt
  if (num < 0) throw new IllegalArgumentException("Negative")
  num * 2
}

val result = parseAndProcess("42") match {
  case Success(value) => println(s"Result: $value")
  case Failure(ex) => println(s"Error: ${ex.getMessage}")
}
```

**Erlang let-it-crash style:**
```erlang
-spec parse_and_process(binary()) -> integer().
parse_and_process(Input) ->
    Num = binary_to_integer(Input),
    true = Num >= 0,  % Crashes if false
    Num * 2.

% Caller can catch or let supervisor handle
-spec safe_parse_and_process(binary()) -> {ok, integer()} | {error, term()}.
safe_parse_and_process(Input) ->
    try
        {ok, parse_and_process(Input)}
    catch
        _:Reason -> {error, Reason}
    end.
```

**Why this translation:**
- Erlang prefers crashing over defensive checks
- Supervisors restart failed processes
- Use `{ok, Value} | {error, Reason}` for expected errors
- Let unexpected errors crash for debugging clarity

### Error Propagation Patterns

| Scala Pattern | Erlang Pattern | Notes |
|---------------|----------------|-------|
| `Try { ... }` | `try ... catch` | Exception handling |
| `.recover { case ... }` | `catch` clauses | Error recovery |
| `Either.flatMap` | Nested `case` | Error propagation |
| Throwing exceptions | `throw/exit/error` | Rare in idiomatic Erlang |
| Custom exception classes | Atoms or tuples | Error reasons as atoms |
| Stack trace capture | `erlang:get_stacktrace()` | For debugging |

---

## Concurrency Patterns

### Scala Future → Erlang Process

**Scala:**
```scala
import scala.concurrent.{Future, ExecutionContext}
import ExecutionContext.Implicits.global

def fetchData(id: String): Future[Data] = Future {
  // Simulate async operation
  Thread.sleep(1000)
  Data(id, "result")
}

val result = for {
  data1 <- fetchData("1")
  data2 <- fetchData("2")
} yield combine(data1, data2)

result.onComplete {
  case Success(combined) => println(combined)
  case Failure(ex) => println(s"Error: $ex")
}
```

**Erlang:**
```erlang
-spec fetch_data(binary()) -> data().
fetch_data(Id) ->
    timer:sleep(1000),
    #{id => Id, result => <<"result">>}.

-spec async_fetch() -> pid().
async_fetch() ->
    Parent = self(),
    spawn(fun() ->
        Data1 = fetch_data(<<"1">>),
        Data2 = fetch_data(<<"2">>),
        Combined = combine(Data1, Data2),
        Parent ! {result, Combined}
    end).

% Usage
Pid = async_fetch(),
receive
    {result, Combined} -> io:format("~p~n", [Combined])
after 5000 ->
    io:format("Timeout~n")
end.
```

**Why this translation:**
- Futures become spawned processes
- `onComplete` becomes `receive` pattern matching
- Sequential async (for-comprehension) becomes sequential process code
- Timeout handling is explicit in Erlang

### Akka Actor → gen_server

**Scala (Akka):**
```scala
import akka.actor.{Actor, ActorRef, Props}

case class Get(key: String)
case class Put(key: String, value: String)

class KeyValueStore extends Actor {
  private var store = Map.empty[String, String]

  def receive: Receive = {
    case Get(key) =>
      sender() ! store.get(key)

    case Put(key, value) =>
      store = store + (key -> value)
      sender() ! "OK"
  }
}

// Usage
val store = system.actorOf(Props[KeyValueStore])
store ! Put("name", "Alice")
store ! Get("name")
```

**Erlang (gen_server):**
```erlang
-module(kv_store).
-behaviour(gen_server).

-export([start_link/0, get/1, put/2]).
-export([init/1, handle_call/3, handle_cast/2, terminate/2, code_change/3]).

-record(state, {store = #{} :: map()}).

%% API
start_link() ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [], []).

get(Key) ->
    gen_server:call(?MODULE, {get, Key}).

put(Key, Value) ->
    gen_server:call(?MODULE, {put, Key, Value}).

%% Callbacks
init([]) ->
    {ok, #state{}}.

handle_call({get, Key}, _From, State = #state{store = Store}) ->
    Result = maps:get(Key, Store, undefined),
    {reply, Result, State};

handle_call({put, Key, Value}, _From, State = #state{store = Store}) ->
    NewStore = Store#{Key => Value},
    {reply, ok, State#state{store = NewStore}}.

handle_cast(_Msg, State) ->
    {noreply, State}.

terminate(_Reason, _State) ->
    ok.

code_change(_OldVsn, State, _Extra) ->
    {ok, State}.
```

**Why this translation:**
- Akka actors map to gen_server behaviors
- `receive` block becomes `handle_call/handle_cast` callbacks
- `sender()` is implicit in gen_server's `From` parameter
- State management is explicit in callback return tuples
- OTP provides more structure than raw Akka actors

---

## Module and Package Structure

### Scala Package → Erlang Module

**Scala:**
```scala
package com.example.myapp

object UserService {
  def createUser(name: String): User = ???
  def deleteUser(id: Int): Unit = ???
}
```

**Erlang:**
```erlang
-module(user_service).
-export([create_user/1, delete_user/1]).

create_user(Name) ->
    % implementation
    ok.

delete_user(Id) ->
    % implementation
    ok.
```

**Translation notes:**
- Scala packages become application structure (apps/src directories)
- Scala objects become modules
- Package imports become module calls
- No nested modules in Erlang (flat namespace)

---

## Common Pitfalls

1. **Overusing exceptions**: Erlang prefers let-it-crash for unexpected errors and `{ok, Value} | {error, Reason}` for expected errors. Don't translate every `Try` to `try...catch`.

2. **Shared mutable state**: Scala's `var` and mutable collections don't translate directly. Use process state or ETS tables instead.

3. **Type erasure issues**: Scala's generic types are erased at runtime. Erlang is dynamically typed, but Dialyzer type specs help catch errors.

4. **Numeric precision**: Scala's `Int` is 32-bit, but Erlang's `integer()` is arbitrary precision. Document overflow assumptions.

5. **String encoding**: Scala strings are UTF-16; Erlang binaries are UTF-8. Use `<<"binary">>` syntax for UTF-8 strings.

6. **Null handling**: Scala has `null` (avoid it), `None`, and `Option`. Erlang uses `undefined`, `error`, or `{ok, Value}`. Be consistent.

7. **Currying**: Scala's curried functions are uncommon in Erlang. Flatten to multi-argument functions.

8. **Implicits**: Scala's implicit parameters and conversions have no Erlang equivalent. Make dependencies explicit.

9. **Case object equality**: Scala case objects use reference equality. Erlang atoms use value equality.

10. **Pattern match exhaustiveness**: Scala's compiler checks exhaustiveness; Erlang/Dialyzer warns but doesn't enforce. Add catch-all clauses.

---

## Limitations

### Coverage Gaps

| Pillar | Scala Skill | Erlang Skill | Mitigation |
|--------|-------------|--------------|------------|
| Module | ~ | ✓ | Scala packages explained in context |
| Error | ✓ | ✓ | Full coverage |
| Concurrency | ✓ | ✓ | Full coverage |
| Metaprogramming | ~ | ✓ | Scala macros mentioned where relevant |
| Zero/Default | ~ | ✓ | Option/None covered in idioms |
| Serialization | ~ | ✓ | Refer to `patterns-serialization-dev` |
| Build | ✓ | ✓ | Full coverage |
| Testing | ✓ | ✓ | Full coverage |

**Combined Score:** 13.5/16 (Good - proceed with pattern skill references)

### Known Limitations

1. **Serialization**: This skill has limited guidance on JSON/serialization libraries because lang-scala-dev lacks dedicated serialization coverage. Refer to `patterns-serialization-dev` for JSON handling patterns.

2. **Metaprogramming**: Scala macros and compile-time metaprogramming have limited coverage. Erlang macros and parse transforms are covered in lang-erlang-dev.

3. **Module systems**: Scala's package objects and imports are not fully covered. Module structure patterns are provided in context.

### External Resources Used

| Resource | What It Provided | Reliability |
|----------|------------------|-------------|
| Scala official docs | Type system, collections API | High |
| Erlang official docs | OTP behaviors, gen_server patterns | High |
| lang-scala-dev skill | Scala fundamentals, concurrency | High |
| lang-erlang-dev skill | Erlang patterns, OTP | High |
| convert-erlang-scala | Reverse conversion insights | High |

---

## Tooling

| Tool | Purpose | Notes |
|------|---------|-------|
| **rebar3** | Erlang build tool | Successor to rebar, standard for modern Erlang |
| **Dialyzer** | Static analysis | Catches type errors despite dynamic typing |
| **EUnit** | Unit testing | Built-in test framework |
| **Common Test** | Integration testing | OTP's comprehensive test framework |
| **Observer** | Live system inspection | GUI for monitoring processes, ETS, applications |
| **Recon** | Production debugging | Runtime inspection and debugging |
| **PropEr** | Property-based testing | QuickCheck-like testing for Erlang |
| **Elvis** | Style checker | Erlang linter and style enforcer |
| **Relx** | Release building | Creates production releases |
| **Hex** | Package manager | Erlang/Elixir package registry |

**No direct transpilers exist** from Scala to Erlang. Manual conversion is required.

---

## Examples

### Example 1: Simple - Type and Function Translation

**Before (Scala):**
```scala
case class Point(x: Double, y: Double)

def distance(p1: Point, p2: Point): Double = {
  val dx = p2.x - p1.x
  val dy = p2.y - p1.y
  Math.sqrt(dx * dx + dy * dy)
}

val origin = Point(0.0, 0.0)
val point = Point(3.0, 4.0)
val dist = distance(origin, point)  // 5.0
```

**After (Erlang):**
```erlang
-module(geometry).
-export([distance/2]).

-record(point, {x :: float(), y :: float()}).

distance(P1, P2) ->
    Dx = P2#point.x - P1#point.x,
    Dy = P2#point.y - P1#point.y,
    math:sqrt(Dx * Dx + Dy * Dy).

% Usage
Origin = #point{x = 0.0, y = 0.0},
Point = #point{x = 3.0, y = 4.0},
Dist = distance(Origin, Point).  % 5.0
```

### Example 2: Medium - Option and Error Handling

**Before (Scala):**
```scala
sealed trait ValidationError
case class InvalidEmail(email: String) extends ValidationError
case class UserNotFound(id: Int) extends ValidationError

case class User(id: Int, name: String, email: String)

def validateEmail(email: String): Either[ValidationError, String] =
  if (email.contains("@")) Right(email)
  else Left(InvalidEmail(email))

def findUser(id: Int): Option[User] =
  // Simulated database lookup
  if (id == 1) Some(User(1, "Alice", "alice@example.com"))
  else None

def getUserEmail(id: Int): Either[ValidationError, String] = {
  for {
    user <- findUser(id).toRight(UserNotFound(id))
    validEmail <- validateEmail(user.email)
  } yield validEmail
}

// Usage
getUserEmail(1) match {
  case Right(email) => println(s"Email: $email")
  case Left(InvalidEmail(e)) => println(s"Invalid email: $e")
  case Left(UserNotFound(id)) => println(s"User $id not found")
}
```

**After (Erlang):**
```erlang
-module(user_validator).
-export([get_user_email/1]).

-record(user, {id :: integer(), name :: binary(), email :: binary()}).

-type validation_error() ::
    {invalid_email, binary()} |
    {user_not_found, integer()}.

-spec validate_email(binary()) -> {ok, binary()} | {error, validation_error()}.
validate_email(Email) ->
    case binary:match(Email, <<"@">>) of
        {_, _} -> {ok, Email};
        nomatch -> {error, {invalid_email, Email}}
    end.

-spec find_user(integer()) -> {ok, user()} | error.
find_user(1) ->
    {ok, #user{id = 1, name = <<"Alice">>, email = <<"alice@example.com">>}};
find_user(_) ->
    error.

-spec get_user_email(integer()) -> {ok, binary()} | {error, validation_error()}.
get_user_email(Id) ->
    case find_user(Id) of
        {ok, User} ->
            validate_email(User#user.email);
        error ->
            {error, {user_not_found, Id}}
    end.

% Usage
case get_user_email(1) of
    {ok, Email} ->
        io:format("Email: ~s~n", [Email]);
    {error, {invalid_email, E}} ->
        io:format("Invalid email: ~s~n", [E]);
    {error, {user_not_found, Id}} ->
        io:format("User ~p not found~n", [Id])
end.
```

### Example 3: Complex - Actor/Process with State Management

**Before (Scala with Akka):**
```scala
import akka.actor.{Actor, ActorRef, Props}
import scala.collection.mutable

case class Subscribe(topic: String, subscriber: ActorRef)
case class Unsubscribe(topic: String, subscriber: ActorRef)
case class Publish(topic: String, message: String)
case class GetSubscribers(topic: String)

class PubSubBroker extends Actor {
  private val subscriptions = mutable.Map.empty[String, Set[ActorRef]]

  def receive: Receive = {
    case Subscribe(topic, subscriber) =>
      val current = subscriptions.getOrElse(topic, Set.empty)
      subscriptions(topic) = current + subscriber
      sender() ! "Subscribed"

    case Unsubscribe(topic, subscriber) =>
      subscriptions.get(topic).foreach { subs =>
        subscriptions(topic) = subs - subscriber
      }
      sender() ! "Unsubscribed"

    case Publish(topic, message) =>
      subscriptions.get(topic).foreach { subscribers =>
        subscribers.foreach(_ ! message)
      }
      sender() ! "Published"

    case GetSubscribers(topic) =>
      val subs = subscriptions.getOrElse(topic, Set.empty)
      sender() ! subs.size
  }
}

// Usage
val broker = system.actorOf(Props[PubSubBroker], "broker")
broker ! Subscribe("news", subscriberActor)
broker ! Publish("news", "Breaking news!")
```

**After (Erlang with gen_server):**
```erlang
-module(pubsub_broker).
-behaviour(gen_server).

-export([start_link/0, subscribe/2, unsubscribe/2, publish/2, get_subscribers/1]).
-export([init/1, handle_call/3, handle_cast/2, terminate/2, code_change/3]).

-record(state, {
    subscriptions = #{} :: #{binary() => [pid()]}
}).

%% API
start_link() ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [], []).

subscribe(Topic, Subscriber) ->
    gen_server:call(?MODULE, {subscribe, Topic, Subscriber}).

unsubscribe(Topic, Subscriber) ->
    gen_server:call(?MODULE, {unsubscribe, Topic, Subscriber}).

publish(Topic, Message) ->
    gen_server:cast(?MODULE, {publish, Topic, Message}).

get_subscribers(Topic) ->
    gen_server:call(?MODULE, {get_subscribers, Topic}).

%% Callbacks
init([]) ->
    {ok, #state{}}.

handle_call({subscribe, Topic, Subscriber}, _From, State = #state{subscriptions = Subs}) ->
    Current = maps:get(Topic, Subs, []),
    NewSubs = case lists:member(Subscriber, Current) of
        true -> Subs;
        false -> Subs#{Topic => [Subscriber | Current]}
    end,
    {reply, subscribed, State#state{subscriptions = NewSubs}};

handle_call({unsubscribe, Topic, Subscriber}, _From, State = #state{subscriptions = Subs}) ->
    NewSubs = case maps:get(Topic, Subs, []) of
        [] -> Subs;
        List ->
            Subs#{Topic => lists:delete(Subscriber, List)}
    end,
    {reply, unsubscribed, State#state{subscriptions = NewSubs}};

handle_call({get_subscribers, Topic}, _From, State = #state{subscriptions = Subs}) ->
    Count = length(maps:get(Topic, Subs, [])),
    {reply, Count, State}.

handle_cast({publish, Topic, Message}, State = #state{subscriptions = Subs}) ->
    Subscribers = maps:get(Topic, Subs, []),
    lists:foreach(fun(Sub) -> Sub ! {message, Topic, Message} end, Subscribers),
    {noreply, State}.

terminate(_Reason, _State) ->
    ok.

code_change(_OldVsn, State, _Extra) ->
    {ok, State}.

% Usage
{ok, _Pid} = pubsub_broker:start_link(),
pubsub_broker:subscribe(<<"news">>, self()),
pubsub_broker:publish(<<"news">>, <<"Breaking news!">>),
receive
    {message, <<"news">>, Msg} ->
        io:format("Received: ~s~n", [Msg])
after 5000 ->
    io:format("Timeout~n")
end.
```

**Key differences in this example:**
- Akka's mutable Map becomes immutable Map in gen_server state
- `sender()` is handled implicitly by gen_server's `From` parameter
- Fire-and-forget messages (`!`) map to `handle_cast`
- Request-reply messages map to `handle_call`
- Supervision and lifecycle are managed by OTP

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `convert-erlang-scala` - Reverse conversion (Erlang → Scala)
- `convert-fsharp-erlang` - Similar functional JVM → BEAM conversion
- `lang-scala-dev` - Scala development patterns
- `lang-erlang-dev` - Erlang development patterns

Cross-cutting pattern skills (for areas not fully covered by lang-*-dev):
- `patterns-concurrency-dev` - Async, channels, actors across languages
- `patterns-serialization-dev` - JSON, validation across languages
- `patterns-metaprogramming-dev` - Macros, compile-time code generation
