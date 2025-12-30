---
name: convert-erlang-scala
description: Converts Erlang code to idiomatic Scala while preserving functional programming patterns, actor model semantics through Akka, and fault-tolerance mechanisms. Use when converting Erlang applications, libraries, OTP behaviors, or concurrent systems to Scala, including supervision trees, gen_server patterns, distributed systems, and message-passing architectures on the JVM.
---

# Erlang to Scala Conversion

## Overview

This skill guides the conversion of Erlang code to idiomatic Scala while maintaining functional programming principles, concurrent programming patterns via Akka, and fault-tolerance capabilities. Scala provides strong functional programming support combined with object-oriented features on the JVM, making it suitable for porting Erlang applications while gaining access to the extensive Java/Scala ecosystem.

## Key Language Differences

### Type Systems
- **Erlang**: Dynamic typing with pattern matching
- **Scala**: Static typing with type inference, algebraic data types (sealed traits), and comprehensive pattern matching

### Concurrency Models
- **Erlang**: Actor model with lightweight processes (BEAM VM), message passing, process isolation
- **Scala**: Akka actors (JVM-based), futures/promises, parallel collections

### Runtime Environment
- **Erlang**: BEAM VM with hot code swapping, distributed computing, per-process garbage collection
- **Scala**: JVM with comprehensive standard library, Akka for distributed systems, shared heap garbage collection

## Core Conversion Patterns

### 1. Module and Function Definitions

**Erlang:**
```erlang
-module(calculator).
-export([add/2, multiply/2, power/2]).

add(X, Y) -> X + Y.

multiply(X, Y) -> X * Y.

power(X, N) when N > 0 -> X * power(X, N - 1);
power(_, 0) -> 1.
```

**Scala:**
```scala
object Calculator {
  def add(x: Int, y: Int): Int = x + y

  def multiply(x: Int, y: Int): Int = x * y

  def power(x: Int, n: Int): Int = n match {
    case 0 => 1
    case n if n > 0 => x * power(x, n - 1)
    case _ => throw new IllegalArgumentException("Negative exponent")
  }
}
```

### 2. Pattern Matching and Guards

**Erlang:**
```erlang
-spec classify(number()) -> atom().
classify(N) when N < 0 -> negative;
classify(0) -> zero;
classify(N) when N > 0 -> positive.

process_result({ok, Value}) -> {success, Value};
process_result({error, Reason}) -> {failure, Reason};
process_result(_) -> unknown.
```

**Scala:**
```scala
def classify(n: Int): Symbol = n match {
  case n if n < 0 => 'negative
  case 0 => 'zero
  case n if n > 0 => 'positive
}

// Using sealed traits for better type safety
sealed trait Result[+A]
case class Ok[A](value: A) extends Result[A]
case class Error(reason: String) extends Result[Nothing]

sealed trait ProcessedResult
case class Success(value: Any) extends ProcessedResult
case class Failure(reason: String) extends ProcessedResult
case object Unknown extends ProcessedResult

def processResult(result: Result[Any]): ProcessedResult = result match {
  case Ok(value) => Success(value)
  case Error(reason) => Failure(reason)
}
```

### 3. Records to Case Classes

**Erlang:**
```erlang
-record(person, {name, age, email}).

create_person(Name, Age, Email) ->
    #person{name=Name, age=Age, email=Email}.

get_name(#person{name=Name}) -> Name.

update_email(Person, NewEmail) ->
    Person#person{email=NewEmail}.
```

**Scala:**
```scala
case class Person(name: String, age: Int, email: String)

def createPerson(name: String, age: Int, email: String): Person =
  Person(name, age, email)

def getName(person: Person): String = person.name

def updateEmail(person: Person, newEmail: String): Person =
  person.copy(email = newEmail)
```

### 4. Lists and List Operations

**Erlang:**
```erlang
% List comprehensions
double_list(List) -> [X * 2 || X <- List].

filter_even(List) -> [X || X <- List, X rem 2 =:= 0].

% Recursive list processing
sum([]) -> 0;
sum([H|T]) -> H + sum(T).

map(_, []) -> [];
map(F, [H|T]) -> [F(H) | map(F, T)].
```

**Scala:**
```scala
// List operations with higher-order functions
def doubleList(list: List[Int]): List[Int] =
  list.map(_ * 2)
  // or: for (x <- list) yield x * 2

def filterEven(list: List[Int]): List[Int] =
  list.filter(_ % 2 == 0)
  // or: for (x <- list if x % 2 == 0) yield x

// Recursive list processing
def sum(list: List[Int]): Int = list match {
  case Nil => 0
  case h :: t => h + sum(t)
}

def map[A, B](f: A => B, list: List[A]): List[B] = list match {
  case Nil => Nil
  case h :: t => f(h) :: map(f, t)
}

// Built-in alternatives (preferred)
val summed = list.sum
val mapped = list.map(f)
```

### 5. Higher-Order Functions and Lambdas

**Erlang:**
```erlang
apply_twice(F, X) -> F(F(X)).

% Anonymous functions
Increment = fun(X) -> X + 1 end,
Result = apply_twice(Increment, 5). % Result = 7

% Partial application
add(X, Y) -> X + Y.
add_five(X) -> add(5, X).
```

**Scala:**
```scala
def applyTwice[A](f: A => A, x: A): A = f(f(x))

// Anonymous functions
val increment: Int => Int = _ + 1
val result = applyTwice(increment, 5) // result = 7

// Partial application
def add(x: Int, y: Int): Int = x + y
def addFive: Int => Int = add(5, _)
// or: val addFive = (x: Int) => add(5, x)
```

### 6. Actor Model / Process Communication

**Erlang:**
```erlang
-module(counter).
-export([start/0, increment/1, get_value/1, loop/1]).

start() ->
    spawn(fun() -> loop(0) end).

increment(Pid) ->
    Pid ! {increment, self()},
    receive
        {ok, NewValue} -> NewValue
    after 5000 ->
        timeout
    end.

get_value(Pid) ->
    Pid ! {get, self()},
    receive
        {value, V} -> V
    after 5000 ->
        timeout
    end.

loop(Count) ->
    receive
        {increment, From} ->
            NewCount = Count + 1,
            From ! {ok, NewCount},
            loop(NewCount);
        {get, From} ->
            From ! {value, Count},
            loop(Count);
        stop ->
            ok
    end.
```

**Scala (Akka):**
```scala
import akka.actor._
import akka.pattern.ask
import akka.util.Timeout
import scala.concurrent.duration._
import scala.concurrent.{Await, Future}

class Counter extends Actor {
  private var count = 0

  def receive: Receive = {
    case Increment =>
      count += 1
      sender() ! Ok(count)
    case Get =>
      sender() ! Value(count)
    case Stop =>
      context.stop(self)
  }
}

// Message definitions
case object Increment
case object Get
case class Ok(value: Int)
case class Value(count: Int)
case object Stop

// Usage
object CounterExample extends App {
  val system = ActorSystem("CounterSystem")
  val counter = system.actorOf(Props[Counter], "counter")

  implicit val timeout: Timeout = 5.seconds
  import system.dispatcher

  // Fire-and-forget (like Erlang's !)
  counter ! Increment

  // Request-response (like Erlang's receive)
  val future: Future[Value] = (counter ? Get).mapTo[Value]
  val Value(count) = Await.result(future, 5.seconds)

  counter ! Stop
  system.terminate()
}
```

### 7. gen_server Pattern

**Erlang:**
```erlang
-module(kv_store).
-behaviour(gen_server).
-export([start_link/0, get/1, put/2]).
-export([init/1, handle_call/3, handle_cast/2, terminate/2]).

start_link() ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [], []).

get(Key) ->
    gen_server:call(?MODULE, {get, Key}).

put(Key, Value) ->
    gen_server:cast(?MODULE, {put, Key, Value}).

init([]) ->
    {ok, #{}}.

handle_call({get, Key}, _From, State) ->
    Result = maps:get(Key, State, undefined),
    {reply, Result, State}.

handle_cast({put, Key, Value}, State) ->
    NewState = maps:put(Key, Value, State),
    {noreply, NewState}.

terminate(_Reason, _State) ->
    ok.
```

**Scala (Akka):**
```scala
import akka.actor._

class KVStore extends Actor {
  private var state: Map[String, Any] = Map.empty

  def receive: Receive = {
    case Get(key) =>
      sender() ! state.get(key)

    case Put(key, value) =>
      state = state + (key -> value)
  }

  override def postStop(): Unit = {
    // Cleanup logic (like terminate/2)
    println("KVStore stopped")
  }
}

case class Get(key: String)
case class Put(key: String, value: Any)

// Usage
object KVStoreExample extends App {
  val system = ActorSystem("KVSystem")
  val kvStore = system.actorOf(Props[KVStore], "kvStore")

  // Cast-like (fire-and-forget)
  kvStore ! Put("name", "Scala")
  kvStore ! Put("version", 3)

  // Call-like (request-response)
  import akka.pattern.ask
  import akka.util.Timeout
  import scala.concurrent.duration._
  import scala.concurrent.Await

  implicit val timeout: Timeout = 5.seconds
  val future = (kvStore ? Get("name")).mapTo[Option[Any]]
  val result = Await.result(future, 5.seconds)
  println(s"Result: $result")

  system.terminate()
}
```

### 8. Supervision and Fault Tolerance

**Erlang:**
```erlang
-module(my_supervisor).
-behaviour(supervisor).
-export([start_link/0, init/1]).

start_link() ->
    supervisor:start_link({local, ?MODULE}, ?MODULE, []).

init([]) ->
    ChildSpecs = [
        #{id => worker1,
          start => {my_worker, start_link, []},
          restart => permanent,
          shutdown => 5000,
          type => worker},
        #{id => worker2,
          start => {my_worker, start_link, []},
          restart => transient,
          shutdown => 5000,
          type => worker}
    ],
    {ok, {#{strategy => one_for_one,
            intensity => 5,
            period => 10}, ChildSpecs}}.
```

**Scala (Akka):**
```scala
import akka.actor._
import scala.concurrent.duration._

class MySupervisor extends Actor {
  override val supervisorStrategy = OneForOneStrategy(
    maxNrOfRetries = 5,
    withinTimeRange = 10.seconds
  ) {
    case _: ArithmeticException => SupervisorStrategy.Resume
    case _: NullPointerException => SupervisorStrategy.Restart
    case _: IllegalArgumentException => SupervisorStrategy.Stop
    case _: Exception => SupervisorStrategy.Escalate
  }

  val worker1 = context.actorOf(Props[MyWorker], "worker1")
  val worker2 = context.actorOf(Props[MyWorker], "worker2")

  def receive: Receive = {
    case msg => worker1 ! msg
  }
}

class MyWorker extends Actor {
  def receive: Receive = {
    case work: Work => processWork(work)
  }

  def processWork(work: Work): Unit = {
    // Work processing logic
    println(s"Processing: $work")
  }

  override def preStart(): Unit = {
    println(s"${self.path.name} starting")
  }

  override def postRestart(reason: Throwable): Unit = {
    println(s"${self.path.name} restarted due to: $reason")
  }
}

case class Work(data: String)
```

### 9. Error Handling

**Erlang:**
```erlang
safe_divide(_, 0) -> {error, division_by_zero};
safe_divide(X, Y) -> {ok, X / Y}.

% Try-catch
try_operation(Data) ->
    try
        risky_function(Data)
    catch
        error:badarg -> {error, bad_argument};
        error:Reason -> {error, Reason};
        throw:Value -> {thrown, Value}
    end.

% Let it crash philosophy
process_data(Data) ->
    % Process crashes if something goes wrong
    transform(Data).
```

**Scala:**
```scala
// Using Either for explicit error handling
sealed trait DivisionError
case object DivisionByZero extends DivisionError

def safeDivide(x: Double, y: Double): Either[DivisionError, Double] =
  if (y == 0) Left(DivisionByZero)
  else Right(x / y)

// Using Option for simple cases
def safeDivideOption(x: Double, y: Double): Option[Double] =
  if (y == 0) None
  else Some(x / y)

// Try-catch for exception handling
import scala.util.{Try, Success, Failure}

def tryOperation(data: String): Either[String, Int] =
  Try(riskyFunction(data)) match {
    case Success(value) => Right(value)
    case Failure(ex: IllegalArgumentException) => Left("bad_argument")
    case Failure(ex) => Left(ex.getMessage)
  }

// For-comprehension for chaining operations
def complexOperation(x: Int, y: Int): Either[String, Int] = for {
  divided <- safeDivide(x.toDouble, y.toDouble).left.map(_.toString)
  result <- Right(divided.toInt)
} yield result
```

### 10. Binary Pattern Matching

**Erlang:**
```erlang
parse_header(<<Type:8, Length:16/big, Rest/binary>>) ->
    {Type, Length, Rest}.

parse_packet(<<Magic:32/big, Version:8, Data/binary>>) ->
    {Magic, Version, Data}.

encode_header(Type, Length, Data) ->
    <<Type:8, Length:16/big, Data/binary>>.
```

**Scala:**
```scala
import akka.util.ByteString
import java.nio.ByteOrder

// Using Akka ByteString
def parseHeader(bytes: ByteString): Option[(Byte, Short, ByteString)] = {
  if (bytes.length < 3) None
  else {
    val iter = bytes.iterator
    val typ = iter.getByte
    val length = iter.getShort(ByteOrder.BIG_ENDIAN)
    val rest = bytes.drop(3)
    Some((typ, length, rest))
  }
}

// Using scodec for complex binary protocols
import scodec._
import scodec.bits._
import scodec.codecs._

case class Header(typ: Int, length: Int, data: ByteVector)

val headerCodec: Codec[Header] =
  (uint8 :: uint16 :: bytes).as[Header]

// Encoding
val encoded: BitVector = headerCodec.encode(Header(1, 256, hex"deadbeef")).require

// Decoding
val decoded: Header = headerCodec.decode(encoded).require.value
```

### 11. ETS Tables to Concurrent Collections

**Erlang:**
```erlang
start() ->
    ets:new(cache, [named_table, public, set]),
    ok.

insert(Key, Value) ->
    ets:insert(cache, {Key, Value}),
    ok.

lookup(Key) ->
    case ets:lookup(cache, Key) of
        [{Key, Value}] -> {ok, Value};
        [] -> {error, not_found}
    end.

delete(Key) ->
    ets:delete(cache, Key),
    ok.
```

**Scala:**
```scala
import java.util.concurrent.ConcurrentHashMap
import scala.jdk.CollectionConverters._

object Cache {
  private val cache = new ConcurrentHashMap[String, Any]().asScala

  def insert(key: String, value: Any): Unit =
    cache.put(key, value)

  def lookup(key: String): Option[Any] =
    cache.get(key)

  def delete(key: String): Unit =
    cache.remove(key)
}

// Or using an actor for state management
class CacheActor extends Actor {
  private var cache: Map[String, Any] = Map.empty

  def receive: Receive = {
    case Insert(k, v) =>
      cache = cache + (k -> v)
      sender() ! Done

    case Lookup(k) =>
      sender() ! cache.get(k)

    case Delete(k) =>
      cache = cache - k
      sender() ! Done
  }
}

case class Insert(key: String, value: Any)
case class Lookup(key: String)
case class Delete(key: String)
case object Done
```

### 12. Distributed Erlang to Akka Cluster

**Erlang:**
```erlang
% Send message to named process on remote node
send_to_node(Node, ProcessName, Message) ->
    {ProcessName, Node} ! Message.

% Register process globally
register_globally(Name, Pid) ->
    global:register_name(Name, Pid).

% Call remote process
call_remote(Node, Module, Function, Args) ->
    rpc:call(Node, Module, Function, Args).
```

**Scala (Akka Cluster):**
```scala
import akka.actor._
import akka.cluster.Cluster
import akka.cluster.routing._

// Remote actor communication
object DistributedExample {
  def sendToRemote(system: ActorSystem, path: String, message: Any): Unit = {
    val selection = system.actorSelection(path)
    selection ! message
  }

  // Cluster-aware routing
  def createClusterRouter(system: ActorSystem): ActorRef = {
    system.actorOf(
      ClusterRouterPool(
        local = akka.routing.RoundRobinPool(5),
        settings = ClusterRouterPoolSettings(
          totalInstances = 20,
          maxInstancesPerNode = 5,
          allowLocalRoutees = true
        )
      ).props(Props[Worker]),
      name = "workerRouter"
    )
  }
}

// Cluster singleton for global registration
import akka.cluster.singleton._

object SingletonExample {
  def createSingleton(system: ActorSystem): ActorRef = {
    system.actorOf(
      ClusterSingletonManager.props(
        singletonProps = Props[GlobalRegistry],
        terminationMessage = PoisonPill,
        settings = ClusterSingletonManagerSettings(system)
      ),
      name = "globalRegistry"
    )
  }
}

class GlobalRegistry extends Actor {
  private var registry: Map[String, ActorRef] = Map.empty

  def receive: Receive = {
    case Register(name, ref) =>
      registry = registry + (name -> ref)
      sender() ! Registered

    case Lookup(name) =>
      sender() ! registry.get(name)
  }
}

case class Register(name: String, ref: ActorRef)
case class Lookup(name: String)
case object Registered
```

## Conversion Strategy

### Step 1: Analyze Erlang Codebase
- Identify module structure and dependencies
- Map OTP behaviors (gen_server, gen_statem, gen_event, supervisor)
- Document message-passing patterns and process hierarchies
- List external dependencies and find Scala/Java equivalents
- Analyze distributed Erlang usage

### Step 2: Design Scala Architecture
- Plan package organization and module structure
- Design type hierarchy using sealed traits and case classes
- Choose concurrency framework (Akka actors, Akka Typed, or Cats Effect)
- Select fault-tolerance strategy (Akka supervision or custom)
- Plan distributed system architecture (Akka Cluster, gRPC)

### Step 3: Convert Core Logic
- Start with pure functions and data structures
- Convert pattern matching to Scala's match expressions
- Translate list operations to Scala collections
- Migrate error handling to Either/Option types or custom ADTs
- Convert records to case classes

### Step 4: Implement Concurrency
- Replace spawn/receive with Akka actors
- Convert gen_server to actor-based patterns
- Implement supervision hierarchies with Akka supervision strategies
- Add lifecycle callbacks (preStart, postStop, postRestart)

### Step 5: Handle Distribution
- Implement Akka Cluster for distributed scenarios
- Set up cluster routing and sharding
- Configure cluster singleton for global state
- Implement serialization for remote messages

### Step 6: Testing and Validation
- Port EUnit/CommonTest to ScalaTest or Specs2
- Test concurrent behaviors with Akka TestKit
- Validate message-passing semantics
- Property-based testing with ScalaCheck
- Performance testing and JVM tuning

## Common Libraries and Equivalents

| Erlang | Scala / JVM Equivalent |
|--------|----------------------|
| gen_server | Akka actors, Akka Typed |
| supervisor | Akka supervision |
| gen_statem | Akka FSM, Akka Typed behaviors |
| ETS | ConcurrentHashMap, Caffeine cache |
| Mnesia | Slick, Doobie, Quill (SQL databases) |
| httpc, hackney | Akka HTTP client, http4s, sttp |
| cowboy | Akka HTTP, http4s, Play Framework |
| jsx, jiffy (JSON) | Circe, Play JSON, spray-json |
| lager (logging) | Logback, Log4j2, scala-logging |
| poolboy | Akka routing, HikariCP (DB) |
| riak_core | Akka Cluster Sharding |

## Best Practices

### 1. Embrace Static Typing
- Use Scala's type system to catch errors at compile time
- Define sealed traits for algebraic data types
- Use type parameters and variance for generic code
- Leverage type classes (implicits) for polymorphism

### 2. Preserve Functional Patterns
- Keep functions pure where possible
- Use immutable data structures by default
- Leverage for-comprehensions for sequential operations
- Use pattern matching extensively

### 3. Adapt Concurrency Models
- Use Akka actors for actor-like behavior
- Consider Akka Typed for better type safety
- Use futures for asynchronous computations
- Implement backpressure with Akka Streams

### 4. Supervision Strategies
- Design supervision hierarchies carefully
- Use different strategies per error type
- Implement lifecycle hooks (preStart, postRestart)
- Monitor critical actors with death watch

### 5. Error Handling
- Prefer Either and Option over exceptions
- Use Try for exception-throwing operations
- Design error ADTs with sealed traits
- Use for-comprehensions for error propagation

### 6. Performance Considerations
- Profile JVM performance regularly
- Tune garbage collection settings
- Use specialized collections where appropriate
- Consider Akka Streams for backpressure
- Benchmark actor mailbox sizes

### 7. Testing
- Write unit tests with ScalaTest or Specs2
- Use Akka TestKit for actor testing
- Property-based testing with ScalaCheck
- Integration testing for distributed scenarios

## Example: Complete Application Conversion

### Erlang Chat Server
```erlang
-module(chat_server).
-behaviour(gen_server).
-export([start_link/0, join/2, leave/1, send_message/2]).
-export([init/1, handle_call/3, handle_cast/2, terminate/2]).

-record(state, {users = #{}}).

start_link() ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [], []).

init([]) ->
    {ok, #state{}}.

handle_call({join, Username, Pid}, _From, State = #state{users = Users}) ->
    monitor(process, Pid),
    NewUsers = Users#{Username => Pid},
    notify_all(NewUsers, {user_joined, Username}),
    {reply, ok, State#state{users = NewUsers}};

handle_call({leave, Username}, _From, State = #state{users = Users}) ->
    NewUsers = maps:remove(Username, Users),
    notify_all(NewUsers, {user_left, Username}),
    {reply, ok, State#state{users = NewUsers}}.

handle_cast({send_message, From, Message}, State = #state{users = Users}) ->
    notify_all(Users, {message, From, Message}),
    {noreply, State}.

terminate(_Reason, _State) ->
    ok.

notify_all(Users, Msg) ->
    maps:foreach(fun(_, Pid) -> Pid ! Msg end, Users).

join(Username, Pid) ->
    gen_server:call(?MODULE, {join, Username, Pid}).

leave(Username) ->
    gen_server:call(?MODULE, {leave, Username}).

send_message(From, Message) ->
    gen_server:cast(?MODULE, {send_message, From, Message}).
```

### Scala Chat Server
```scala
import akka.actor._
import scala.collection.immutable.Map

class ChatServer extends Actor {
  private var users: Map[String, ActorRef] = Map.empty

  def receive: Receive = {
    case Join(username, userRef) =>
      context.watch(userRef)
      users = users + (username -> userRef)
      notifyAll(UserJoined(username))
      sender() ! Joined

    case Leave(username) =>
      users.get(username).foreach(context.unwatch)
      users = users - username
      notifyAll(UserLeft(username))
      sender() ! Left

    case SendMessage(from, message) =>
      notifyAll(Message(from, message))

    case Terminated(userRef) =>
      users.find(_._2 == userRef).foreach { case (username, _) =>
        users = users - username
        notifyAll(UserLeft(username))
      }
  }

  private def notifyAll(msg: ChatEvent): Unit = {
    users.values.foreach(_ ! msg)
  }

  override def postStop(): Unit = {
    println("Chat server stopped")
  }
}

// Message protocol
sealed trait ChatCommand
case class Join(username: String, userRef: ActorRef) extends ChatCommand
case class Leave(username: String) extends ChatCommand
case class SendMessage(from: String, message: String) extends ChatCommand

sealed trait ChatResponse
case object Joined extends ChatResponse
case object Left extends ChatResponse

sealed trait ChatEvent
case class UserJoined(username: String) extends ChatEvent
case class UserLeft(username: String) extends ChatEvent
case class Message(from: String, text: String) extends ChatEvent

// User client actor
class ChatClient(username: String, server: ActorRef) extends Actor {
  override def preStart(): Unit = {
    server ! Join(username, self)
  }

  def receive: Receive = {
    case Joined =>
      println(s"$username joined the chat")

    case UserJoined(user) =>
      println(s"$user joined")

    case UserLeft(user) =>
      println(s"$user left")

    case Message(from, text) =>
      println(s"[$from]: $text")

    case SendMsg(text) =>
      server ! SendMessage(username, text)
  }

  override def postStop(): Unit = {
    server ! Leave(username)
  }
}

case class SendMsg(text: String)

// Usage example
object ChatExample extends App {
  val system = ActorSystem("ChatSystem")
  val server = system.actorOf(Props[ChatServer], "server")

  val alice = system.actorOf(Props(new ChatClient("Alice", server)), "alice")
  val bob = system.actorOf(Props(new ChatClient("Bob", server)), "bob")

  Thread.sleep(100)
  alice ! SendMsg("Hello everyone!")
  bob ! SendMsg("Hi Alice!")

  Thread.sleep(1000)
  system.terminate()
}
```

## Advanced Topics

### Hot Code Swapping
Erlang's hot code swapping has limited JVM equivalents:
- **JRebel**: Commercial tool for class reloading
- **sbt-revolver**: Development-time hot reloading
- **Akka Rolling Updates**: For production deployments
- **Containerized deployments**: Blue-green or canary deployments
- **Feature flags**: Toggle functionality without redeployment

### Process Migration
For Erlang's process migration:
- **Akka Cluster Sharding**: Automatic entity rebalancing
- **Akka Cluster Singleton**: Migrate singleton across nodes
- **Akka Persistence**: State recovery after migration
- **Custom serialization**: Efficient message serialization

### Binary Protocols
For complex binary protocols:
- **scodec**: Composable binary codecs
- **Akka ByteString**: Efficient binary operations
- **java.nio.ByteBuffer**: Low-level binary handling
- **Protocol Buffers**: Schema-based serialization

### Distributed Tracing
Monitor distributed systems:
- **Kamon**: Metrics and tracing for Akka
- **OpenTelemetry**: Distributed tracing standard
- **Zipkin**: Distributed tracing system
- **Jaeger**: Distributed tracing platform

## Troubleshooting

### Common Issues

**Issue**: Actor mailbox overflow
- **Solution**: Implement bounded mailboxes, backpressure, or use Akka Streams

**Issue**: Memory leaks in long-running actors
- **Solution**: Implement state cleanup, use Akka Timers for periodic cleanup

**Issue**: Shared mutable state
- **Solution**: Encapsulate all mutable state within actors, use immutable messages

**Issue**: JVM garbage collection pauses
- **Solution**: Tune GC settings, use G1GC or ZGC, reduce allocation rate

**Issue**: Supervision strategy not triggering
- **Solution**: Ensure exceptions are thrown (not caught), verify supervisor hierarchy

**Issue**: Cluster split-brain
- **Solution**: Configure Akka Split Brain Resolver, use lease-based strategies

**Issue**: Serialization errors in distributed setup
- **Solution**: Configure serialization bindings, use Protocol Buffers or Avro

**Issue**: Performance degradation under load
- **Solution**: Profile with JMC/VisualVM, tune dispatcher settings, use routing

## References

### Official Documentation
- [Scala Documentation](https://docs.scala-lang.org/)
- [Akka Documentation](https://doc.akka.io/docs/akka/current/)
- [Erlang Documentation](https://www.erlang.org/docs)

### Libraries
- [Akka](https://akka.io/) - Actor model for JVM
- [Akka HTTP](https://doc.akka.io/docs/akka-http/current/) - HTTP server/client
- [Cats](https://typelevel.org/cats/) - Functional programming abstractions
- [Cats Effect](https://typelevel.org/cats-effect/) - Functional effects
- [scodec](http://scodec.org/) - Binary serialization
- [Circe](https://circe.github.io/circe/) - JSON library

### Learning Resources
- "Programming in Scala" by Martin Odersky
- "Akka in Action" by Raymond Roestenburg
- "Functional Programming in Scala" by Paul Chiusano
- "Reactive Messaging Patterns with the Actor Model" by Vaughn Vernon
- Scala documentation: https://docs.scala-lang.org/
- Akka documentation: https://doc.akka.io/

### Tools
- **sbt**: Scala build tool
- **ScalaTest/Specs2**: Testing frameworks
- **ScalaCheck**: Property-based testing
- **Metals**: Scala language server
- **IntelliJ IDEA**: IDE with Scala support
