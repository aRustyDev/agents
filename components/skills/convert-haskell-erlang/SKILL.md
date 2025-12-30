---
name: convert-haskell-erlang
description: Convert Haskell code to idiomatic Erlang/OTP. Use when migrating Haskell projects to Erlang, translating pure functional patterns to fault-tolerant concurrent systems, or refactoring Haskell codebases into distributed Erlang applications. Extends meta-convert-dev with Haskell-to-Erlang specific patterns.
---

# Convert Haskell to Erlang

Convert Haskell code to idiomatic Erlang/OTP. This skill extends `meta-convert-dev` with Haskell-to-Erlang specific type mappings, idiom translations, and tooling for converting pure functional code to fault-tolerant distributed systems.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Haskell types → Erlang terms
- **Idiom translations**: Pure functions → Process-based patterns
- **Error handling**: Maybe/Either → ok/error tuples
- **Async patterns**: Monadic IO → Process message passing
- **Concurrency**: STM/Async → OTP behaviors and supervision
- **Evaluation**: Lazy → Eager evaluation strategies

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Haskell language fundamentals - see `lang-haskell-dev`
- Erlang language fundamentals - see `lang-erlang-dev`
- Reverse conversion (Erlang → Haskell) - see `convert-erlang-haskell`

---

## Quick Reference

| Haskell | Erlang | Notes |
|---------|--------|-------|
| `Int`, `Integer` | `integer()` | Arbitrary precision in both |
| `Float`, `Double` | `float()` | IEEE 754 floating point |
| `String` | `string()` / `binary()` | String is `[char()]`, prefer binaries |
| `[a]` | `[term()]` | Lists work similarly |
| `(a, b)` | `{A, B}` | Tuples preserve structure |
| `Maybe a` | `undefined \| A` or `{ok, A} \| error` | No Maybe, use atoms/tuples |
| `Either e a` | `{ok, A} \| {error, E}` | Standard Erlang convention |
| `data X = ...` | `-record(x, {...})` or `map()` | Records or maps |
| `class TypeClass` | `-behaviour(...)` | OTP behaviors |
| `IO a` | `fun() -> A` or process | Side effects via processes |
| `do` notation | Pattern matching + `case` | Sequential operations |
| `fmap`, `<$>` | `lists:map/2` | List transformations |
| `>>=` (bind) | Nested function calls | No monadic bind |
| `pure` / `return` | Direct value | No lifting needed |

## When Converting Code

1. **Analyze purity boundaries** - Identify pure vs effectful code
2. **Map types to Erlang terms** - Create type equivalence table
3. **Convert laziness to eagerness** - Evaluate strictly
4. **Replace monads with processes** - IO/State → gen_server
5. **Adopt Erlang idioms** - Don't write "Haskell code in Erlang syntax"
6. **Embrace failure** - Use supervision trees, not defensive code
7. **Test equivalence** - Same inputs → same outputs

---

## Type System Mapping

### Primitive Types

| Haskell | Erlang | Notes |
|---------|--------|-------|
| `Int` | `integer()` | Erlang integers are arbitrary precision |
| `Integer` | `integer()` | No distinction in Erlang |
| `Float` | `float()` | IEEE 754 double precision |
| `Double` | `float()` | No separate double type |
| `Char` | `char()` | Integer 0-1114111 (Unicode) |
| `Bool` | `boolean()` | `true` / `false` atoms |
| `()` (unit) | `ok` or `{}` | Often use `ok` atom |

### Collection Types

| Haskell | Erlang | Notes |
|---------|--------|-------|
| `[a]` | `[A]` | Lists are similar, but eager |
| `String` | `string()` | List of chars: `[char()]` |
| `Text` | `binary()` | Prefer UTF-8 binaries |
| `ByteString` | `binary()` | Direct mapping |
| `(a, b)` | `{A, B}` | Tuples |
| `(a, b, c)` | `{A, B, C}` | N-tuples supported |
| `Map k v` | `#{K => V}` | Erlang maps (17+) |
| `Set a` | `sets:set(A)` or `ordsets:ordset(A)` | Standard library modules |

### Composite Types

| Haskell | Erlang | Notes |
|---------|--------|-------|
| `data X = X { field :: Type }` | `-record(x, {field :: type()})` | Record syntax |
| `data X = X { field :: Type }` | `#{field => Type}` | Or use maps |
| `newtype UserId = UserId Int` | `integer()` or `-type user_id() :: integer()` | Type aliases only |
| `type Alias = Type` | `-type alias() :: type()` | Type aliases |
| `data X = A \| B` | Atoms or tagged tuples | Sum types |
| `data X = A Int \| B String` | `{a, integer()} \| {b, string()}` | Tagged unions |

### Function Types

| Haskell | Erlang | Notes |
|---------|--------|-------|
| `a -> b` | `fun((A) -> B)` | Single argument |
| `a -> b -> c` | `fun((A, B) -> C)` | Multiple arguments (uncurried) |
| `IO a` | `fun(() -> A)` | Thunk for lazy eval |
| `m a` (monad) | Process or explicit state | Use processes for effects |

### Monadic Types

| Haskell | Erlang | Notes |
|---------|--------|-------|
| `Maybe a` | `undefined \| A` | Or `{ok, A} \| error` |
| `Either e a` | `{ok, A} \| {error, E}` | Standard error convention |
| `IO a` | Side effects directly | No IO monad needed |
| `State s a` | gen_server state | Use OTP behavior |
| `Reader r a` | Pass as parameter | Or use process dictionary |
| `Writer w a` | Accumulate in state | Or send messages |

---

## Idiom Translation

### Pattern: Maybe to ok/error

**Haskell:**
```haskell
findUser :: UserId -> Maybe User
findUser uid = lookup uid users

getUserEmail :: UserId -> String
getUserEmail uid =
    case findUser uid of
        Just user -> email user
        Nothing -> "no-email@example.com"
```

**Erlang:**
```erlang
-spec find_user(user_id()) -> {ok, user()} | error.
find_user(UserId) ->
    case lists:keyfind(UserId, #user.id, users()) of
        false -> error;
        User -> {ok, User}
    end.

-spec get_user_email(user_id()) -> string().
get_user_email(UserId) ->
    case find_user(UserId) of
        {ok, User} -> User#user.email;
        error -> "no-email@example.com"
    end.
```

**Why this translation:**
- Erlang has no Maybe type, uses atoms and tuples instead
- `{ok, Value} | error` is the standard Erlang convention
- Pattern matching works similarly in both languages

### Pattern: Either to {ok, Value} | {error, Reason}

**Haskell:**
```haskell
validateAge :: Int -> Either String Int
validateAge age
    | age < 0 = Left "Age cannot be negative"
    | age > 150 = Left "Age too high"
    | otherwise = Right age

validateEmail :: String -> Either String String
validateEmail email
    | '@' `elem` email = Right email
    | otherwise = Left "Invalid email"

createUser :: Int -> String -> Either String User
createUser age email = do
    validAge <- validateAge age
    validEmail <- validateEmail email
    return $ User validEmail validAge
```

**Erlang:**
```erlang
-spec validate_age(integer()) -> {ok, integer()} | {error, string()}.
validate_age(Age) when Age < 0 ->
    {error, "Age cannot be negative"};
validate_age(Age) when Age > 150 ->
    {error, "Age too high"};
validate_age(Age) ->
    {ok, Age}.

-spec validate_email(string()) -> {ok, string()} | {error, string()}.
validate_email(Email) ->
    case lists:member($@, Email) of
        true -> {ok, Email};
        false -> {error, "Invalid email"}
    end.

-spec create_user(integer(), string()) -> {ok, user()} | {error, string()}.
create_user(Age, Email) ->
    case validate_age(Age) of
        {ok, ValidAge} ->
            case validate_email(Email) of
                {ok, ValidEmail} ->
                    {ok, #user{email = ValidEmail, age = ValidAge}};
                {error, Reason} ->
                    {error, Reason}
            end;
        {error, Reason} ->
            {error, Reason}
    end.
```

**Why this translation:**
- Either maps naturally to `{ok, Value} | {error, Reason}`
- Monadic do-notation becomes nested case statements
- Early returns via pattern matching replace bind operator

### Pattern: List Comprehensions

**Haskell:**
```haskell
-- Filter and map
evenSquares :: [Int] -> [Int]
evenSquares xs = [x^2 | x <- xs, even x]

-- Cartesian product
pairs :: [a] -> [b] -> [(a, b)]
pairs xs ys = [(x, y) | x <- xs, y <- ys]

-- Nested with guards
pythagoras :: Int -> [(Int, Int, Int)]
pythagoras n = [(a, b, c) | a <- [1..n],
                             b <- [a..n],
                             c <- [b..n],
                             a^2 + b^2 == c^2]
```

**Erlang:**
```erlang
%% Filter and map
-spec even_squares([integer()]) -> [integer()].
even_squares(Xs) ->
    [X * X || X <- Xs, X rem 2 =:= 0].

%% Cartesian product
-spec pairs([A], [B]) -> [{A, B}].
pairs(Xs, Ys) ->
    [{X, Y} || X <- Xs, Y <- Ys].

%% Nested with guards
-spec pythagoras(integer()) -> [{integer(), integer(), integer()}].
pythagoras(N) ->
    [{A, B, C} || A <- lists:seq(1, N),
                   B <- lists:seq(A, N),
                   C <- lists:seq(B, N),
                   A * A + B * B =:= C * C].
```

**Why this translation:**
- List comprehensions translate almost directly
- Guards work similarly in both languages
- Syntax is nearly identical

### Pattern: Recursive Functions

**Haskell:**
```haskell
factorial :: Integer -> Integer
factorial 0 = 1
factorial n = n * factorial (n - 1)

sum' :: [Int] -> Int
sum' [] = 0
sum' (x:xs) = x + sum' xs

map' :: (a -> b) -> [a] -> [b]
map' _ [] = []
map' f (x:xs) = f x : map' f xs
```

**Erlang:**
```erlang
-spec factorial(integer()) -> integer().
factorial(0) -> 1;
factorial(N) when N > 0 -> N * factorial(N - 1).

-spec sum([integer()]) -> integer().
sum([]) -> 0;
sum([X|Xs]) -> X + sum(Xs).

-spec map(fun((A) -> B), [A]) -> [B].
map(_, []) -> [];
map(F, [X|Xs]) -> [F(X) | map(F, Xs)].
```

**Why this translation:**
- Pattern matching translates directly
- Recursion works identically
- Guards provide additional safety in Erlang

### Pattern: Higher-Order Functions

**Haskell:**
```haskell
processItems :: [Item] -> [Result]
processItems items =
    items
    & filter isValid
    & map transform
    & map enrich
    & filter isComplete

-- Function composition
addThenDouble :: Int -> Int
addThenDouble = (*2) . (+1)

-- Partial application
add5 :: Int -> Int
add5 = (+5)
```

**Erlang:**
```erlang
-spec process_items([item()]) -> [result()].
process_items(Items) ->
    lists:filter(fun is_complete/1,
        lists:map(fun enrich/1,
            lists:map(fun transform/1,
                lists:filter(fun is_valid/1, Items)))).

%% Or with pipes (shell syntax, not in modules)
%% Items
%%   |> lists:filter(fun is_valid/1)
%%   |> lists:map(fun transform/1)
%%   |> lists:map(fun enrich/1)
%%   |> lists:filter(fun is_complete/1).

%% Function composition - manual
-spec add_then_double(integer()) -> integer().
add_then_double(X) -> (X + 1) * 2.

%% Partial application - use fun wrapper
-spec add5(integer()) -> integer().
add5(X) -> X + 5.

%% Or return a fun
make_adder(N) -> fun(X) -> X + N end.
```

**Why this translation:**
- Erlang doesn't have built-in composition operators
- Functions are not curried by default
- Use nested calls or explicit intermediate variables
- Partial application requires wrapping in `fun`

---

## Error Handling

### Haskell Error Model → Erlang Error Model

| Haskell Pattern | Erlang Pattern | Use Case |
|----------------|----------------|----------|
| `Maybe a` | `{ok, A} \| error` | Simple success/failure |
| `Maybe a` | `undefined \| A` | Nullable values |
| `Either String a` | `{ok, A} \| {error, Reason}` | Errors with context |
| Pure exception (error) | `erlang:error(Reason)` | Unrecoverable errors |
| `MonadError` | Process exit/crash | Let it crash philosophy |

### Exception Handling

**Haskell:**
```haskell
-- Throwing errors
safeDivide :: Float -> Float -> Either String Float
safeDivide _ 0 = Left "division by zero"
safeDivide x y = Right (x / y)

-- Catching exceptions
parseConfig :: FilePath -> IO (Either String Config)
parseConfig path = do
    contents <- readFile path
    return $ case decode contents of
        Just config -> Right config
        Nothing -> Left "Failed to parse config"
```

**Erlang:**
```erlang
%% Returning errors
-spec safe_divide(float(), float()) -> {ok, float()} | {error, string()}.
safe_divide(_, 0.0) ->
    {error, "division by zero"};
safe_divide(X, Y) ->
    {ok, X / Y}.

%% Try-catch for external calls
-spec parse_config(file:filename()) -> {ok, config()} | {error, term()}.
parse_config(Path) ->
    try
        {ok, Contents} = file:read_file(Path),
        case jsone:decode(Contents) of
            Config -> {ok, Config}
        end
    catch
        error:Reason -> {error, Reason}
    end.
```

### Let It Crash vs Defensive Programming

**Haskell (defensive):**
```haskell
processUser :: UserId -> IO (Either String Result)
processUser uid = do
    userResult <- fetchUser uid
    case userResult of
        Left err -> return $ Left err
        Right user -> do
            validationResult <- validateUser user
            case validationResult of
                Left err -> return $ Left err
                Right validUser -> do
                    saveResult <- saveUser validUser
                    case saveResult of
                        Left err -> return $ Left err
                        Right result -> return $ Right result
```

**Erlang (let it crash):**
```erlang
%% Under supervisor, just crash on error
-spec process_user(user_id()) -> result().
process_user(UserId) ->
    User = fetch_user(UserId),        % Crash if not found
    ValidUser = validate_user(User),  % Crash if invalid
    save_user(ValidUser).             % Crash if save fails

%% Supervisor handles restart
-spec init([]) -> {ok, {supervisor:sup_flags(), [supervisor:child_spec()]}}.
init([]) ->
    SupFlags = #{
        strategy => one_for_one,
        intensity => 5,
        period => 60
    },
    ChildSpecs = [#{
        id => user_processor,
        start => {user_processor, start_link, []},
        restart => permanent,
        shutdown => 5000,
        type => worker
    }],
    {ok, {SupFlags, ChildSpecs}}.
```

**Why this translation:**
- Erlang embraces failure with supervision trees
- Don't handle every error - let supervisors restart failed processes
- Reserve error tuples for expected failures

---

## Concurrency Patterns

### IO Monad → Processes

**Haskell:**
```haskell
-- Sequential IO operations
main :: IO ()
main = do
    putStrLn "Enter your name:"
    name <- getLine
    putStrLn $ "Hello, " ++ name

-- Concurrent operations with Async
import Control.Concurrent.Async

fetchData :: IO ()
fetchData = do
    (users, orders) <- concurrently fetchUsers fetchOrders
    processData users orders
```

**Erlang:**
```erlang
%% Sequential operations (no special monad needed)
main() ->
    io:format("Enter your name:~n"),
    {ok, [Name]} = io:fread("", "~s"),
    io:format("Hello, ~s~n", [Name]).

%% Concurrent operations with processes
fetch_data() ->
    Parent = self(),
    spawn(fun() -> Parent ! {users, fetch_users()} end),
    spawn(fun() -> Parent ! {orders, fetch_orders()} end),

    Users = receive {users, U} -> U end,
    Orders = receive {orders, O} -> O end,

    process_data(Users, Orders).
```

### State Monad → gen_server

**Haskell:**
```haskell
import Control.Monad.State

type Counter a = State Int a

increment :: Counter ()
increment = modify (+1)

getCount :: Counter Int
getCount = get

program :: Counter Int
program = do
    increment
    increment
    increment
    getCount

main :: IO ()
main = print $ evalState program 0  -- Prints 3
```

**Erlang:**
```erlang
-module(counter).
-behaviour(gen_server).

%% API
-export([start_link/0, increment/0, get_count/0]).

%% gen_server callbacks
-export([init/1, handle_call/3, handle_cast/2]).

start_link() ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [], []).

increment() ->
    gen_server:cast(?MODULE, increment).

get_count() ->
    gen_server:call(?MODULE, get_count).

%% Callbacks
init([]) ->
    {ok, 0}.

handle_call(get_count, _From, Count) ->
    {reply, Count, Count}.

handle_cast(increment, Count) ->
    {noreply, Count + 1}.

%% Usage
main() ->
    {ok, _Pid} = counter:start_link(),
    counter:increment(),
    counter:increment(),
    counter:increment(),
    Count = counter:get_count(),
    io:format("~p~n", [Count]).  % Prints 3
```

### STM → ETS or gen_server

**Haskell:**
```haskell
import Control.Concurrent.STM

type Account = TVar Int

transfer :: Account -> Account -> Int -> STM ()
transfer from to amount = do
    fromBalance <- readTVar from
    when (fromBalance < amount) retry
    modifyTVar from (subtract amount)
    modifyTVar to (+ amount)

main :: IO ()
main = do
    account1 <- newTVarIO 1000
    account2 <- newTVarIO 0
    atomically $ transfer account1 account2 500
```

**Erlang (using ETS):**
```erlang
-module(bank).
-export([init/0, transfer/3]).

init() ->
    ets:new(accounts, [named_table, public, set]),
    ets:insert(accounts, {account1, 1000}),
    ets:insert(accounts, {account2, 0}).

transfer(From, To, Amount) ->
    % Note: ETS operations are not atomic across multiple keys
    % For true atomicity, use gen_server or mnesia transactions
    [{From, FromBalance}] = ets:lookup(accounts, From),

    if FromBalance >= Amount ->
        ets:update_counter(accounts, From, {2, -Amount}),
        ets:update_counter(accounts, To, {2, Amount}),
        ok;
    true ->
        {error, insufficient_funds}
    end.
```

**Erlang (using gen_server for atomicity):**
```erlang
-module(bank_server).
-behaviour(gen_server).

-export([start_link/0, transfer/3]).
-export([init/1, handle_call/3]).

start_link() ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [], []).

transfer(From, To, Amount) ->
    gen_server:call(?MODULE, {transfer, From, To, Amount}).

init([]) ->
    State = #{account1 => 1000, account2 => 0},
    {ok, State}.

handle_call({transfer, From, To, Amount}, _From, State) ->
    FromBalance = maps:get(From, State),
    if FromBalance >= Amount ->
        NewState = State#{
            From => FromBalance - Amount,
            To => maps:get(To, State) + Amount
        },
        {reply, ok, NewState};
    true ->
        {reply, {error, insufficient_funds}, State}
    end.
```

**Why this translation:**
- Erlang has no STM; use ETS for shared state or gen_server for atomicity
- gen_server provides serialized access (single-threaded state)
- For distributed transactions, use Mnesia

---

## Memory & Evaluation

### Lazy → Eager Evaluation

**Haskell (lazy):**
```haskell
-- Infinite lists
naturals :: [Integer]
naturals = [1..]

take10 :: [Integer]
take10 = take 10 naturals  -- Only evaluates first 10

-- Lazy evaluation benefits
expensiveComputation :: Int -> Int
expensiveComputation x = trace ("Computing " ++ show x) (x * 2)

result = if condition
         then take 5 $ map expensiveComputation [1..1000]
         else []
-- Only computes first 5 if condition is True
```

**Erlang (eager):**
```erlang
%% No infinite lists - must be explicit
naturals(N) -> lists:seq(1, N).

take10() -> lists:sublist(naturals(10), 10).

%% Must be careful with large computations
expensive_computation(X) ->
    io:format("Computing ~p~n", [X]),
    X * 2.

result(Condition) ->
    case Condition of
        true ->
            %% All 1000 items are computed, then we take 5
            lists:sublist(lists:map(fun expensive_computation/1,
                                     lists:seq(1, 1000)), 5);
        false ->
            []
    end.

%% Better: Use lazy construction
result_lazy(Condition) ->
    case Condition of
        true ->
            %% Compute only what's needed
            [expensive_computation(X) || X <- lists:seq(1, 5)];
        false ->
            []
    end.
```

### Thunks for Delayed Evaluation

**Haskell:**
```haskell
-- Lazy by default
expensiveValue :: Int
expensiveValue = sum [1..1000000]

useValue :: Bool -> Int
useValue False = 0
useValue True = expensiveValue  -- Only computed if needed
```

**Erlang:**
```erlang
%% Use fun() for thunks
expensive_value() -> lists:sum(lists:seq(1, 1000000)).

use_value(false) -> 0;
use_value(true) -> expensive_value().  % Computed every time called

%% Or pass as thunk
use_value_lazy(false, _Thunk) -> 0;
use_value_lazy(true, Thunk) -> Thunk().

%% Usage
Result = use_value_lazy(true, fun expensive_value/0).
```

**Why this translation:**
- Erlang is eager by default
- Use `fun()` to create thunks for delayed evaluation
- Be explicit about when computation happens

---

## Common Pitfalls

1. **Assuming laziness**: Erlang evaluates eagerly. Infinite lists don't work; be careful with large computations.

2. **Missing currying**: Haskell functions are curried by default; Erlang functions take all arguments at once. Use `fun` wrappers for partial application.

3. **Type safety assumptions**: Haskell's type system catches errors at compile time; Erlang catches them at runtime. Add comprehensive tests.

4. **Monadic composition**: Haskell's `>>=` and do-notation have no direct equivalent. Use nested case statements or helper functions.

5. **Defensive error handling**: Don't translate Haskell's comprehensive error handling to defensive Erlang code. Embrace "let it crash" with supervision.

6. **Immutability patterns**: Both languages are immutable, but Erlang uses processes for state instead of monads. Don't try to replicate State monad patterns.

7. **String handling**: Haskell `String` is `[Char]`; Erlang `string()` is `[char()]`. Prefer `binary()` in Erlang for efficiency.

8. **Pattern matching limitations**: Erlang guards are more limited than Haskell's. Can't call arbitrary functions in guards.

9. **Type class translation**: Haskell type classes don't map directly to Erlang behaviors. Behaviors are for OTP patterns, not ad-hoc polymorphism.

10. **Performance expectations**: Pure functional Haskell can be optimized heavily by GHC. Erlang prioritizes fault tolerance and concurrency over raw speed.

---

## Tooling

| Tool | Purpose | Notes |
|------|---------|-------|
| Manual translation | Convert code by hand | No mature transpiler exists |
| Dialyzer | Static analysis for Erlang | Type specs help catch errors |
| EUnit | Unit testing | Port Haskell HSpec tests |
| PropEr | Property-based testing | Similar to QuickCheck |
| Common Test | Integration testing | For OTP application testing |
| Rebar3 | Build tool | Like Cabal/Stack |
| Observer | Runtime inspection | Monitor processes, memory |

---

## Examples

### Example 1: Simple - Pure Function Translation

**Before (Haskell):**
```haskell
-- Calculate factorial
factorial :: Integer -> Integer
factorial 0 = 1
factorial n = n * factorial (n - 1)

-- Filter even numbers
evens :: [Int] -> [Int]
evens xs = [x | x <- xs, even x]
```

**After (Erlang):**
```erlang
%% Calculate factorial
-spec factorial(integer()) -> integer().
factorial(0) -> 1;
factorial(N) when N > 0 -> N * factorial(N - 1).

%% Filter even numbers
-spec evens([integer()]) -> [integer()].
evens(Xs) -> [X || X <- Xs, X rem 2 =:= 0].
```

### Example 2: Medium - Maybe and List Processing

**Before (Haskell):**
```haskell
data User = User { userId :: Int, userName :: String, userEmail :: String }

findUser :: Int -> [User] -> Maybe User
findUser uid users = find (\u -> userId u == uid) users

getUserEmails :: [Int] -> [User] -> [String]
getUserEmails ids users =
    mapMaybe (\uid -> fmap userEmail $ findUser uid users) ids

processUserData :: [Int] -> [User] -> [String]
processUserData ids users =
    getUserEmails ids users
    & filter (not . null)
    & map (\email -> "Email: " ++ email)
```

**After (Erlang):**
```erlang
-record(user, {
    user_id :: integer(),
    user_name :: string(),
    user_email :: string()
}).

-spec find_user(integer(), [#user{}]) -> {ok, #user{}} | error.
find_user(UserId, Users) ->
    case lists:filter(fun(U) -> U#user.user_id =:= UserId end, Users) of
        [User|_] -> {ok, User};
        [] -> error
    end.

-spec get_user_emails([integer()], [#user{}]) -> [string()].
get_user_emails(Ids, Users) ->
    lists:filtermap(
        fun(UserId) ->
            case find_user(UserId, Users) of
                {ok, User} -> {true, User#user.user_email};
                error -> false
            end
        end,
        Ids
    ).

-spec process_user_data([integer()], [#user{}]) -> [string()].
process_user_data(Ids, Users) ->
    Emails = get_user_emails(Ids, Users),
    Filtered = lists:filter(fun(E) -> E =/= "" end, Emails),
    lists:map(fun(Email) -> "Email: " ++ Email end, Filtered).
```

### Example 3: Complex - Stateful Server with Error Handling

**Before (Haskell):**
```haskell
{-# LANGUAGE GeneralizedNewtypeDeriving #-}

import Control.Monad.State
import Control.Monad.Except
import qualified Data.Map as Map

type UserId = Int
type SessionId = String

data User = User
    { userId :: UserId
    , userName :: String
    } deriving (Show, Eq)

data AppError
    = UserNotFound UserId
    | InvalidSession SessionId
    | DatabaseError String
    deriving (Show)

type Sessions = Map.Map SessionId UserId
type Users = Map.Map UserId User

data AppState = AppState
    { appSessions :: Sessions
    , appUsers :: Users
    } deriving (Show)

newtype App a = App
    { runApp :: ExceptT AppError (State AppState) a
    } deriving (Functor, Applicative, Monad, MonadState AppState, MonadError AppError)

createSession :: UserId -> App SessionId
createSession uid = do
    users <- gets appUsers
    case Map.lookup uid users of
        Nothing -> throwError $ UserNotFound uid
        Just _ -> do
            let sessionId = "session-" ++ show uid
            modify $ \s -> s { appSessions = Map.insert sessionId uid (appSessions s) }
            return sessionId

getUser :: SessionId -> App User
getUser sessionId = do
    sessions <- gets appSessions
    case Map.lookup sessionId sessions of
        Nothing -> throwError $ InvalidSession sessionId
        Just uid -> do
            users <- gets appUsers
            case Map.lookup uid users of
                Nothing -> throwError $ UserNotFound uid
                Just user -> return user

logout :: SessionId -> App ()
logout sessionId = do
    sessions <- gets appSessions
    unless (Map.member sessionId sessions) $
        throwError $ InvalidSession sessionId
    modify $ \s -> s { appSessions = Map.delete sessionId (appSessions s) }

-- Usage
runProgram :: AppState -> Either AppError (SessionId, AppState)
runProgram initialState =
    let action = do
            sid <- createSession 1
            user <- getUser sid
            logout sid
            return sid
    in runState (runExceptT $ runApp action) initialState
```

**After (Erlang):**
```erlang
-module(session_server).
-behaviour(gen_server).

%% API
-export([start_link/0, create_session/1, get_user/1, logout/1]).

%% gen_server callbacks
-export([init/1, handle_call/3, handle_cast/2, terminate/2]).

-record(user, {
    user_id :: integer(),
    user_name :: string()
}).

-record(state, {
    sessions :: #{session_id() => user_id()},
    users :: #{user_id() => #user{}}
}).

-type user_id() :: integer().
-type session_id() :: string().
-type error_reason() :: {user_not_found, user_id()}
                      | {invalid_session, session_id()}
                      | {database_error, string()}.

%%% API Functions

-spec start_link() -> {ok, pid()} | {error, term()}.
start_link() ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [], []).

-spec create_session(user_id()) -> {ok, session_id()} | {error, error_reason()}.
create_session(UserId) ->
    gen_server:call(?MODULE, {create_session, UserId}).

-spec get_user(session_id()) -> {ok, #user{}} | {error, error_reason()}.
get_user(SessionId) ->
    gen_server:call(?MODULE, {get_user, SessionId}).

-spec logout(session_id()) -> ok | {error, error_reason()}.
logout(SessionId) ->
    gen_server:call(?MODULE, {logout, SessionId}).

%%% gen_server Callbacks

init([]) ->
    %% Initialize with sample user
    Users = #{1 => #user{user_id = 1, user_name = "Alice"}},
    {ok, #state{sessions = #{}, users = Users}}.

handle_call({create_session, UserId}, _From, State) ->
    #state{sessions = Sessions, users = Users} = State,
    case maps:is_key(UserId, Users) of
        false ->
            {reply, {error, {user_not_found, UserId}}, State};
        true ->
            SessionId = "session-" ++ integer_to_list(UserId),
            NewSessions = maps:put(SessionId, UserId, Sessions),
            NewState = State#state{sessions = NewSessions},
            {reply, {ok, SessionId}, NewState}
    end;

handle_call({get_user, SessionId}, _From, State) ->
    #state{sessions = Sessions, users = Users} = State,
    case maps:get(SessionId, Sessions, undefined) of
        undefined ->
            {reply, {error, {invalid_session, SessionId}}, State};
        UserId ->
            case maps:get(UserId, Users, undefined) of
                undefined ->
                    {reply, {error, {user_not_found, UserId}}, State};
                User ->
                    {reply, {ok, User}, State}
            end
    end;

handle_call({logout, SessionId}, _From, State) ->
    #state{sessions = Sessions} = State,
    case maps:is_key(SessionId, Sessions) of
        false ->
            {reply, {error, {invalid_session, SessionId}}, State};
        true ->
            NewSessions = maps:remove(SessionId, Sessions),
            NewState = State#state{sessions = NewSessions},
            {reply, ok, NewState}
    end.

handle_cast(_Msg, State) ->
    {noreply, State}.

terminate(_Reason, _State) ->
    ok.

%%% Usage Example

run_program() ->
    {ok, _Pid} = start_link(),
    {ok, SessionId} = create_session(1),
    {ok, _User} = get_user(SessionId),
    ok = logout(SessionId),
    {ok, SessionId}.
```

**Key differences in this example:**
- Haskell's monad transformers become gen_server state
- `ExceptT` error handling becomes `{ok, Value} | {error, Reason}` tuples
- State monad becomes gen_server process state
- Pattern matching and guards handle all error cases
- OTP behavior provides structure and supervision

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `convert-erlang-haskell` - Reverse conversion (Erlang → Haskell)
- `lang-haskell-dev` - Haskell development patterns
- `lang-erlang-dev` - Erlang development patterns

Cross-cutting pattern skills:
- `patterns-concurrency-dev` - Processes, supervision, fault tolerance
- `patterns-serialization-dev` - Data encoding, validation
- `patterns-metaprogramming-dev` - Compile-time code generation
