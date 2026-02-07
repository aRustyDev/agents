# Tag Unions in Roc
#
# Demonstrates algebraic data types via tag unions.

module [Color, Shape, Result, Option, Tree, Json]

## Simple enum-like tag union

Color : [Red, Green, Blue, Yellow, Orange, Purple]

colorToHex : Color -> Str
colorToHex = \color ->
    when color is
        Red -> "#FF0000"
        Green -> "#00FF00"
        Blue -> "#0000FF"
        Yellow -> "#FFFF00"
        Orange -> "#FFA500"
        Purple -> "#800080"

## Tag union with payloads

Shape : [
    Circle F64,
    Rectangle F64 F64,
    Triangle F64 F64 F64,
    Point,
]

shapeArea : Shape -> F64
shapeArea = \shape ->
    when shape is
        Circle radius -> 3.14159 * radius * radius
        Rectangle width height -> width * height
        Triangle a b c ->
            # Heron's formula
            s = (a + b + c) / 2.0
            Num.sqrt (s * (s - a) * (s - b) * (s - c))
        Point -> 0.0

## Result type (like Rust's Result)

Result ok err : [Ok ok, Err err]

mapResult : Result a e, (a -> b) -> Result b e
mapResult = \result, f ->
    when result is
        Ok value -> Ok (f value)
        Err e -> Err e

flatMapResult : Result a e, (a -> Result b e) -> Result b e
flatMapResult = \result, f ->
    when result is
        Ok value -> f value
        Err e -> Err e

## Option type (like Rust's Option)

Option a : [Just a, Nothing]

mapOption : Option a, (a -> b) -> Option b
mapOption = \option, f ->
    when option is
        Just value -> Just (f value)
        Nothing -> Nothing

unwrapOr : Option a, a -> a
unwrapOr = \option, default ->
    when option is
        Just value -> value
        Nothing -> default

## Recursive tag union (binary tree)

Tree a : [
    Empty,
    Node a (Tree a) (Tree a),
]

treeSize : Tree a -> U64
treeSize = \tree ->
    when tree is
        Empty -> 0
        Node _ left right -> 1 + treeSize left + treeSize right

treeDepth : Tree a -> U64
treeDepth = \tree ->
    when tree is
        Empty -> 0
        Node _ left right ->
            leftDepth = treeDepth left
            rightDepth = treeDepth right
            1 + (if leftDepth > rightDepth then leftDepth else rightDepth)

insertTree : Tree (Num a), Num a -> Tree (Num a)
insertTree = \tree, value ->
    when tree is
        Empty -> Node value Empty Empty
        Node nodeValue left right ->
            if value < nodeValue then
                Node nodeValue (insertTree left value) right
            else
                Node nodeValue left (insertTree right value)

## JSON-like recursive type

Json : [
    Null,
    Bool Bool,
    Number F64,
    String Str,
    Array (List Json),
    Object (Dict Str Json),
]

jsonToStr : Json -> Str
jsonToStr = \json ->
    when json is
        Null -> "null"
        Bool b -> if b then "true" else "false"
        Number n -> Num.toStr n
        String s -> Str.concat "\"" (Str.concat s "\"")
        Array items ->
            inner = items |> List.map jsonToStr |> Str.joinWith ", "
            Str.concat "[" (Str.concat inner "]")
        Object _ -> "{...}"  # Simplified

## Open tag unions (extensible)

handleStatus : [Ok, Loading, Error Str]* -> Str
handleStatus = \status ->
    when status is
        Ok -> "Success!"
        Loading -> "Please wait..."
        Error msg -> Str.concat "Error: " msg
        _ -> "Unknown status"
