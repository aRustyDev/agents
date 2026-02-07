// Pattern Matching in Scala
//
// Demonstrates exhaustive pattern matching and extractors.

package examples.control

// Basic pattern matching
object BasicPatterns {
  def describe(x: Any): String = x match {
    case 0 => "zero"
    case 1 => "one"
    case "hello" => "greeting"
    case true => "yes"
    case false => "no"
    case _ => "something else"
  }

  // Type patterns
  def typeMatch(x: Any): String = x match {
    case i: Int => s"Int: $i"
    case s: String => s"String: $s"
    case l: List[_] => s"List with ${l.length} elements"
    case _ => "Unknown type"
  }

  // Guard patterns
  def classify(n: Int): String = n match {
    case x if x < 0 => "negative"
    case 0 => "zero"
    case x if x <= 10 => "small positive"
    case x if x <= 100 => "medium positive"
    case _ => "large positive"
  }
}

// Case class patterns
object CaseClassPatterns {
  case class Person(name: String, age: Int)
  case class Address(street: String, city: String)
  case class Employee(person: Person, address: Address)

  def greet(person: Person): String = person match {
    case Person("Alice", _) => "Hello, Alice!"
    case Person(name, age) if age < 18 => s"Hi, young $name!"
    case Person(name, _) => s"Hello, $name"
  }

  // Nested patterns
  def getCity(employee: Employee): String = employee match {
    case Employee(_, Address(_, city)) => city
  }

  // Variable binding with @
  def checkPerson(person: Person): String = person match {
    case p @ Person(_, age) if age >= 18 => s"Adult: ${p.name}"
    case p => s"Minor: ${p.name}"
  }
}

// Sealed trait patterns (exhaustive matching)
object SealedPatterns {
  sealed trait Shape
  case class Circle(radius: Double) extends Shape
  case class Rectangle(width: Double, height: Double) extends Shape
  case class Triangle(a: Double, b: Double, c: Double) extends Shape

  def area(shape: Shape): Double = shape match {
    case Circle(r) => math.Pi * r * r
    case Rectangle(w, h) => w * h
    case Triangle(a, b, c) =>
      val s = (a + b + c) / 2
      math.sqrt(s * (s - a) * (s - b) * (s - c))
  }

  // Option matching
  def process(opt: Option[Int]): String = opt match {
    case Some(n) if n > 0 => s"Positive: $n"
    case Some(n) if n < 0 => s"Negative: $n"
    case Some(0) => "Zero"
    case None => "Nothing"
  }

  // Either matching
  def handleResult(result: Either[String, Int]): String = result match {
    case Right(n) => s"Success: $n"
    case Left(err) => s"Error: $err"
  }
}

// List patterns
object ListPatterns {
  def describeList(list: List[Int]): String = list match {
    case Nil => "empty"
    case x :: Nil => s"singleton: $x"
    case x :: y :: Nil => s"pair: $x and $y"
    case x :: y :: rest => s"starts with $x, $y and ${rest.length} more"
  }

  // Pattern with list operations
  def sum(list: List[Int]): Int = list match {
    case Nil => 0
    case head :: tail => head + sum(tail)
  }

  // With guards
  def findFirst(list: List[Int], pred: Int => Boolean): Option[Int] = list match {
    case Nil => None
    case head :: _ if pred(head) => Some(head)
    case _ :: tail => findFirst(tail, pred)
  }
}

// Tuple patterns
object TuplePatterns {
  def processPair(pair: (Int, Int)): String = pair match {
    case (0, 0) => "origin"
    case (x, 0) => s"on x-axis at $x"
    case (0, y) => s"on y-axis at $y"
    case (x, y) if x == y => s"on diagonal at $x"
    case (x, y) => s"at ($x, $y)"
  }

  def swap[A, B](pair: (A, B)): (B, A) = pair match {
    case (a, b) => (b, a)
  }

  // Triple patterns
  def classify(triple: (Int, Int, Int)): String = triple match {
    case (a, b, c) if a == b && b == c => "all equal"
    case (a, b, _) if a == b => "first two equal"
    case (_, b, c) if b == c => "last two equal"
    case _ => "all different"
  }
}

// Extractor patterns
object ExtractorPatterns {
  // Custom extractor
  object Even {
    def unapply(n: Int): Option[Int] =
      if (n % 2 == 0) Some(n / 2) else None
  }

  object Odd {
    def unapply(n: Int): Boolean = n % 2 == 1
  }

  def classify(n: Int): String = n match {
    case Even(half) => s"Even, half is $half"
    case Odd() => "Odd"
  }

  // Regex extractor
  val EmailPattern = """(\w+)@(\w+)\.(\w+)""".r

  def parseEmail(email: String): Option[(String, String, String)] = email match {
    case EmailPattern(user, domain, tld) => Some((user, domain, tld))
    case _ => None
  }

  // Sequence extractor
  object Split {
    def unapplySeq(s: String): Option[Seq[String]] =
      Some(s.split(",").toSeq)
  }

  def parseCsv(line: String): List[String] = line match {
    case Split(first, second, rest @ _*) =>
      List(first, second) ++ rest
    case Split(single) => List(single)
    case Split() => Nil
  }
}

// Partial functions from patterns
object PartialFunctionPatterns {
  // Partial function literal
  val positive: PartialFunction[Int, String] = {
    case n if n > 0 => s"Positive: $n"
  }

  val negative: PartialFunction[Int, String] = {
    case n if n < 0 => s"Negative: $n"
  }

  // Combining partial functions
  val classify: PartialFunction[Int, String] =
    positive orElse negative orElse { case 0 => "Zero" }

  // Using with collect
  val numbers = List(-2, -1, 0, 1, 2)
  val positives: List[String] = numbers.collect {
    case n if n > 0 => s"Positive: $n"
  }
}

// Match expressions as values
object MatchAsValue {
  def describe(n: Int): String = {
    val kind = n match {
      case 0 => "zero"
      case x if x > 0 => "positive"
      case _ => "negative"
    }
    s"$n is $kind"
  }

  // Inline match
  val result: String = (1, 2) match {
    case (a, b) => s"sum: ${a + b}"
  }
}
