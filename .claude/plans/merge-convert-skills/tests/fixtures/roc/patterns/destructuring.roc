# Destructuring Patterns
#
# Demonstrates various destructuring techniques in Roc.

module [destructRecord, destructTuple, destructList, destructNested]

## Record destructuring in function parameters

destructRecord : { name : Str, age : U8 } -> Str
destructRecord = \{ name, age } ->
    Str.concat name (Str.concat " is " (Str.concat (Num.toStr age) " years old"))

## Partial record destructuring

getNameOnly : { name : Str }* -> Str
getNameOnly = \{ name } ->
    name

## Tuple destructuring

swapTuple : (a, b) -> (b, a)
swapTuple = \(first, second) ->
    (second, first)

destructTuple : (I64, Str, Bool) -> Str
destructTuple = \(num, text, flag) ->
    flagStr = if flag then "true" else "false"
    Str.concat (Num.toStr num) (Str.concat ", " (Str.concat text (Str.concat ", " flagStr)))

## List destructuring

firstElement : List a -> [Just a, Nothing]
firstElement = \list ->
    when list is
        [first, ..] -> Just first
        [] -> Nothing

firstTwo : List a -> [Both a a, One a, None]
firstTwo = \list ->
    when list is
        [first, second, ..] -> Both first second
        [first] -> One first
        [] -> None

## Rest patterns

splitFirst : List a -> [Split a (List a), Empty]
splitFirst = \list ->
    when list is
        [first, .. as rest] -> Split first rest
        [] -> Empty

## Nested destructuring

Person : { name : Str, address : { city : Str, zip : Str } }

getCity : Person -> Str
getCity = \{ address: { city } } ->
    city

## Destructuring in let bindings

processCoords : { x : I64, y : I64 } -> I64
processCoords = \point ->
    { x, y } = point
    x * x + y * y

## Multiple levels of destructuring

ComplexData : {
    meta : { id : U64, version : U8 },
    payload : { items : List Str, count : U64 },
}

extractInfo : ComplexData -> { id : U64, firstItem : [Just Str, Nothing] }
extractInfo = \{ meta: { id }, payload: { items } } ->
    firstItem = when items is
        [first, ..] -> Just first
        [] -> Nothing
    { id, firstItem }

## Ignoring parts with underscore

ignoreMiddle : (a, b, c) -> (a, c)
ignoreMiddle = \(first, _, third) ->
    (first, third)

## Combined patterns

Response : [
    Success { data : Str, code : U16 },
    Failure { error : Str, code : U16 },
]

getCode : Response -> U16
getCode = \response ->
    when response is
        Success { code } -> code
        Failure { code } -> code

getMessage : Response -> Str
getMessage = \response ->
    when response is
        Success { data } -> data
        Failure { error } -> error

## Destructuring with type annotation

Point : { x : F64, y : F64 }

distance : Point, Point -> F64
distance = \{ x: x1, y: y1 }, { x: x2, y: y2 } ->
    dx = x2 - x1
    dy = y2 - y1
    Num.sqrt (dx * dx + dy * dy)
