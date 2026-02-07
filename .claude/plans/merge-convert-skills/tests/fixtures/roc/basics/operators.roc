# Operators in Roc
#
# Demonstrates operator usage and precedence.

module [arithmetic, comparison, logical, bitwise]

## Arithmetic operators

arithmetic : I64 -> I64
arithmetic = \n ->
    result1 = n + 10
    result2 = n - 5
    result3 = n * 2
    result4 = n // 3  # Integer division
    result5 = Num.rem n 7  # Remainder

    result1 + result2 + result3 + result4 + result5

## Floating point arithmetic

floatArithmetic : F64 -> F64
floatArithmetic = \x ->
    y = x + 1.5
    z = x - 0.5
    w = x * 2.0
    v = x / 4.0

    y + z + w + v

## Comparison operators

comparison : I64, I64 -> Bool
comparison = \a, b ->
    eq = a == b
    neq = a != b
    lt = a < b
    lte = a <= b
    gt = a > b
    gte = a >= b

    eq || neq || lt || lte || gt || gte

## Logical operators

logical : Bool, Bool -> Bool
logical = \a, b ->
    andResult = a && b
    orResult = a || b
    notA = !a
    notB = !b

    (andResult || orResult) && !(notA && notB)

## String concatenation

stringConcat : Str, Str -> Str
stringConcat = \a, b ->
    Str.concat a b

## List operations

listOps : List I64, List I64 -> List I64
listOps = \xs, ys ->
    List.concat xs ys

## Pipe operator usage

pipeExample : I64 -> I64
pipeExample = \n ->
    n
    |> (\x -> x * 2)
    |> (\x -> x + 1)
    |> (\x -> x * 3)

## Backpassing (reverse pipe)

backpassExample : I64 -> I64
backpassExample = \n ->
    doubled <- (\f -> f (n * 2))
    incremented <- (\f -> f (doubled + 1))
    incremented * 3
