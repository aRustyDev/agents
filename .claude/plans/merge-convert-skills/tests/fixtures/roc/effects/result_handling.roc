# Result Type Handling
#
# Demonstrates explicit error handling with Result type.

module [Result, Ok, Err, parseNumber, divideBy, safeDivide, chainResults]

## Result type definition (builtin, shown for reference)

Result ok err : [Ok ok, Err err]

## Simple Result creation

parseNumber : Str -> Result I64 [InvalidNumber]
parseNumber = \input ->
    when Str.toI64 input is
        Ok n -> Ok n
        Err _ -> Err InvalidNumber

## Division with error handling

DivisionError : [DivisionByZero]

divideBy : I64, I64 -> Result I64 DivisionError
divideBy = \a, b ->
    if b == 0 then
        Err DivisionByZero
    else
        Ok (a // b)

## Safe operations returning Result

safeDivide : F64, F64 -> Result F64 [DivisionByZero, Overflow, Underflow]
safeDivide = \a, b ->
    if b == 0.0 then
        Err DivisionByZero
    else
        result = a / b
        if Num.isInfinite result then
            Err Overflow
        else if Num.isNaN result then
            Err Underflow
        else
            Ok result

## Mapping over Result

mapResult : Result a e, (a -> b) -> Result b e
mapResult = \result, f ->
    when result is
        Ok value -> Ok (f value)
        Err e -> Err e

## Flat mapping (and-then pattern)

andThen : Result a e, (a -> Result b e) -> Result b e
andThen = \result, f ->
    when result is
        Ok value -> f value
        Err e -> Err e

## Chaining multiple Result operations

chainResults : Str -> Result I64 [InvalidNumber, DivisionByZero]
chainResults = \input ->
    parseNumber input
    |> andThen \n -> divideBy n 2
    |> mapResult \n -> n + 1

## Error mapping

mapErr : Result a e1, (e1 -> e2) -> Result a e2
mapErr = \result, f ->
    when result is
        Ok value -> Ok value
        Err e -> Err (f e)

## Unwrapping with default

unwrapOr : Result a e, a -> a
unwrapOr = \result, default ->
    when result is
        Ok value -> value
        Err _ -> default

## Unwrapping with default computation

unwrapOrElse : Result a e, (e -> a) -> a
unwrapOrElse = \result, f ->
    when result is
        Ok value -> value
        Err e -> f e

## Combining Results

combine : Result a e, Result b e -> Result (a, b) e
combine = \r1, r2 ->
    when (r1, r2) is
        (Ok a, Ok b) -> Ok (a, b)
        (Err e, _) -> Err e
        (_, Err e) -> Err e

## Sequence a list of Results

sequence : List (Result a e) -> Result (List a) e
sequence = \results ->
    List.walkUntil results (Ok []) \acc, result ->
        when (acc, result) is
            (Ok list, Ok value) -> Continue (Ok (List.append list value))
            (Err e, _) -> Break (Err e)
            (_, Err e) -> Break (Err e)

## Try pattern (early return simulation)

ParseError : [InvalidFormat, MissingField Str, InvalidValue Str]

parseConfig : Str -> Result { host : Str, port : I64 } ParseError
parseConfig = \input ->
    lines = Str.split input "\n"

    hostLine <- Result.try (List.first lines |> Result.mapErr \_ -> MissingField "host")
    portLine <- Result.try (List.get lines 1 |> Result.mapErr \_ -> MissingField "port")

    host <- Result.try (parseHostLine hostLine)
    port <- Result.try (parsePortLine portLine)

    Ok { host, port }

parseHostLine : Str -> Result Str ParseError
parseHostLine = \line ->
    when Str.splitFirst line "=" is
        Ok { before: "host", after } -> Ok (Str.trim after)
        _ -> Err InvalidFormat

parsePortLine : Str -> Result I64 ParseError
parsePortLine = \line ->
    when Str.splitFirst line "=" is
        Ok { before: "port", after } ->
            Str.toI64 (Str.trim after)
            |> Result.mapErr \_ -> InvalidValue "port"
        _ -> Err InvalidFormat
