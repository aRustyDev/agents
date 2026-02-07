# Guard Expressions
#
# Demonstrates conditional guards in pattern matching.

module [classifyAge, processValue, validateInput]

## Basic guard expressions

classifyAge : U8 -> Str
classifyAge = \age ->
    when age is
        0 -> "newborn"
        n if n < 13 -> "child"
        n if n < 20 -> "teenager"
        n if n < 65 -> "adult"
        _ -> "senior"

## Multiple conditions in guards

classifyNumber : I64 -> Str
classifyNumber = \n ->
    when n is
        0 -> "zero"
        x if x > 0 && x < 10 -> "small positive"
        x if x >= 10 && x < 100 -> "medium positive"
        x if x >= 100 -> "large positive"
        x if x < 0 && x > -10 -> "small negative"
        x if x <= -10 && x > -100 -> "medium negative"
        _ -> "large negative"

## Guards with record fields

Person : { name : Str, age : U8, isStudent : Bool }

describeStudent : Person -> Str
describeStudent = \person ->
    when person is
        { isStudent: Bool.true, age } if age < 18 -> "minor student"
        { isStudent: Bool.true, age } if age < 25 -> "young adult student"
        { isStudent: Bool.true } -> "adult student"
        { age } if age < 18 -> "minor non-student"
        _ -> "adult non-student"

## Guards with function calls

isEven : I64 -> Bool
isEven = \n -> Num.rem n 2 == 0

processValue : I64 -> Str
processValue = \n ->
    when n is
        x if x < 0 -> "negative"
        x if isEven x -> "positive even"
        _ -> "positive odd"

## Guards with list checks

categorizeList : List a -> Str
categorizeList = \list ->
    len = List.len list
    when list is
        [] -> "empty"
        _ if len == 1 -> "singleton"
        _ if len < 5 -> "small"
        _ if len < 20 -> "medium"
        _ -> "large"

## Combining pattern matching with guards

Result a e : [Ok a, Err e]

validateInput : Result I64 Str -> Str
validateInput = \result ->
    when result is
        Ok n if n < 0 -> "Error: negative value"
        Ok n if n > 1000 -> "Error: value too large"
        Ok 0 -> "Warning: zero value"
        Ok n -> Str.concat "Valid: " (Num.toStr n)
        Err msg -> Str.concat "Error: " msg

## Guards with string operations

classifyString : Str -> Str
classifyString = \s ->
    len = Str.countUtf8Bytes s
    when s is
        "" -> "empty"
        _ if len == 1 -> "single character"
        _ if len < 10 -> "short"
        _ if len < 100 -> "medium"
        _ -> "long"

## Complex guard conditions

Range : { min : I64, max : I64 }

inRange : I64, Range -> Bool
inRange = \value, { min, max } ->
    value >= min && value <= max

classifyValue : I64, Range, Range, Range -> Str
classifyValue = \value, low, mid, high ->
    when value is
        _ if inRange value low -> "low"
        _ if inRange value mid -> "medium"
        _ if inRange value high -> "high"
        _ -> "out of range"

## Guard precedence examples

processData : { x : I64, y : I64 } -> Str
processData = \point ->
    when point is
        { x: 0, y: 0 } -> "origin"
        { x: 0, y } if y > 0 -> "positive y-axis"
        { x: 0, y } if y < 0 -> "negative y-axis"
        { x, y: 0 } if x > 0 -> "positive x-axis"
        { x, y: 0 } if x < 0 -> "negative x-axis"
        { x, y } if x > 0 && y > 0 -> "quadrant I"
        { x, y } if x < 0 && y > 0 -> "quadrant II"
        { x, y } if x < 0 && y < 0 -> "quadrant III"
        _ -> "quadrant IV"
