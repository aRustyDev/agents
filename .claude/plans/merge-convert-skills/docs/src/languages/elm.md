# Elm

> Purely functional language for reliable web applications with no runtime exceptions.

## Overview

Elm is a purely functional programming language created by Evan Czaplicki in 2012, designed specifically for building web front-end applications. It compiles to JavaScript and is known for its friendly error messages, strong static typing, and the guarantee of no runtime exceptions.

Elm pioneered The Elm Architecture (TEA), a pattern for building web applications that influenced Redux, Vuex, and many other state management solutions. The language enforces immutability and purity, using a managed effects system for side effects.

The language prioritizes developer experience, maintainability, and correctness over flexibility, making it ideal for applications where reliability is critical.

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | ML-FP | Haskell-influenced, pure |
| Secondary Family | — | No OOP |
| Subtype | pure-web | Web-specific pure FP |

See: [ML-FP Family](../language-families/ml-fp.md)

## Version History

| Version | Release | Key Changes for Conversion |
|---------|---------|---------------------------|
| 0.17 | 2016-05 | Subscriptions, effect managers |
| 0.18 | 2016-11 | Debugger, lazy rendering |
| 0.19 | 2018-08 | Faster, smaller, removed native code |
| 0.19.1 | 2019-10 | Bug fixes, current stable |

**Note:** Elm has a slow, deliberate release cycle focused on stability.

## Feature Profile

### Type System

- **Strength:** strong (static, sound, no escape hatches)
- **Inference:** global (Hindley-Milner)
- **Generics:** parametric (type variables)
- **Nullability:** explicit (Maybe a only)

### Memory Model

- **Management:** gc (JavaScript runtime)
- **Mutability:** immutable (no mutable state)
- **Allocation:** heap (JavaScript semantics)

### Control Flow

- **Structured:** if-then-else, case-of
- **Effects:** managed (Cmd, Sub - no direct IO)
- **Async:** Cmd msg (Task-based commands)

### Data Types

- **Primitives:** Int, Float, Bool, Char, String
- **Composites:** records, custom types (ADTs), tuples
- **Collections:** List, Array, Dict, Set
- **Abstraction:** modules, type aliases

### Metaprogramming

- **Macros:** none
- **Reflection:** none
- **Code generation:** elm-codegen (external tool)

## Ecosystem

| Tool | Name | Notes |
|------|------|-------|
| Package Manager | elm (built-in) | Enforced semver |
| Build System | elm make, elm-live | Simple build |
| LSP | elm-language-server | Good IDE support |
| Formatter | elm-format | Opinionated, standard |
| Linter | elm-review | Extensive rule set |
| REPL | elm repl | Built-in |
| Test Framework | elm-test | Property-based included |

## Syntax Patterns

```elm
-- Function definition
greet : String -> Int -> String
greet name times =
    String.repeat times ("Hello, " ++ name ++ "! ")

-- Generic function
identity : a -> a
identity x =
    x

-- Type alias (record)
type alias User =
    { id : String
    , name : String
    , email : Maybe String
    }

-- Custom type (ADT / sum type)
type Result value error
    = Ok value
    | Err error

type Shape
    = Circle Float
    | Rectangle Float Float

-- Pattern matching
area : Shape -> Float
area shape =
    case shape of
        Circle r ->
            pi * r * r

        Rectangle w h ->
            w * h

-- The Elm Architecture: Model
type alias Model =
    { count : Int
    , loading : Bool
    }

-- The Elm Architecture: Messages
type Msg
    = Increment
    | Decrement
    | GotResponse (Result Http.Error String)

-- The Elm Architecture: Update
update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        Increment ->
            ( { model | count = model.count + 1 }
            , Cmd.none
            )

        Decrement ->
            ( { model | count = model.count - 1 }
            , Cmd.none
            )

        GotResponse result ->
            case result of
                Ok data ->
                    ( { model | loading = False }
                    , Cmd.none
                    )

                Err _ ->
                    ( model, Cmd.none )

-- The Elm Architecture: View
view : Model -> Html Msg
view model =
    div []
        [ button [ onClick Decrement ] [ text "-" ]
        , text (String.fromInt model.count)
        , button [ onClick Increment ] [ text "+" ]
        ]

-- HTTP request (returns Cmd)
fetchData : Cmd Msg
fetchData =
    Http.get
        { url = "/api/data"
        , expect = Http.expectString GotResponse
        }

-- Pipeline style
processNumbers : List Int -> Int
processNumbers numbers =
    numbers
        |> List.filter (\x -> x > 0)
        |> List.map (\x -> x * 2)
        |> List.sum

-- Record update
updateUser : User -> User
updateUser user =
    { user | name = "New Name" }

-- Maybe handling
getEmailOrDefault : User -> String
getEmailOrDefault user =
    user.email
        |> Maybe.withDefault "no-email@example.com"

-- JSON decoding
userDecoder : Decoder User
userDecoder =
    Decode.map3 User
        (Decode.field "id" Decode.string)
        (Decode.field "name" Decode.string)
        (Decode.maybe (Decode.field "email" Decode.string))
```

## Semantic Gaps

| Gap | Severity | Workaround |
|-----|----------|------------|
| No higher-kinded types | moderate | Use specific types, phantom types |
| No type classes | moderate | Use module patterns, explicit passing |
| No custom operators | minor | Use descriptive function names |
| Limited JS interop (ports only) | moderate | Design port-based architecture |
| No native/FFI in 0.19 | moderate | Use ports or web components |

## Convert-* Coverage

| Direction | Count | Skills |
|-----------|-------|--------|
| As Source | 5 | elm-erlang, elm-fsharp, elm-haskell, elm-roc, elm-scala |
| As Target | 3 | python-elm, elixir-elm, clojure-elm |

**Note:** Web-focused FP - conversions often involve architecture patterns.

## Idiomatic Patterns

### Custom Types → ADTs/Enums

```elm
-- Elm: custom type
type Maybe a
    = Just a
    | Nothing

-- IR equivalent: enum
-- enum Maybe<T> { Just(T), Nothing }
```

### The Elm Architecture → State Machine

```elm
-- Elm: TEA pattern
update : Msg -> Model -> ( Model, Cmd Msg )

-- IR equivalent: state reducer with effects
-- fn update(msg: Msg, model: Model) -> (Model, Effect<Msg>)
```

### Ports → Foreign Function Interface

```elm
-- Elm: port definition
port sendMessage : String -> Cmd msg
port receiveMessage : (String -> msg) -> Sub msg

-- IR equivalent: external function binding
-- external fn sendMessage(String) -> IO ()
```

### Record Update → Immutable Update

```elm
-- Elm: record update syntax
{ user | name = "Alice" }

-- IR equivalent: spread/copy with update
-- User { name: "Alice", ..user }
```

## Related Languages

- **Influenced by:** Haskell, ML, Standard ML
- **Influenced:** Roc, PureScript (architecture), Redux
- **Compiles to:** JavaScript
- **FFI compatible:** JavaScript (via ports only)

## Sources

- [Elm Guide](https://guide.elm-lang.org/)
- [Elm Syntax Documentation](https://elm-lang.org/docs/syntax)
- [Elm Packages](https://package.elm-lang.org/)
- [Elm Architecture Tutorial](https://guide.elm-lang.org/architecture/)

## See Also

- [ML-FP Family](../language-families/ml-fp.md)
- [Haskell](haskell.md) - Influence source
- [Roc](roc.md) - Similar philosophy, different domain
- [PureScript](purescript.md) - Alternative pure FP for web
