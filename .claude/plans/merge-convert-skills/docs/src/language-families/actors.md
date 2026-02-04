# Actor Model Family

> Concurrency model where isolated actors communicate exclusively via asynchronous message passing.

## Overview

The actor model provides concurrency through:

- **Isolation** - Each actor has private state
- **Message passing** - Asynchronous, ordered per sender
- **Location transparency** - Actors can be local or remote
- **Fault tolerance** - Supervision hierarchies

## Base Families

This is a **feature family** primarily associated with [BEAM](beam.md) languages and libraries for other families.

## Languages & Libraries

| Implementation | Base Family | Notes |
|----------------|-------------|-------|
| Erlang/Elixir | BEAM | Native processes |
| Akka (Scala/Java) | ML-FP / Managed-OOP | Actor library |
| Swift actors | Apple | Swift 5.5+ native |
| Pony | Systems | Actor + capabilities |
| Orleans (.NET) | Managed-OOP | Virtual actors |

## Key Concepts

### Actor Definition

```elixir
# Elixir GenServer
defmodule Counter do
  use GenServer

  def init(count), do: {:ok, count}

  def handle_call(:get, _from, count) do
    {:reply, count, count}
  end

  def handle_cast(:increment, count) do
    {:noreply, count + 1}
  end
end
```

```scala
// Akka Typed
object Counter {
  sealed trait Command
  case object Increment extends Command
  case class Get(replyTo: ActorRef[Int]) extends Command

  def apply(): Behavior[Command] = counter(0)

  private def counter(count: Int): Behavior[Command] =
    Behaviors.receive { (context, message) =>
      message match {
        case Increment => counter(count + 1)
        case Get(replyTo) =>
          replyTo ! count
          Behaviors.same
      }
    }
}
```

```swift
// Swift actor
actor Counter {
    private var count = 0

    func increment() { count += 1 }
    func get() -> Int { count }
}

// Usage (await required)
let counter = Counter()
await counter.increment()
print(await counter.get())
```

### Supervision

```elixir
# Supervision tree
children = [
  {Counter, 0},
  {Logger, []},
]
Supervisor.start_link(children, strategy: :one_for_one)
```

## Conversion Considerations

### Converting FROM Actors

**What's hard:**

- Actor isolation → shared state (lose guarantees)
- Supervision → exception handling (different model)
- Location transparency → explicit distribution

### Converting TO Actors

**What maps well:**

- Event handlers → actors
- State machines → actor behaviors
- Worker pools → actor pools

**What requires redesign:**

- Shared mutable state → actor state
- Locks/mutexes → message ordering
- Callbacks → message replies

## Sources

- [BEAM Book](https://blog.stenmans.org/theBeamBook/)
- [Akka Documentation](https://doc.akka.io/)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)

## See Also

- [BEAM](beam.md) - Native actor support
- [ML-FP](ml-fp.md) - Akka on Scala
- [Overview](overview.md) - Comparison matrices
