// For Comprehensions in Scala
//
// Demonstrates monadic composition via for-yield syntax.

package examples.control

// Basic for comprehensions with collections
object CollectionComprehensions {
  // Simple iteration
  val doubled: List[Int] = for {
    x <- List(1, 2, 3)
  } yield x * 2

  // Nested iteration (cartesian product)
  val pairs: List[(Int, String)] = for {
    x <- List(1, 2, 3)
    y <- List("a", "b")
  } yield (x, y)

  // With guards (filtering)
  val evens: List[Int] = for {
    x <- 1 to 10
    if x % 2 == 0
  } yield x

  // Multiple generators with guards
  val pythagorean: Seq[(Int, Int, Int)] = for {
    c <- 1 to 20
    b <- 1 until c
    a <- 1 until b
    if a * a + b * b == c * c
  } yield (a, b, c)

  // With pattern matching
  case class Person(name: String, age: Int)
  val people = List(Person("Alice", 25), Person("Bob", 30))

  val names: List[String] = for {
    Person(name, _) <- people
  } yield name

  // With value definitions
  val computed: List[Int] = for {
    x <- List(1, 2, 3)
    squared = x * x
    cubed = squared * x
  } yield cubed
}

// For comprehensions with Option
object OptionComprehensions {
  def divide(a: Int, b: Int): Option[Int] =
    if (b == 0) None else Some(a / b)

  def safeSqrt(x: Double): Option[Double] =
    if (x < 0) None else Some(math.sqrt(x))

  // Chaining Option operations
  val result: Option[Double] = for {
    a <- Some(100)
    b <- divide(a, 4)
    c <- safeSqrt(b.toDouble)
  } yield c

  // Early termination on None
  val failed: Option[Int] = for {
    a <- Some(10)
    b <- None: Option[Int]  // Stops here
    c <- Some(20)           // Never executed
  } yield a + b + c

  // With guards
  def findUser(id: Int): Option[String] = Some(s"User$id")
  def isAdmin(user: String): Boolean = user.endsWith("1")

  val adminUser: Option[String] = for {
    user <- findUser(1)
    if isAdmin(user)
  } yield user
}

// For comprehensions with Either
object EitherComprehensions {
  type Error = String
  type Result[A] = Either[Error, A]

  def parseNumber(s: String): Result[Int] =
    s.toIntOption.toRight(s"Invalid number: $s")

  def divide(a: Int, b: Int): Result[Int] =
    if (b == 0) Left("Division by zero")
    else Right(a / b)

  // Chaining Either operations
  val calculation: Result[Int] = for {
    a <- parseNumber("100")
    b <- parseNumber("4")
    c <- divide(a, b)
  } yield c

  // Early exit on Left
  val failing: Result[Int] = for {
    a <- parseNumber("100")
    b <- parseNumber("zero")  // Fails here
    c <- divide(a, b)
  } yield c
}

// For comprehensions with Try
object TryComprehensions {
  import scala.util.{Try, Success, Failure}

  def parseJson(s: String): Try[Map[String, Any]] =
    Try(scala.util.parsing.json.JSON.parseFull(s).get.asInstanceOf[Map[String, Any]])

  def extractField(m: Map[String, Any], key: String): Try[Any] =
    Try(m(key))

  // Chaining Try operations
  def processJson(json: String, field: String): Try[String] = for {
    parsed <- parseJson(json)
    value <- extractField(parsed, field)
  } yield value.toString
}

// For comprehensions with Future
object FutureComprehensions {
  import scala.concurrent.{Future, ExecutionContext}
  import scala.concurrent.ExecutionContext.Implicits.global

  def fetchUser(id: Int): Future[String] =
    Future(s"User$id")

  def fetchOrders(user: String): Future[List[String]] =
    Future(List(s"Order1-$user", s"Order2-$user"))

  def calculateTotal(orders: List[String]): Future[Double] =
    Future(orders.length * 10.0)

  // Chaining Future operations
  def processUser(id: Int): Future[Double] = for {
    user <- fetchUser(id)
    orders <- fetchOrders(user)
    total <- calculateTotal(orders)
  } yield total

  // Parallel composition (not sequential)
  def parallel(id1: Int, id2: Int): Future[(String, String)] = {
    val f1 = fetchUser(id1)
    val f2 = fetchUser(id2)
    for {
      u1 <- f1
      u2 <- f2
    } yield (u1, u2)
  }
}

// Custom monad in for comprehension
object CustomMonad {
  // Simple IO monad
  case class IO[A](unsafeRun: () => A) {
    def map[B](f: A => B): IO[B] = IO(() => f(unsafeRun()))
    def flatMap[B](f: A => IO[B]): IO[B] = IO(() => f(unsafeRun()).unsafeRun())
  }

  object IO {
    def pure[A](a: A): IO[A] = IO(() => a)
    def putStrLn(s: String): IO[Unit] = IO(() => println(s))
    def getLine: IO[String] = IO(() => scala.io.StdIn.readLine())
  }

  // Using for comprehension with custom IO
  val program: IO[Unit] = for {
    _ <- IO.putStrLn("What is your name?")
    name <- IO.getLine
    _ <- IO.putStrLn(s"Hello, $name!")
  } yield ()
}

// Translation of for comprehensions
object ForTranslation {
  // for { x <- expr1 } yield x * 2
  // translates to:
  // expr1.map(x => x * 2)

  // for { x <- expr1; y <- expr2 } yield (x, y)
  // translates to:
  // expr1.flatMap(x => expr2.map(y => (x, y)))

  // for { x <- expr1 if cond } yield x
  // translates to:
  // expr1.withFilter(x => cond).map(x => x)

  // Explicit translation example
  val forStyle: List[(Int, Int)] = for {
    x <- List(1, 2, 3)
    if x % 2 == 1
    y <- List(x, x * 10)
  } yield (x, y)

  val explicitStyle: List[(Int, Int)] =
    List(1, 2, 3)
      .withFilter(x => x % 2 == 1)
      .flatMap(x => List(x, x * 10).map(y => (x, y)))
}
