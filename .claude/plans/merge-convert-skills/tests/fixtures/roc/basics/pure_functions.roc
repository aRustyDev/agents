# Pure Functions in Roc
#
# Demonstrates pure function patterns - the foundation of Roc.

module [double, triple, add, multiply, identity, compose, pipe]

## Simple pure functions

double : I64 -> I64
double = \n ->
    n * 2

triple : I64 -> I64
triple = \n ->
    n * 3

## Binary functions

add : I64, I64 -> I64
add = \a, b ->
    a + b

multiply : I64, I64 -> I64
multiply = \a, b ->
    a * b

## Generic identity function

identity : a -> a
identity = \x ->
    x

## Function composition

compose : (b -> c), (a -> b) -> (a -> c)
compose = \f, g ->
    \x -> f (g x)

## Pipe-style composition

pipe : a, (a -> b) -> b
pipe = \x, f ->
    f x

## Curried function example

addCurried : I64 -> (I64 -> I64)
addCurried = \a ->
    \b -> a + b

## Point-free style

doubleAll : List I64 -> List I64
doubleAll = List.map double

## Higher-order functions

applyTwice : (a -> a), a -> a
applyTwice = \f, x ->
    f (f x)

mapBoth : (a -> b), (a, a) -> (b, b)
mapBoth = \f, (x, y) ->
    (f x, f y)
