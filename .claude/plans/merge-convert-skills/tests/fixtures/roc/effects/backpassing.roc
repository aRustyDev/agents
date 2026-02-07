# Backpassing Syntax
#
# Demonstrates Roc's backpassing (reverse function application) pattern.

app [main] { pf: platform "https://github.com/roc-lang/basic-cli/releases/download/0.10.0/vNe6s9hWzoTZtFmNkvSvMl63s9gxRRrKX7lRsnq6NDY.tar.br" }

import pf.Stdout
import pf.Task exposing [Task]

## Basic backpassing with Task

main : Task {} *
main =
    # Backpassing binds the result to a name
    {} <- Stdout.line "Step 1: Initialize"
    {} <- Stdout.line "Step 2: Process"
    {} <- Stdout.line "Step 3: Complete"
    Task.ok {}

## Equivalent without backpassing

mainExplicit : Task {} *
mainExplicit =
    Task.await (Stdout.line "Step 1") \{} ->
        Task.await (Stdout.line "Step 2") \{} ->
            Task.await (Stdout.line "Step 3") \{} ->
                Task.ok {}

## Backpassing with values

computeSequence : Task I64 *
computeSequence =
    a <- Task.await (Task.ok 10)
    b <- Task.await (Task.ok 20)
    c <- Task.await (Task.ok a + b)
    Task.ok (c * 2)

## Backpassing with Result

Result ok err : [Ok ok, Err err]

parseAndDouble : Str -> Result I64 [ParseError]
parseAndDouble = \input ->
    num <- Result.try (parseNumber input)
    Ok (num * 2)

parseNumber : Str -> Result I64 [ParseError]
parseNumber = \str ->
    when Str.toI64 str is
        Ok n -> Ok n
        Err _ -> Err ParseError

## Chain multiple Result operations

processChain : Str -> Result I64 [ParseError, DivisionByZero]
processChain = \input ->
    a <- Result.try (parseNumber input)
    b <- Result.try (safeDivide a 2)
    c <- Result.try (safeDivide b 3)
    Ok c

safeDivide : I64, I64 -> Result I64 [DivisionByZero]
safeDivide = \a, b ->
    if b == 0 then
        Err DivisionByZero
    else
        Ok (a // b)

## Backpassing with List operations

doubleAll : List I64 -> List I64
doubleAll = \list ->
    n <- List.map list
    n * 2

filterAndMap : List I64 -> List Str
filterAndMap = \list ->
    n <- List.keepIf list (\x -> x > 0)
        |> List.map
    Num.toStr n

## Nested backpassing

nestedExample : Task (List I64) *
nestedExample =
    items <- Task.await (Task.ok [1, 2, 3, 4, 5])

    processed = List.map items \n ->
        doubled <- (\f -> f (n * 2))
        incremented <- (\f -> f (doubled + 1))
        incremented

    Task.ok processed

## Backpassing with conditional

conditionalBackpass : Bool -> Task Str *
conditionalBackpass = \flag ->
    value <-
        if flag then
            Task.ok "enabled"
        else
            Task.ok "disabled"
        |> Task.await

    Task.ok (Str.concat "Status: " value)

## Pattern matching in backpassing

matchBackpass : Result I64 Str -> Task I64 *
matchBackpass = \result ->
    value <- Task.await
        (when result is
            Ok n -> Task.ok n
            Err _ -> Task.ok 0)

    Task.ok (value * 2)

## Backpassing for Option handling

Option a : [Just a, Nothing]

withDefault : Option a, a -> a
withDefault = \option, default ->
    value <- (\f ->
        when option is
            Just v -> f v
            Nothing -> default)
    value
