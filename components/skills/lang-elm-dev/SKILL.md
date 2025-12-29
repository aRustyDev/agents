---
name: lang-elm-dev
description: Foundational Elm development patterns covering The Elm Architecture (TEA), type-safe frontend development, and core language features. Use when building Elm applications, understanding functional patterns in web development, working with union types and Maybe/Result, or needing guidance on Elm tooling and ecosystem.
---

# Elm Development

Foundational patterns for building type-safe frontend applications with Elm. This skill covers The Elm Architecture, core language features, and Elm's unique approach to functional web development.

## Overview

Elm is a purely functional language for building reliable web applications with no runtime exceptions. It compiles to JavaScript and enforces immutability, pure functions, and explicit error handling through its type system.

**This skill covers:**
- The Elm Architecture (Model-View-Update pattern)
- Core syntax (types, functions, pattern matching)
- Type system (union types, type aliases, Maybe/Result)
- Working with JSON and HTTP
- Common patterns and idioms
- Elm tooling (elm-format, elm-review, elm-test)

**This skill does NOT cover:**
- Advanced UI patterns → See elm-ui or elm-css specific skills
- Complex state management → See elm-spa patterns
- Backend integration specifics → See framework-specific docs
- JavaScript interop deep-dives → See ports/flags documentation

---

## Quick Reference

| Task | Pattern |
|------|---------|
| Define type alias | `type alias User = { name : String, age : Int }` |
| Define union type | `type Msg = Increment \| Decrement` |
| Pattern match | `case msg of ...` |
| Handle Maybe | `Maybe.withDefault default maybeValue` |
| Handle Result | `Result.withDefault default result` |
| Update function | `update : Msg -> Model -> ( Model, Cmd Msg )` |
| View function | `view : Model -> Html Msg` |
| HTTP request | `Http.get { url = "...", expect = Http.expectJson ... }` |
| Decode JSON | `Decode.field "name" Decode.string` |

---

## The Elm Architecture (TEA)

The Elm Architecture is the core pattern for all Elm applications. It consists of Model, View, and Update.

### Basic Structure

```elm
module Main exposing (main)

import Browser
import Html exposing (Html, button, div, text)
import Html.Events exposing (onClick)

-- MODEL

type alias Model =
    { count : Int
    }

init : () -> ( Model, Cmd Msg )
init _ =
    ( { count = 0 }, Cmd.none )

-- UPDATE

type Msg
    = Increment
    | Decrement

update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        Increment ->
            ( { model | count = model.count + 1 }, Cmd.none )

        Decrement ->
            ( { model | count = model.count - 1 }, Cmd.none )

-- VIEW

view : Model -> Html Msg
view model =
    div []
        [ button [ onClick Decrement ] [ text "-" ]
        , div [] [ text (String.fromInt model.count) ]
        , button [ onClick Increment ] [ text "+" ]
        ]

-- MAIN

main : Program () Model Msg
main =
    Browser.element
        { init = init
        , update = update
        , view = view
        , subscriptions = \_ -> Sub.none
        }
```

### TEA Flow

```
┌─────────────────────────────────────────────────┐
│              The Elm Architecture               │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌───────────┐                                  │
│  │  init     │ ──▶ ( Model, Cmd Msg )           │
│  └───────────┘                                  │
│       │                                         │
│       ▼                                         │
│  ┌───────────┐      User                        │
│  │   Model   │ ◀─── Event                       │
│  └───────────┘                                  │
│       │                                         │
│       ▼                                         │
│  ┌───────────┐                                  │
│  │   view    │ ──▶ Html Msg                     │
│  └───────────┘                                  │
│       │                                         │
│       ▼                                         │
│  ┌───────────┐                                  │
│  │    Msg    │ (user clicks button)             │
│  └───────────┘                                  │
│       │                                         │
│       ▼                                         │
│  ┌───────────┐                                  │
│  │  update   │ ──▶ ( Model, Cmd Msg )           │
│  └───────────┘                                  │
│       │                                         │
│       └──────────▶ (loop back to Model)         │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Key Principles:**
- Model holds all application state
- View is a pure function: Model → Html Msg
- Update is a pure function: Msg → Model → (Model, Cmd Msg)
- All side effects through Cmd (commands) and Sub (subscriptions)

---

## Core Types

### Type Aliases

```elm
-- Simple record type
type alias User =
    { name : String
    , email : String
    , age : Int
    }

-- Creating instances
user : User
user =
    { name = "Alice"
    , email = "alice@example.com"
    , age = 30
    }

-- Updating records (immutable)
updatedUser : User
updatedUser =
    { user | age = 31 }

-- Nested records
type alias Address =
    { street : String
    , city : String
    }

type alias Person =
    { name : String
    , address : Address
    }
```

### Union Types (Custom Types)

```elm
-- Simple union type
type Direction
    = North
    | South
    | East
    | West

-- Union type with data
type Msg
    = NoOp
    | SetName String
    | SetAge Int
    | Login { username : String, password : String }

-- Using union types
handleMsg : Msg -> Model -> Model
handleMsg msg model =
    case msg of
        NoOp ->
            model

        SetName name ->
            { model | name = name }

        SetAge age ->
            { model | age = age }

        Login { username, password } ->
            -- Handle login
            model
```

### Maybe and Result

```elm
-- Maybe: value that might not exist
type Maybe a
    = Just a
    | Nothing

-- Using Maybe
findUser : Int -> Maybe User
findUser id =
    if id == 1 then
        Just { name = "Alice", email = "alice@example.com", age = 30 }
    else
        Nothing

-- Pattern matching Maybe
displayName : Maybe User -> String
displayName maybeUser =
    case maybeUser of
        Just user ->
            user.name

        Nothing ->
            "Anonymous"

-- Maybe helpers
name : String
name =
    findUser 1
        |> Maybe.map .name
        |> Maybe.withDefault "Anonymous"

-- Result: operation that might fail
type Result error value
    = Ok value
    | Err error

-- Using Result
parseAge : String -> Result String Int
parseAge str =
    case String.toInt str of
        Just age ->
            if age >= 0 then
                Ok age
            else
                Err "Age must be non-negative"

        Nothing ->
            Err "Not a valid number"

-- Chaining Results
validateAge : String -> Result String Int
validateAge str =
    parseAge str
        |> Result.andThen (\age ->
            if age < 120 then
                Ok age
            else
                Err "Age must be less than 120"
        )
```

---

## Pattern Matching

### Case Expressions

```elm
-- Basic case
describeNumber : Int -> String
describeNumber n =
    case n of
        0 ->
            "zero"

        1 ->
            "one"

        _ ->
            "other"

-- Multiple patterns
describeList : List a -> String
describeList list =
    case list of
        [] ->
            "empty"

        [ x ] ->
            "singleton"

        [ x, y ] ->
            "pair"

        x :: xs ->
            "list with multiple elements"

-- Destructuring records
greet : User -> String
greet user =
    case user of
        { name, age } ->
            "Hello " ++ name ++ ", age " ++ String.fromInt age
```

### If-Let Pattern

```elm
-- Guards in case expressions
classify : Int -> String
classify n =
    case n of
        x ->
            if x < 0 then
                "negative"
            else if x == 0 then
                "zero"
            else
                "positive"

-- Let-in for local bindings
calculate : Int -> Int
calculate x =
    let
        doubled =
            x * 2

        squared =
            x * x
    in
    doubled + squared
```

---

## Functions

### Function Syntax

```elm
-- Simple function
add : Int -> Int -> Int
add x y =
    x + y

-- Anonymous function (lambda)
increment : Int -> Int
increment =
    \x -> x + 1

-- Partial application
add5 : Int -> Int
add5 =
    add 5

-- Pipeline operator
result : Int
result =
    10
        |> add 5
        |> multiply 2
        |> subtract 3

-- Composition operator
addThenDouble : Int -> Int -> Int
addThenDouble =
    add >> multiply 2
```

### Higher-Order Functions

```elm
-- Map
doubled : List Int
doubled =
    List.map (\x -> x * 2) [ 1, 2, 3, 4, 5 ]

-- Filter
evens : List Int
evens =
    List.filter (\x -> modBy 2 x == 0) [ 1, 2, 3, 4, 5 ]

-- Fold (reduce)
sum : Int
sum =
    List.foldl (+) 0 [ 1, 2, 3, 4, 5 ]

-- Chain operations
processNumbers : List Int -> Int
processNumbers numbers =
    numbers
        |> List.filter (\x -> x > 0)
        |> List.map (\x -> x * 2)
        |> List.foldl (+) 0
```

---

## Working with JSON

### JSON Decoders

```elm
import Json.Decode as Decode exposing (Decoder)

-- Simple decoder
userDecoder : Decoder User
userDecoder =
    Decode.map3 User
        (Decode.field "name" Decode.string)
        (Decode.field "email" Decode.string)
        (Decode.field "age" Decode.int)

-- Alternative syntax with succeed and pipeline
import Json.Decode.Pipeline exposing (required, optional)

userDecoder : Decoder User
userDecoder =
    Decode.succeed User
        |> required "name" Decode.string
        |> required "email" Decode.string
        |> required "age" Decode.int

-- Decoding lists
usersDecoder : Decoder (List User)
usersDecoder =
    Decode.list userDecoder

-- Decoding nested objects
type alias Response =
    { data : List User
    , total : Int
    }

responseDecoder : Decoder Response
responseDecoder =
    Decode.map2 Response
        (Decode.field "data" (Decode.list userDecoder))
        (Decode.field "total" Decode.int)

-- Optional fields
type alias Config =
    { apiUrl : String
    , timeout : Maybe Int
    }

configDecoder : Decoder Config
configDecoder =
    Decode.map2 Config
        (Decode.field "apiUrl" Decode.string)
        (Decode.maybe (Decode.field "timeout" Decode.int))
```

### JSON Encoders

```elm
import Json.Encode as Encode

-- Encode user to JSON
encodeUser : User -> Encode.Value
encodeUser user =
    Encode.object
        [ ( "name", Encode.string user.name )
        , ( "email", Encode.string user.email )
        , ( "age", Encode.int user.age )
        ]

-- Encode list
encodeUsers : List User -> Encode.Value
encodeUsers users =
    Encode.list encodeUser users

-- Optional fields
encodeConfig : Config -> Encode.Value
encodeConfig config =
    case config.timeout of
        Just timeout ->
            Encode.object
                [ ( "apiUrl", Encode.string config.apiUrl )
                , ( "timeout", Encode.int timeout )
                ]

        Nothing ->
            Encode.object
                [ ( "apiUrl", Encode.string config.apiUrl )
                ]
```

---

## HTTP Requests

### Making HTTP Requests

```elm
import Http
import Json.Decode as Decode

-- GET request
type Msg
    = GotUsers (Result Http.Error (List User))

getUsers : Cmd Msg
getUsers =
    Http.get
        { url = "https://api.example.com/users"
        , expect = Http.expectJson GotUsers (Decode.list userDecoder)
        }

-- POST request
createUser : User -> Cmd Msg
createUser user =
    Http.post
        { url = "https://api.example.com/users"
        , body = Http.jsonBody (encodeUser user)
        , expect = Http.expectJson GotCreateUserResponse userDecoder
        }

-- Custom request
updateUser : Int -> User -> Cmd Msg
updateUser id user =
    Http.request
        { method = "PUT"
        , headers = [ Http.header "Authorization" "Bearer token" ]
        , url = "https://api.example.com/users/" ++ String.fromInt id
        , body = Http.jsonBody (encodeUser user)
        , expect = Http.expectJson GotUpdateUserResponse userDecoder
        , timeout = Nothing
        , tracker = Nothing
        }

-- Handling HTTP results in update
update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        GotUsers result ->
            case result of
                Ok users ->
                    ( { model | users = users, error = Nothing }, Cmd.none )

                Err error ->
                    ( { model | error = Just (httpErrorToString error) }, Cmd.none )

-- HTTP error handling
httpErrorToString : Http.Error -> String
httpErrorToString error =
    case error of
        Http.BadUrl url ->
            "Bad URL: " ++ url

        Http.Timeout ->
            "Request timed out"

        Http.NetworkError ->
            "Network error"

        Http.BadStatus status ->
            "Bad status: " ++ String.fromInt status

        Http.BadBody body ->
            "Bad body: " ++ body
```

---

## Common Patterns

### Loading States

```elm
type RemoteData error value
    = NotAsked
    | Loading
    | Success value
    | Failure error

type alias Model =
    { users : RemoteData Http.Error (List User)
    }

-- In update
update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        FetchUsers ->
            ( { model | users = Loading }, getUsers )

        GotUsers result ->
            case result of
                Ok users ->
                    ( { model | users = Success users }, Cmd.none )

                Err error ->
                    ( { model | users = Failure error }, Cmd.none )

-- In view
view : Model -> Html Msg
view model =
    case model.users of
        NotAsked ->
            button [ onClick FetchUsers ] [ text "Load Users" ]

        Loading ->
            div [] [ text "Loading..." ]

        Success users ->
            div [] (List.map viewUser users)

        Failure error ->
            div [] [ text ("Error: " ++ httpErrorToString error) ]
```

### Form Handling

```elm
type alias Form =
    { name : String
    , email : String
    , errors : List String
    }

type Msg
    = SetName String
    | SetEmail String
    | Submit

update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        SetName name ->
            ( { model | form = updateFormName name model.form }, Cmd.none )

        SetEmail email ->
            ( { model | form = updateFormEmail email model.form }, Cmd.none )

        Submit ->
            case validateForm model.form of
                Ok validForm ->
                    ( model, submitForm validForm )

                Err errors ->
                    ( { model | form = setFormErrors errors model.form }, Cmd.none )

-- View with form
viewForm : Form -> Html Msg
viewForm form =
    div []
        [ input
            [ type_ "text"
            , placeholder "Name"
            , value form.name
            , onInput SetName
            ]
            []
        , input
            [ type_ "email"
            , placeholder "Email"
            , value form.email
            , onInput SetEmail
            ]
            []
        , button [ onClick Submit ] [ text "Submit" ]
        , viewErrors form.errors
        ]

viewErrors : List String -> Html msg
viewErrors errors =
    div []
        (List.map (\error -> div [] [ text error ]) errors)
```

### Routing

```elm
import Browser.Navigation as Nav
import Url
import Url.Parser as Parser exposing (Parser, (</>))

type Route
    = Home
    | Users
    | User Int
    | NotFound

routeParser : Parser (Route -> a) a
routeParser =
    Parser.oneOf
        [ Parser.map Home Parser.top
        , Parser.map Users (Parser.s "users")
        , Parser.map User (Parser.s "users" </> Parser.int)
        ]

fromUrl : Url.Url -> Route
fromUrl url =
    Parser.parse routeParser url
        |> Maybe.withDefault NotFound

-- In application
type alias Model =
    { key : Nav.Key
    , route : Route
    }

type Msg
    = UrlChanged Url.Url
    | LinkClicked Browser.UrlRequest

update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        LinkClicked urlRequest ->
            case urlRequest of
                Browser.Internal url ->
                    ( model, Nav.pushUrl model.key (Url.toString url) )

                Browser.External href ->
                    ( model, Nav.load href )

        UrlChanged url ->
            ( { model | route = fromUrl url }, Cmd.none )
```

---

## Elm Tooling

### elm.json

```json
{
    "type": "application",
    "source-directories": [
        "src"
    ],
    "elm-version": "0.19.1",
    "dependencies": {
        "direct": {
            "elm/browser": "1.0.2",
            "elm/core": "1.0.5",
            "elm/html": "1.0.0",
            "elm/http": "2.0.0",
            "elm/json": "1.1.3"
        },
        "indirect": {}
    },
    "test-dependencies": {
        "direct": {},
        "indirect": {}
    }
}
```

### Commands

```bash
# Initialize new project
elm init

# Install package
elm install elm/http

# Build
elm make src/Main.elm

# Build optimized
elm make src/Main.elm --optimize --output=main.js

# Start development server
elm reactor

# Run tests
elm-test

# Format code
elm-format src/ --yes

# Review code
elm-review
```

---

## Troubleshooting

### Type Mismatch Errors

**Problem:** `The 1st argument to map is not what I expect`

```elm
-- Error: Wrong type
List.map String.toInt [ "1", "2", "3" ]  -- Returns List (Maybe Int)

-- Fix: Handle Maybe
List.filterMap String.toInt [ "1", "2", "3" ]  -- Returns List Int
```

### Missing Pattern Match

**Problem:** `This case expression does not have branches for all possibilities`

```elm
-- Error: Missing Nothing case
getName : Maybe User -> String
getName maybeUser =
    case maybeUser of
        Just user ->
            user.name

-- Fix: Add all cases
getName : Maybe User -> String
getName maybeUser =
    case maybeUser of
        Just user ->
            user.name

        Nothing ->
            "Anonymous"
```

### Circular Dependencies

**Problem:** `IMPORT CYCLE`

**Fix:** Extract shared types to separate module:

```elm
-- Before: Main.elm imports User.elm, User.elm imports Main.elm

-- After: Create Types.elm
module Types exposing (User, Msg)

-- Main.elm imports Types
-- User.elm imports Types
```

---

## Concurrency

Elm takes a fundamentally different approach to concurrency compared to traditional imperative languages. Rather than managing threads and locks, Elm's architecture handles concurrency through managed effects. For cross-language comparison, see `patterns-concurrency-dev`.

### Why Traditional Concurrency Doesn't Apply

```elm
-- Elm has NO:
-- - Threads or green threads
-- - Locks or mutexes
-- - Race conditions
-- - Shared mutable state
-- - Async/await keywords

-- Instead: The Elm Runtime manages ALL concurrency
-- Your code is ALWAYS single-threaded and synchronous
```

### The Elm Architecture Handles Concurrency

```elm
-- Multiple HTTP requests "in flight" - runtime manages them
type Msg
    = GotUser1 (Result Http.Error User)
    | GotUser2 (Result Http.Error User)
    | GotUser3 (Result Http.Error User)

update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        StartFetching ->
            -- Runtime executes these concurrently
            ( { model | loading = True }
            , Cmd.batch
                [ Http.get { url = "/api/user/1", expect = Http.expectJson GotUser1 userDecoder }
                , Http.get { url = "/api/user/2", expect = Http.expectJson GotUser2 userDecoder }
                , Http.get { url = "/api/user/3", expect = Http.expectJson GotUser3 userDecoder }
                ]
            )

        GotUser1 result ->
            -- Each response handled independently as it arrives
            -- Runtime ensures update is never called concurrently
            handleUserResult 1 result model

        GotUser2 result ->
            handleUserResult 2 result model

        GotUser3 result ->
            handleUserResult 3 result model
```

### Cmd and Sub: Managed Effects

```elm
-- Cmd: Commands that produce effects
-- The runtime executes these, guarantees serialized updates

type alias Model =
    { time : Time.Posix
    , windowSize : ( Int, Int )
    }

type Msg
    = Tick Time.Posix
    | WindowResized Int Int

-- Subscriptions: Stream of events from outside world
subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.batch
        [ Time.every 1000 Tick           -- Every second
        , Browser.Events.onResize WindowResized  -- On window resize
        ]
        -- Runtime manages these subscriptions
        -- Messages arrive one at a time in update function

update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        Tick newTime ->
            ( { model | time = newTime }, Cmd.none )

        WindowResized width height ->
            ( { model | windowSize = ( width, height ) }, Cmd.none )
```

### Task: Sequential Async Operations

```elm
import Task exposing (Task)
import Time
import Http

-- Task: Describes async operation, doesn't execute until performed
-- Think of it as a "recipe" for an async operation

getCurrentTime : Task Never Time.Posix
getCurrentTime =
    Time.now

-- Chain Tasks sequentially
fetchAndLog : Task Http.Error String
fetchAndLog =
    Http.task
        { method = "GET"
        , headers = []
        , url = "/api/data"
        , body = Http.emptyBody
        , resolver = Http.stringResolver handleResponse
        , timeout = Nothing
        }
        |> Task.andThen (\data ->
            -- Log happens AFTER fetch completes
            Task.succeed ("Fetched: " ++ data)
        )

-- Perform task to create Cmd
type Msg
    = GotData (Result Http.Error String)

fetchData : Cmd Msg
fetchData =
    Task.attempt GotData fetchAndLog

-- Task combinators for "concurrent" execution
-- (Runtime manages, you describe relationships)
fetchMultiple : Cmd Msg
fetchMultiple =
    Task.map2 Tuple.pair
        (Http.task { ... })  -- Fetch 1
        (Http.task { ... })  -- Fetch 2
        |> Task.attempt GotBothResults
        -- Runtime may execute concurrently, delivers result when BOTH complete
```

### Process: Background Tasks

```elm
import Process
import Task

-- Delay execution
delayed : Msg -> Cmd Msg
delayed msg =
    Process.sleep 1000  -- 1 second in milliseconds
        |> Task.perform (\_ -> msg)

-- Debouncing user input
type Msg
    = UserTyped String
    | DebouncedInput String
    | CancelDebounce

update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        UserTyped input ->
            ( { model | input = input }
            , Cmd.batch
                [ Process.sleep 500
                    |> Task.perform (\_ -> DebouncedInput input)
                ]
            )

        DebouncedInput input ->
            -- Only fires if user stops typing for 500ms
            ( model, performSearch input )
```

### Ports: Concurrent JavaScript Interop

```elm
-- port: Escape hatch for JS concurrency primitives
port module Main exposing (..)

-- Outgoing: Send to JavaScript
port sendToWorker : String -> Cmd msg

-- Incoming: Receive from JavaScript (subscription)
port workerResponse : (String -> msg) -> Sub msg

type Msg
    = StartWork String
    | WorkComplete String

subscriptions : Model -> Sub Msg
subscriptions model =
    workerResponse WorkComplete

update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        StartWork data ->
            -- JavaScript can run Web Workers, handle concurrency
            ( { model | working = True }
            , sendToWorker data
            )

        WorkComplete result ->
            ( { model | working = False, result = result }
            , Cmd.none
            )

-- In JavaScript:
-- app.ports.sendToWorker.subscribe(function(data) {
--     const worker = new Worker('worker.js');
--     worker.postMessage(data);
--     worker.onmessage = function(e) {
--         app.ports.workerResponse.send(e.data);
--     };
-- });
```

### Key Principles

```elm
-- 1. Update is NEVER concurrent - always single-threaded
-- 2. Runtime manages ALL asynchronous operations
-- 3. No race conditions possible in Elm code
-- 4. Cmd/Sub provide declarative concurrency
-- 5. For CPU-intensive work: Use ports + Web Workers

-- Compare to other languages:
-- - Go/Erlang: Explicit goroutines/processes → Elm: Cmd/Sub
-- - JavaScript: async/await → Elm: Task
-- - Rust: threads + channels → Elm: Runtime + messages
```

---

## Metaprogramming

Elm intentionally does not support traditional metaprogramming like macros or reflection. This is a deliberate design choice to ensure code is explicit, maintainable, and debuggable. For cross-language comparison, see `patterns-metaprogramming-dev`.

### Why Elm Has No Metaprogramming

```elm
-- Elm has NO:
-- - Macros (no code that writes code)
-- - Reflection (can't inspect types at runtime)
-- - eval() (no runtime code execution)
-- - Dynamic code generation
-- - Preprocessor directives

-- Philosophy:
-- - Explicit is better than implicit
-- - Code should be readable without magic
-- - Compiler guarantees should be reliable
-- - Refactoring should be safe and predictable
```

### Alternative: Code Generation (elm-codegen)

```bash
# External tool generates Elm code at build time
# NOT metaprogramming - generates source files you commit

# Example: Generate API client from OpenAPI spec
elm-codegen openapi.yaml --output src/Generated/Api.elm

# Result: Normal Elm code you can read and version control
```

```elm
-- Generated/Api.elm (example output)
module Generated.Api exposing (getUser, createUser)

import Http
import Json.Decode as Decode

getUser : Int -> (Result Http.Error User -> msg) -> Cmd msg
getUser userId toMsg =
    Http.get
        { url = "/api/users/" ++ String.fromInt userId
        , expect = Http.expectJson toMsg userDecoder
        }

userDecoder : Decode.Decoder User
userDecoder =
    Decode.map3 User
        (Decode.field "name" Decode.string)
        (Decode.field "email" Decode.string)
        (Decode.field "age" Decode.int)
```

### Alternative: Type-Driven Design

```elm
-- Instead of metaprogramming, use types to enforce invariants

-- Bad: Use strings, need validation everywhere
type alias UserId = String

validateUserId : String -> Maybe UserId
validateUserId str =
    if String.startsWith "user-" str then
        Just str
    else
        Nothing

-- Good: Make invalid states unrepresentable
type UserId = UserId String

createUserId : String -> Maybe UserId
createUserId str =
    if String.startsWith "user-" str then
        Just (UserId str)
    else
        Nothing

getUserById : UserId -> Cmd Msg
getUserById (UserId id) =
    -- Guaranteed to be valid, no runtime checks needed
    Http.get { url = "/api/users/" ++ id, ... }

-- Type system does the "metaprogramming" work at compile time
```

### Alternative: Phantom Types

```elm
-- Encode state in types without runtime cost

type Validated
type Unvalidated

type Form a
    = Form
        { email : String
        , age : String
        }

-- Can't use unvalidated form
submitForm : Form Validated -> Cmd Msg
submitForm (Form data) =
    Http.post { ... }

-- Must validate first
validateForm : Form Unvalidated -> Result (List String) (Form Validated)
validateForm (Form data) =
    if String.contains "@" data.email then
        Ok (Form data)
    else
        Err [ "Invalid email" ]

-- Type system prevents: submitForm unvalidatedForm
-- Type system enforces: validateForm form |> Result.map submitForm
```

### Alternative: Custom Types for DSLs

```elm
-- Instead of macros, define DSL as data

type Query
    = Select (List String) Table (Maybe Condition)
    | Insert Table (List ( String, Value ))

type Table = Table String

type Condition
    = Equals String Value
    | And Condition Condition
    | Or Condition Condition

type Value
    = StringVal String
    | IntVal Int

-- Build queries as data
query : Query
query =
    Select
        [ "name", "email" ]
        (Table "users")
        (Just (Equals "active" (StringVal "true")))

-- Interpret DSL
toSql : Query -> String
toSql queryData =
    case queryData of
        Select fields (Table tableName) maybeWhere ->
            "SELECT "
                ++ String.join ", " fields
                ++ " FROM "
                ++ tableName
                ++ (case maybeWhere of
                        Just condition ->
                            " WHERE " ++ conditionToSql condition

                        Nothing ->
                            ""
                   )

        _ ->
            "..."

-- Result: Type-safe SQL without macros
-- Compiler checks all queries at compile time
```

### Ports as FFI (Foreign Function Interface)

```elm
-- Port: Call JavaScript for things Elm can't do
port module Analytics exposing (trackEvent)

-- Send data to JavaScript
port trackEvent : { name : String, properties : Json.Encode.Value } -> Cmd msg

-- Use like any other Cmd
update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ButtonClicked ->
            ( model
            , trackEvent
                { name = "button_clicked"
                , properties =
                    Json.Encode.object
                        [ ( "button_id", Json.Encode.string "submit" )
                        ]
                }
            )
```

```javascript
// JavaScript side (ports.js)
app.ports.trackEvent.subscribe(function(event) {
    // Use any JS metaprogramming/reflection here
    analytics.track(event.name, event.properties);

    // Can use JS features Elm doesn't have:
    // - eval()
    // - Proxy objects
    // - Reflect API
    // - Dynamic code loading
});
```

### elm-review for Custom Linting

```elm
-- Instead of macros, write custom compile-time checks
-- elm-review: Analyze and transform code at build time

module ReviewConfig exposing (config)

import Review.Rule as Rule
import Elm.Syntax.Expression exposing (Expression)

-- Custom rule: Prevent Debug.log in production
noDebugLog : Rule
noDebugLog =
    Rule.newModuleRuleSchema "NoDebugLog" ()
        |> Rule.withSimpleExpressionVisitor expressionVisitor
        |> Rule.fromModuleRuleSchema

expressionVisitor : Expression -> List Rule.Error
expressionVisitor expression =
    case expression of
        FunctionOrValue [ "Debug" ] "log" ->
            [ Rule.error
                { message = "Debug.log is not allowed"
                , details = [ "Remove Debug.log before committing" ]
                }
            ]

        _ ->
            []
```

### Key Principles

```elm
-- Elm philosophy on metaprogramming:
-- 1. No magic - code should be obvious
-- 2. Use types instead of runtime checks
-- 3. Generate code externally, commit it
-- 4. Ports for JS interop when needed
-- 5. elm-review for custom compile-time checks

-- Compare to other languages:
-- - Ruby/Lisp macros → Elm: Code generation + types
-- - Python reflection → Elm: Phantom types
-- - Template Haskell → Elm: External codegen
-- - C preprocessor → Elm: Type system + elm-review
```

---

## Cross-Cutting Patterns

For cross-language comparison and translation patterns, see:

- `patterns-concurrency-dev` - Compare Elm's Cmd/Sub/Task to threads, async/await, actors
- `patterns-metaprogramming-dev` - Compare Elm's type-driven approach to macros, reflection, codegen
- `patterns-serialization-dev` - JSON decoders/encoders patterns across languages

---

## References

- [Elm Guide](https://guide.elm-lang.org/) - Official tutorial
- [Elm Packages](https://package.elm-lang.org/) - Package repository
- [Elm Discourse](https://discourse.elm-lang.org/) - Community forum
- [Elm Radio Podcast](https://elm-radio.com/) - Elm news and discussions
- [Elm in Action](https://www.manning.com/books/elm-in-action) - Comprehensive book
