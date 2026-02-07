# Pattern Matching with when...is
#
# Demonstrates Roc's pattern matching capabilities.

module [matchNumber, matchList, matchTuple, matchRecord, matchNested]

## Simple value matching

matchNumber : I64 -> Str
matchNumber = \n ->
    when n is
        0 -> "zero"
        1 -> "one"
        2 -> "two"
        _ -> "many"

## Range-like matching with guards

classifyNumber : I64 -> Str
classifyNumber = \n ->
    when n is
        0 -> "zero"
        x if x < 0 -> "negative"
        x if x <= 10 -> "small positive"
        x if x <= 100 -> "medium positive"
        _ -> "large positive"

## List pattern matching

matchList : List a -> Str
matchList = \list ->
    when list is
        [] -> "empty"
        [_] -> "single"
        [_, _] -> "pair"
        [_, _, _] -> "triple"
        _ -> "many elements"

## Destructuring list head and tail

sumList : List I64 -> I64
sumList = \list ->
    when list is
        [] -> 0
        [first, .. as rest] -> first + sumList rest

## Tuple pattern matching

matchTuple : (I64, Str) -> Str
matchTuple = \pair ->
    when pair is
        (0, s) -> Str.concat "Zero with: " s
        (1, "one") -> "One and one"
        (n, s) -> Str.concat (Num.toStr n) (Str.concat " with " s)

## Record pattern matching

matchRecord : { status : [Ok, Error Str], value : I64 } -> Str
matchRecord = \record ->
    when record is
        { status: Ok, value: 0 } -> "OK with zero"
        { status: Ok, value } -> Str.concat "OK: " (Num.toStr value)
        { status: Error msg, value: _ } -> Str.concat "Error: " msg

## Nested pattern matching

matchNested : { outer : { inner : I64 } } -> I64
matchNested = \data ->
    when data is
        { outer: { inner: n } } -> n * 2

## Tag union pattern matching with payloads

Result a e : [Ok a, Err e]

handleResult : Result I64 Str -> Str
handleResult = \result ->
    when result is
        Ok 0 -> "Zero result"
        Ok n if n > 0 -> Str.concat "Positive: " (Num.toStr n)
        Ok n -> Str.concat "Negative: " (Num.toStr n)
        Err msg -> Str.concat "Error: " msg

## Multiple patterns with same arm

isWeekend : [Mon, Tue, Wed, Thu, Fri, Sat, Sun] -> Bool
isWeekend = \day ->
    when day is
        Sat | Sun -> Bool.true
        _ -> Bool.false

## Exhaustive matching verification

Direction : [North, South, East, West]

opposite : Direction -> Direction
opposite = \dir ->
    when dir is
        North -> South
        South -> North
        East -> West
        West -> East

## As-patterns

processWithOriginal : { x : I64, y : I64 } -> { original : { x : I64, y : I64 }, sum : I64 }
processWithOriginal = \point ->
    when point is
        { x, y } as original -> { original, sum: x + y }

## Matching on boolean

boolToStr : Bool -> Str
boolToStr = \b ->
    when b is
        Bool.true -> "yes"
        Bool.false -> "no"

## Complex nested patterns

Tree a : [Empty, Node a (Tree a) (Tree a)]

treeToList : Tree a -> List a
treeToList = \tree ->
    when tree is
        Empty -> []
        Node value Empty Empty -> [value]
        Node value left Empty -> List.concat (treeToList left) [value]
        Node value Empty right -> List.concat [value] (treeToList right)
        Node value left right ->
            leftList = treeToList left
            rightList = treeToList right
            List.concat (List.concat leftList [value]) rightList
