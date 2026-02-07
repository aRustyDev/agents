# Task Basics
#
# Demonstrates Roc's Task type for effects.

app [main] { pf: platform "https://github.com/roc-lang/basic-cli/releases/download/0.10.0/vNe6s9hWzoTZtFmNkvSvMl63s9gxRRrKX7lRsnq6NDY.tar.br" }

import pf.Stdout
import pf.Task exposing [Task]

## Main entry point - must return a Task

main : Task {} *
main =
    Stdout.line "Hello, Roc!"

## Simple effectful function

printGreeting : Str -> Task {} *
printGreeting = \name ->
    Stdout.line (Str.concat "Hello, " name)

## Chaining tasks with Task.await (backpassing style)

chainedGreeting : Task {} *
chainedGreeting =
    {} <- Stdout.line "First line"
    {} <- Stdout.line "Second line"
    Stdout.line "Third line"

## Chaining with explicit await

explicitChain : Task {} *
explicitChain =
    Task.await (Stdout.line "Step 1") \{} ->
        Task.await (Stdout.line "Step 2") \{} ->
            Stdout.line "Step 3"

## Mapping over Task results

mappedTask : Task I64 *
mappedTask =
    Task.ok 42
    |> Task.map (\n -> n * 2)

## Sequence of pure computations lifted to Task

pureToTask : I64 -> Task I64 *
pureToTask = \n ->
    Task.ok (n * 2 + 1)

## Task that always succeeds

alwaysSucceed : Task Str *
alwaysSucceed =
    Task.ok "success"

## Task that represents failure

TaskError : [NetworkError, ParseError Str, NotFound]

alwaysFail : Task a TaskError
alwaysFail =
    Task.err NotFound

## Handling Task errors

handleErrors : Task I64 [NotFound, InvalidInput] -> Task I64 *
handleErrors = \task ->
    Task.onErr task \err ->
        when err is
            NotFound -> Task.ok 0
            InvalidInput -> Task.ok -1

## Combining multiple Tasks

parallelTasks : Task (I64, I64) *
parallelTasks =
    task1 = Task.ok 10
    task2 = Task.ok 20

    n1 <- Task.await task1
    n2 <- Task.await task2

    Task.ok (n1, n2)

## Forever loop (for servers)

# serverLoop : Task {} *
# serverLoop =
#     {} <- handleRequest
#     serverLoop

## Conditional Task execution

conditionalTask : Bool -> Task Str *
conditionalTask = \condition ->
    if condition then
        Task.ok "condition was true"
    else
        Task.ok "condition was false"
