# List Operations
#
# Demonstrates common list operations in Roc.

module [map, filter, fold, transform, combine]

## Basic map

doubleAll : List I64 -> List I64
doubleAll = \list ->
    List.map list (\n -> n * 2)

## Map with index

withIndex : List a -> List { index : U64, value : a }
withIndex = \list ->
    List.mapWithIndex list \value, index ->
        { index, value }

## Filter

keepPositive : List I64 -> List I64
keepPositive = \list ->
    List.keepIf list (\n -> n > 0)

removeEmpty : List Str -> List Str
removeEmpty = \list ->
    List.dropIf list Str.isEmpty

## Fold (reduce)

sum : List I64 -> I64
sum = \list ->
    List.walk list 0 (\acc, n -> acc + n)

product : List I64 -> I64
product = \list ->
    List.walk list 1 (\acc, n -> acc * n)

## Fold with initial value

concat : List Str -> Str
concat = \list ->
    List.walk list "" Str.concat

## Right fold

sumRight : List I64 -> I64
sumRight = \list ->
    List.walkBackwards list 0 (\acc, n -> acc + n)

## Find operations

findFirst : List a, (a -> Bool) -> [Found a, NotFound]
findFirst = \list, predicate ->
    when List.findFirst list predicate is
        Ok value -> Found value
        Err _ -> NotFound

findIndex : List a, (a -> Bool) -> [Found U64, NotFound]
findIndex = \list, predicate ->
    when List.findFirstIndex list predicate is
        Ok index -> Found index
        Err _ -> NotFound

## Check operations

allPositive : List I64 -> Bool
allPositive = \list ->
    List.all list (\n -> n > 0)

anyNegative : List I64 -> Bool
anyNegative = \list ->
    List.any list (\n -> n < 0)

## Length and empty checks

isEmpty : List a -> Bool
isEmpty = \list ->
    List.isEmpty list

length : List a -> U64
length = \list ->
    List.len list

## Concatenation

append : List a, a -> List a
append = \list, item ->
    List.append list item

prepend : List a, a -> List a
prepend = \list, item ->
    List.prepend list item

join : List a, List a -> List a
join = \list1, list2 ->
    List.concat list1 list2

## Flattening

flatten : List (List a) -> List a
flatten = \lists ->
    List.join lists

flatMap : List a, (a -> List b) -> List b
flatMap = \list, f ->
    list
    |> List.map f
    |> List.join

## Sorting

sortAsc : List I64 -> List I64
sortAsc = \list ->
    List.sortAsc list

sortDesc : List I64 -> List I64
sortDesc = \list ->
    List.sortDesc list

sortBy : List a, (a -> I64) -> List a
sortBy = \list, keyFn ->
    List.sortWith list \a, b ->
        keyA = keyFn a
        keyB = keyFn b
        if keyA < keyB then LT
        else if keyA > keyB then GT
        else EQ

## Unique elements

unique : List a -> List a where a implements Eq
unique = \list ->
    List.walk list [] \acc, item ->
        if List.contains acc item then
            acc
        else
            List.append acc item

## Grouping

groupBy : List a, (a -> k) -> Dict k (List a) where k implements Hash & Eq
groupBy = \list, keyFn ->
    List.walk list (Dict.empty {}) \acc, item ->
        key = keyFn item
        when Dict.get acc key is
            Ok existing -> Dict.insert acc key (List.append existing item)
            Err _ -> Dict.insert acc key [item]

## Partition

partition : List a, (a -> Bool) -> { matching : List a, notMatching : List a }
partition = \list, predicate ->
    List.walk list { matching: [], notMatching: [] } \{ matching, notMatching }, item ->
        if predicate item then
            { matching: List.append matching item, notMatching }
        else
            { matching, notMatching: List.append notMatching item }

## Take and drop

takeFirst : List a, U64 -> List a
takeFirst = \list, count ->
    List.takeFirst list count

dropFirst : List a, U64 -> List a
dropFirst = \list, count ->
    List.dropFirst list count

## Zip operations

zip : List a, List b -> List (a, b)
zip = \list1, list2 ->
    List.map2 list1 list2 \a, b -> (a, b)

zipWith : List a, List b, (a, b -> c) -> List c
zipWith = \list1, list2, f ->
    List.map2 list1 list2 f
