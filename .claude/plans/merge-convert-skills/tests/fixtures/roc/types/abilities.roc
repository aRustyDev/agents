# Abilities in Roc
#
# Demonstrates Roc's type class system via abilities.

module [Eq, Hash, Ordering, compare, equal, hashValue]

## Custom types for ability demonstration

Point : { x : I64, y : I64 }

Color : [Red, Green, Blue]

Person : {
    name : Str,
    age : U8,
}

## Implementing Eq ability (value equality)

eqPoint : Point, Point -> Bool
eqPoint = \p1, p2 ->
    p1.x == p2.x && p1.y == p2.y

eqColor : Color, Color -> Bool
eqColor = \c1, c2 ->
    when (c1, c2) is
        (Red, Red) -> Bool.true
        (Green, Green) -> Bool.true
        (Blue, Blue) -> Bool.true
        _ -> Bool.false

## Implementing Hash ability

hashPoint : Point -> U64
hashPoint = \{ x, y } ->
    # Simple hash combining
    xHash = Num.toU64 (Num.abs x)
    yHash = Num.toU64 (Num.abs y)
    Num.bitwiseXor xHash (yHash * 31)

hashColor : Color -> U64
hashColor = \color ->
    when color is
        Red -> 0
        Green -> 1
        Blue -> 2

## Ordering for comparison

Ordering : [LT, EQ, GT]

compareI64 : I64, I64 -> Ordering
compareI64 = \a, b ->
    if a < b then LT
    else if a > b then GT
    else EQ

comparePoint : Point, Point -> Ordering
comparePoint = \p1, p2 ->
    when compareI64 p1.x p2.x is
        LT -> LT
        GT -> GT
        EQ -> compareI64 p1.y p2.y

## Generic functions using abilities

sortBy : List a, (a, a -> Ordering) -> List a
sortBy = \list, cmp ->
    # Simplified bubble sort for demonstration
    List.sortWith list (\a, b ->
        when cmp a b is
            LT -> LT
            EQ -> EQ
            GT -> GT
    )

## Finding in list with custom equality

findWith : List a, a, (a, a -> Bool) -> [Found a, NotFound]
findWith = \list, target, eq ->
    when List.findFirst list (\item -> eq item target) is
        Ok found -> Found found
        Err _ -> NotFound

## Deduplication with custom equality

dedupWith : List a, (a, a -> Bool) -> List a
dedupWith = \list, eq ->
    List.walk list [] \acc, item ->
        alreadyExists = List.any acc (\existing -> eq existing item)
        if alreadyExists then acc else List.append acc item

## Type with multiple ability implementations

Vector3 : { x : F64, y : F64, z : F64 }

eqVector3 : Vector3, Vector3 -> Bool
eqVector3 = \v1, v2 ->
    v1.x == v2.x && v1.y == v2.y && v1.z == v2.z

hashVector3 : Vector3 -> U64
hashVector3 = \{ x, y, z } ->
    # Convert to bits and combine
    xBits = Num.toU64 (Num.round x)
    yBits = Num.toU64 (Num.round y)
    zBits = Num.toU64 (Num.round z)
    Num.bitwiseXor xBits (Num.bitwiseXor (yBits * 31) (zBits * 961))

compareVector3 : Vector3, Vector3 -> Ordering
compareVector3 = \v1, v2 ->
    # Compare by magnitude
    mag1 = v1.x * v1.x + v1.y * v1.y + v1.z * v1.z
    mag2 = v2.x * v2.x + v2.y * v2.y + v2.z * v2.z
    if mag1 < mag2 then LT
    else if mag1 > mag2 then GT
    else EQ
