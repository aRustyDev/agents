// Partial Functions in Scala
//
// Demonstrates partial function composition and usage.

package examples.control

// PartialFunction basics
object PartialFunctionBasics {
  // Partial function literal
  val divide: PartialFunction[Int, Int] = {
    case n if n != 0 => 100 / n
  }

  // Check if defined
  val isDefined: Boolean = divide.isDefinedAt(5)  // true
  val notDefined: Boolean = divide.isDefinedAt(0) // false

  // Safe application with lift
  val safeResult: Option[Int] = divide.lift(5)  // Some(20)
  val noResult: Option[Int] = divide.lift(0)    // None

  // Apply or else
  val withDefault: Int = divide.applyOrElse(0, (_: Int) => 0)
}

// Composing partial functions
object PartialFunctionComposition {
  val positive: PartialFunction[Int, String] = {
    case n if n > 0 => s"positive: $n"
  }

  val zero: PartialFunction[Int, String] = {
    case 0 => "zero"
  }

  val negative: PartialFunction[Int, String] = {
    case n if n < 0 => s"negative: $n"
  }

  // orElse composition
  val classify: PartialFunction[Int, String] =
    positive orElse zero orElse negative

  // andThen composition
  val classifyAndLength: PartialFunction[Int, Int] =
    classify andThen (_.length)

  // compose (reversed order)
  val absClassify: PartialFunction[Int, String] =
    classify compose ((n: Int) => math.abs(n))
}

// Using with collections
object PartialFunctionWithCollections {
  val numbers = List(-2, -1, 0, 1, 2, 3)

  // collect - filter + map using partial function
  val positiveDoubled: List[Int] = numbers.collect {
    case n if n > 0 => n * 2
  }
  // Result: List(2, 4, 6)

  // collectFirst - find first match
  val firstPositive: Option[Int] = numbers.collectFirst {
    case n if n > 0 => n * 2
  }
  // Result: Some(2)

  // Partial function in flatMap
  val processed: List[String] = numbers.flatMap {
    case n if n > 0 => Some(s"positive: $n")
    case 0 => Some("zero")
    case _ => None
  }
}

// Error handling with partial functions
object PartialFunctionErrorHandling {
  // Try recovery with partial function
  import scala.util.{Try, Success, Failure}

  def riskyOperation(n: Int): Int = {
    if (n < 0) throw new IllegalArgumentException("negative")
    if (n == 0) throw new ArithmeticException("zero")
    100 / n
  }

  val result: Try[Int] = Try(riskyOperation(-1)).recover {
    case _: IllegalArgumentException => -1
    case _: ArithmeticException => 0
  }

  // Future recovery
  import scala.concurrent.{Future, ExecutionContext}
  import scala.concurrent.ExecutionContext.Implicits.global

  def asyncOp(n: Int): Future[Int] = Future(riskyOperation(n))

  val recoveredFuture: Future[Int] = asyncOp(-1).recover {
    case _: IllegalArgumentException => -1
    case _: ArithmeticException => 0
  }

  // recoverWith for chaining
  val chainedRecovery: Future[Int] = asyncOp(-1).recoverWith {
    case _: IllegalArgumentException => asyncOp(1)
  }
}

// Pattern matching and partial functions
object PatternMatchingPartial {
  // Any pattern match block is a partial function
  val handler: PartialFunction[Any, String] = {
    case i: Int => s"Integer: $i"
    case s: String => s"String: $s"
    case l: List[_] => s"List of ${l.length}"
  }

  // Combine with type safety
  sealed trait Event
  case class Click(x: Int, y: Int) extends Event
  case class KeyPress(key: Char) extends Event
  case class Scroll(amount: Int) extends Event

  val clickHandler: PartialFunction[Event, String] = {
    case Click(x, y) => s"Clicked at ($x, $y)"
  }

  val keyHandler: PartialFunction[Event, String] = {
    case KeyPress(k) => s"Pressed $k"
  }

  val eventHandler: PartialFunction[Event, String] =
    clickHandler orElse keyHandler
}

// Creating partial functions
object CreatingPartialFunctions {
  // From function + guard
  def fromFunction[A, B](f: A => B)(guard: A => Boolean): PartialFunction[A, B] =
    new PartialFunction[A, B] {
      def isDefinedAt(x: A): Boolean = guard(x)
      def apply(x: A): B = f(x)
    }

  val safeDivide: PartialFunction[Int, Int] =
    fromFunction[Int, Int](100 / _)(_ != 0)

  // From case blocks
  val caseBlock: PartialFunction[Option[Int], Int] = {
    case Some(n) => n
  }

  // Lifting total function to partial
  def liftToPartial[A, B](f: A => Option[B]): PartialFunction[A, B] =
    new PartialFunction[A, B] {
      def isDefinedAt(x: A): Boolean = f(x).isDefined
      def apply(x: A): B = f(x).get
    }

  val parseIntPartial: PartialFunction[String, Int] =
    liftToPartial[String, Int](s => s.toIntOption)
}

// Chaining and pipelines
object PartialFunctionPipelines {
  // Processing pipeline with partial functions
  type Processor = PartialFunction[String, String]

  val trim: Processor = { case s => s.trim }
  val uppercase: Processor = { case s if s.nonEmpty => s.toUpperCase }
  val addPrefix: Processor = { case s => s"[${s}]" }

  val pipeline: Processor = trim andThen uppercase andThen addPrefix

  // Conditional processing
  val conditionalProcess: Processor = {
    case s if s.startsWith("@") => s.drop(1).toUpperCase
    case s if s.startsWith("#") => s.drop(1).toLowerCase
    case s => s
  }

  // With fallback
  val safeProcess: String => String = pipeline.applyOrElse(_, identity[String])
}

// PartialFunction vs Function
object PartialVsTotal {
  // Total function - always returns a result
  val total: Int => String = n => s"number: $n"

  // Partial function - may not be defined for all inputs
  val partial: PartialFunction[Int, String] = {
    case n if n >= 0 => s"non-negative: $n"
  }

  // Convert partial to total with default
  val withDefault: Int => String = partial.applyOrElse(_, (n: Int) => s"negative: $n")

  // Convert partial to Option-returning function
  val asOption: Int => Option[String] = partial.lift
}
