// Case Class Methods in Scala
//
// Demonstrates rich method patterns on case classes.

package examples.oop_fp

// Case class with custom methods
case class Point(x: Double, y: Double) {
  // Instance methods
  def distance(other: Point): Double = {
    val dx = x - other.x
    val dy = y - other.y
    math.sqrt(dx * dx + dy * dy)
  }

  def magnitude: Double = distance(Point.origin)

  def normalize: Point = {
    val mag = magnitude
    if (mag == 0) this else Point(x / mag, y / mag)
  }

  // Operator-like methods
  def +(other: Point): Point = Point(x + other.x, y + other.y)
  def -(other: Point): Point = Point(x - other.x, y - other.y)
  def *(scalar: Double): Point = Point(x * scalar, y * scalar)
  def unary_- : Point = Point(-x, -y)

  // Method returning new copy
  def moveBy(dx: Double, dy: Double): Point = copy(x = x + dx, y = y + dy)
  def scaleBy(factor: Double): Point = this * factor

  // Predicate methods
  def isOrigin: Boolean = x == 0 && y == 0
  def isOnAxis: Boolean = x == 0 || y == 0

  // String representation (overriding default)
  override def toString: String = f"Point($x%.2f, $y%.2f)"
}

object Point {
  // Companion object values
  val origin: Point = Point(0, 0)
  val unitX: Point = Point(1, 0)
  val unitY: Point = Point(0, 1)

  // Factory methods
  def polar(r: Double, theta: Double): Point =
    Point(r * math.cos(theta), r * math.sin(theta))

  def fromTuple(t: (Double, Double)): Point = Point(t._1, t._2)

  // Smart constructor with validation
  def validated(x: Double, y: Double): Either[String, Point] =
    if (x.isNaN || y.isNaN) Left("Coordinates cannot be NaN")
    else if (x.isInfinite || y.isInfinite) Left("Coordinates cannot be infinite")
    else Right(Point(x, y))
}

// Case class with type parameters
case class Box[A](value: A) {
  def map[B](f: A => B): Box[B] = Box(f(value))
  def flatMap[B](f: A => Box[B]): Box[B] = f(value)
  def fold[B](f: A => B): B = f(value)

  // Combining boxes
  def zip[B](other: Box[B]): Box[(A, B)] = Box((value, other.value))
  def zipWith[B, C](other: Box[B])(f: (A, B) => C): Box[C] =
    Box(f(value, other.value))
}

object Box {
  def pure[A](a: A): Box[A] = Box(a)

  // Applicative-style combining
  def map2[A, B, C](ba: Box[A], bb: Box[B])(f: (A, B) => C): Box[C] =
    ba.zipWith(bb)(f)
}

// Case class with validation
case class Email private (value: String) {
  def domain: String = value.split("@").last
  def localPart: String = value.split("@").head
}

object Email {
  def apply(value: String): Either[String, Email] = {
    val emailRegex = """^[\w.-]+@[\w.-]+\.\w+$""".r
    value match {
      case emailRegex() => Right(new Email(value.toLowerCase))
      case _ => Left(s"Invalid email format: $value")
    }
  }

  def unsafe(value: String): Email = new Email(value)
}

// Case class with computed properties
case class Person(firstName: String, lastName: String, birthYear: Int) {
  def fullName: String = s"$firstName $lastName"
  def age(currentYear: Int): Int = currentYear - birthYear

  def initials: String = s"${firstName.head}.${lastName.head}."

  // Update methods
  def withFirstName(name: String): Person = copy(firstName = name)
  def withLastName(name: String): Person = copy(lastName = name)

  // Builder-style methods
  def named(first: String, last: String): Person =
    copy(firstName = first, lastName = last)
}

object Person {
  def apply(fullName: String, birthYear: Int): Option[Person] = {
    fullName.split(" ").toList match {
      case first :: last :: Nil => Some(Person(first, last, birthYear))
      case _ => None
    }
  }
}

// Case class with rich equality
case class Money(amount: BigDecimal, currency: String) {
  require(currency.length == 3, "Currency must be 3-letter code")

  def +(other: Money): Money = {
    require(currency == other.currency, "Currencies must match")
    Money(amount + other.amount, currency)
  }

  def -(other: Money): Money = {
    require(currency == other.currency, "Currencies must match")
    Money(amount - other.amount, currency)
  }

  def *(multiplier: BigDecimal): Money = Money(amount * multiplier, currency)

  def isPositive: Boolean = amount > 0
  def isNegative: Boolean = amount < 0
  def isZero: Boolean = amount == 0

  def format: String = f"${currency} ${amount}%.2f"
}

object Money {
  def usd(amount: BigDecimal): Money = Money(amount, "USD")
  def eur(amount: BigDecimal): Money = Money(amount, "EUR")
  def gbp(amount: BigDecimal): Money = Money(amount, "GBP")

  val zero: Money = Money(0, "USD")
}

// Case class with lens-like updates
case class Address(street: String, city: String, country: String)

case class Company(name: String, address: Address) {
  // Nested update
  def updateCity(newCity: String): Company =
    copy(address = address.copy(city = newCity))

  def updateStreet(newStreet: String): Company =
    copy(address = address.copy(street = newStreet))
}

// Case class implementing traits
trait Comparable[A] {
  def compareTo(other: A): Int
}

case class Version(major: Int, minor: Int, patch: Int)
    extends Comparable[Version]
    with Ordered[Version] {

  def compareTo(other: Version): Int = compare(other)

  def compare(other: Version): Int = {
    val majorCmp = major.compare(other.major)
    if (majorCmp != 0) majorCmp
    else {
      val minorCmp = minor.compare(other.minor)
      if (minorCmp != 0) minorCmp
      else patch.compare(other.patch)
    }
  }

  def increment: Version = copy(patch = patch + 1)
  def incrementMinor: Version = copy(minor = minor + 1, patch = 0)
  def incrementMajor: Version = copy(major = major + 1, minor = 0, patch = 0)

  override def toString: String = s"$major.$minor.$patch"
}

object Version {
  val zero: Version = Version(0, 0, 0)
  val initial: Version = Version(1, 0, 0)

  def parse(s: String): Option[Version] = {
    s.split('.').toList match {
      case List(maj, min, pat) =>
        for {
          major <- maj.toIntOption
          minor <- min.toIntOption
          patch <- pat.toIntOption
        } yield Version(major, minor, patch)
      case _ => None
    }
  }
}
