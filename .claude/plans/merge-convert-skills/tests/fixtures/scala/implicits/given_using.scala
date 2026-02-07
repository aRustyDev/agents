// Given/Using in Scala 3
//
// Demonstrates Scala 3's given instances and using clauses.

package examples.implicits

// Type class with Scala 3 syntax
trait Printable[A]:
  extension (a: A) def print: String

object Printable:
  // Named given instance
  given Printable[Int] with
    extension (a: Int) def print: String = a.toString

  // Anonymous given instance
  given Printable[String] with
    extension (a: String) def print: String = s"'$a'"

  // Given with type parameter
  given [A](using pa: Printable[A]): Printable[List[A]] with
    extension (list: List[A]) def print: String =
      list.map(_.print).mkString("[", ", ", "]")

  // Given alias (when instance already exists)
  given Printable[Boolean] = new Printable[Boolean]:
    extension (a: Boolean) def print: String = if a then "yes" else "no"

// Using clauses
object PrintableOps:
  // Using clause in parameters
  def printAll[A](items: List[A])(using Printable[A]): String =
    items.map(_.print).mkString(", ")

  // Multiple using clauses
  def combine[A](x: A, y: A)(using pa: Printable[A], ord: Ordering[A]): String =
    val min = if ord.compare(x, y) <= 0 then x else y
    val max = if ord.compare(x, y) > 0 then x else y
    s"${min.print} to ${max.print}"

  // Context bound (shorthand for using)
  def show[A: Printable](a: A): String = a.print

// Given imports
object GivenImports:
  // Import specific given
  import Printable.given Printable[Int]

  // Import all givens of a type
  // import Printable.{given Printable[?]}

  // Import all givens
  // import Printable.given

// Ordering with given (Scala 3)
object OrderingExamples:
  case class Person(name: String, age: Int)

  // Given instance for Person ordering
  given Ordering[Person] with
    def compare(x: Person, y: Person): Int = x.age.compare(y.age)

  // Using the ordering
  def sort(people: List[Person])(using ord: Ordering[Person]): List[Person] =
    people.sorted

  // Derived ordering
  given personByName: Ordering[Person] = Ordering.by(_.name)

// ExecutionContext with given
object ExecutionContextExample:
  import scala.concurrent.{ExecutionContext, Future}

  given ec: ExecutionContext = ExecutionContext.global

  def asyncOp(value: Int)(using ExecutionContext): Future[Int] =
    Future(value * 2)

// Summoner pattern with Scala 3
trait Codec[A]:
  def encode(a: A): String
  def decode(s: String): Option[A]

object Codec:
  def apply[A](using c: Codec[A]): Codec[A] = c

  given Codec[Int] with
    def encode(a: Int): String = a.toString
    def decode(s: String): Option[Int] = s.toIntOption

  given Codec[String] with
    def encode(a: String): String = s"\"$a\""
    def decode(s: String): Option[String] =
      if s.startsWith("\"") && s.endsWith("\"")
      then Some(s.drop(1).dropRight(1))
      else None

  // Derived codec for Option
  given [A](using ca: Codec[A]): Codec[Option[A]] with
    def encode(a: Option[A]): String = a match
      case Some(v) => s"Some(${ca.encode(v)})"
      case None => "None"

    def decode(s: String): Option[Option[A]] =
      if s == "None" then Some(None)
      else if s.startsWith("Some(") && s.endsWith(")")
      then ca.decode(s.drop(5).dropRight(1)).map(Some(_))
      else None

// Type class derivation (Scala 3)
trait JsonEncoder[A]:
  extension (a: A) def toJson: String

object JsonEncoder:
  given JsonEncoder[Int] with
    extension (a: Int) def toJson: String = a.toString

  given JsonEncoder[String] with
    extension (a: String) def toJson: String = s"\"$a\""

  given JsonEncoder[Boolean] with
    extension (a: Boolean) def toJson: String = a.toString

  // Product derivation (simplified)
  given [A, B](using ea: JsonEncoder[A], eb: JsonEncoder[B]): JsonEncoder[(A, B)] with
    extension (pair: (A, B)) def toJson: String =
      s"[${pair._1.toJson}, ${pair._2.toJson}]"

  given [A](using ea: JsonEncoder[A]): JsonEncoder[List[A]] with
    extension (list: List[A]) def toJson: String =
      list.map(_.toJson).mkString("[", ",", "]")
