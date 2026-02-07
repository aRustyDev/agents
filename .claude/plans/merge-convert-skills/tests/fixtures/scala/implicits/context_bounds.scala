// Context Bounds in Scala
//
// Demonstrates context bounds and their relationship to implicits.

package examples.implicits

// Context bound is syntactic sugar for implicit parameter
// def sort[A: Ordering](list: List[A])
// is equivalent to
// def sort[A](list: List[A])(implicit ord: Ordering[A])

// Using context bounds
object ContextBoundExamples {
  // Single context bound
  def sort[A: Ordering](list: List[A]): List[A] =
    list.sorted

  // Multiple context bounds
  def showSorted[A: Ordering: Show](list: List[A]): String = {
    val sorted = list.sorted
    sorted.map(Show[A].show).mkString(", ")
  }

  // Context bound with usage
  def max[A: Ordering](x: A, y: A): A = {
    val ord = implicitly[Ordering[A]]
    if (ord.compare(x, y) >= 0) x else y
  }

  // Using summon (Scala 3) or implicitly (Scala 2)
  def min[A: Ordering](x: A, y: A): A = {
    val ord = Ordering[A] // Companion object apply
    if (ord.compare(x, y) <= 0) x else y
  }
}

// Custom type class with context bounds
trait Printable[A] {
  def print(a: A): String
}

object Printable {
  def apply[A](implicit p: Printable[A]): Printable[A] = p

  implicit val intPrintable: Printable[Int] = (a: Int) => a.toString
  implicit val stringPrintable: Printable[String] = (a: String) => a
  implicit val doublePrintable: Printable[Double] = (a: Double) => f"$a%.2f"
}

object PrintableExamples {
  // Context bound with Printable
  def format[A: Printable](a: A): String =
    s"Value: ${Printable[A].print(a)}"

  // Multiple bounds including custom type class
  def sortAndPrint[A: Ordering: Printable](list: List[A]): String =
    list.sorted.map(Printable[A].print).mkString(", ")
}

// Combining with view bounds (deprecated but still seen in old code)
// View bounds were: def foo[A <% B] = ...
// Now use implicit conversion: def foo[A](implicit ev: A => B) = ...

object ImplicitConversionExample {
  // Old style (deprecated)
  // def stringify[A <% String](a: A): String = a

  // New style
  def stringify[A](a: A)(implicit ev: A => String): String = ev(a)

  // Or using implicit class
  implicit class IntOps(val n: Int) extends AnyVal {
    def times(s: String): String = s * n
  }
}

// Combining context bounds with type bounds
object CombinedBounds {
  // Context bound with upper type bound
  def sortSubtypes[A <: AnyRef: Ordering](list: List[A]): List[A] =
    list.sorted

  // Context bound with variance
  trait Box[+A]

  def sortBoxes[A: Ordering](boxes: List[Box[A]]): List[Box[A]] = {
    implicit val boxOrd: Ordering[Box[A]] = new Ordering[Box[A]] {
      def compare(x: Box[A], y: Box[A]): Int = 0 // Simplified
    }
    boxes.sorted
  }
}

// Evidence pattern
object EvidencePattern {
  // Type equality evidence
  trait =:=[A, B]
  implicit def refl[A]: A =:= A = new =:=[A, A] {}

  // Subtype evidence
  trait <:<[A, B]
  implicit def subtype[A, B >: A]: A <:< B = new <:<[A, B] {}

  // Using evidence
  def castIfEqual[A, B](a: A)(implicit ev: A =:= B): B =
    a.asInstanceOf[B]

  // Safe covariant cast
  def widen[A, B](a: A)(implicit ev: A <:< B): B =
    ev.substituteCo(a)
}

// Recursive context bounds
object RecursiveBounds {
  // Comparable with self-type
  trait Ordered[A <: Ordered[A]] { self: A =>
    def compare(other: A): Int
    def <(other: A): Boolean = compare(other) < 0
    def >(other: A): Boolean = compare(other) > 0
    def <=(other: A): Boolean = compare(other) <= 0
    def >=(other: A): Boolean = compare(other) >= 0
  }

  case class Age(years: Int) extends Ordered[Age] {
    def compare(other: Age): Int = years - other.years
  }
}

// Type class coherence
object TypeClassCoherence {
  // Only one instance per type should exist
  // Orphan instances should be avoided

  // Good: Instance in companion object
  case class UserId(value: Long)
  object UserId {
    implicit val ordering: Ordering[UserId] =
      Ordering.by(_.value)
  }

  // Using the instance (found via implicit scope)
  val sorted: List[UserId] = List(UserId(3), UserId(1), UserId(2)).sorted
}
