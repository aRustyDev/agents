// Standard Collections in Scala
//
// Demonstrates idiomatic use of Scala collections.

package examples.collections

// List operations
object ListOperations {
  val numbers: List[Int] = List(1, 2, 3, 4, 5)

  // Construction
  val constructed: List[Int] = 1 :: 2 :: 3 :: Nil
  val range: List[Int] = (1 to 10).toList
  val filled: List[Int] = List.fill(5)(0)
  val tabulated: List[Int] = List.tabulate(5)(n => n * n)

  // Transformation
  val doubled: List[Int] = numbers.map(_ * 2)
  val filtered: List[Int] = numbers.filter(_ % 2 == 0)
  val flatMapped: List[Int] = numbers.flatMap(n => List(n, n * 10))

  // Folding
  val sum: Int = numbers.foldLeft(0)(_ + _)
  val product: Long = numbers.foldLeft(1L)(_ * _)
  val concatenated: String = numbers.foldLeft("")(_ + _.toString)

  // Pattern matching on lists
  def describe(list: List[Int]): String = list match {
    case Nil => "empty"
    case x :: Nil => s"single: $x"
    case x :: y :: rest => s"starts with $x, $y"
  }

  // Grouping and partitioning
  val (evens, odds) = numbers.partition(_ % 2 == 0)
  val grouped: Map[Int, List[Int]] = numbers.groupBy(_ % 3)

  // Zipping
  val letters = List('a', 'b', 'c')
  val zipped: List[(Int, Char)] = numbers zip letters
  val zipWithIndex: List[(Int, Int)] = numbers.zipWithIndex
}

// Map operations
object MapOperations {
  val scores: Map[String, Int] = Map(
    "Alice" -> 95,
    "Bob" -> 87,
    "Carol" -> 92
  )

  // Access
  val aliceScore: Option[Int] = scores.get("Alice")
  val bobScore: Int = scores.getOrElse("Bob", 0)
  val daveScore: Int = scores.withDefaultValue(0)("Dave")

  // Transformation
  val curvedScores: Map[String, Int] = scores.map { case (name, score) =>
    name -> (score + 5).min(100)
  }

  val topScorers: Map[String, Int] = scores.filter { case (_, score) =>
    score >= 90
  }

  // Combination
  val moreScores = Map("Dave" -> 88, "Eve" -> 94)
  val allScores: Map[String, Int] = scores ++ moreScores

  // Key/value operations
  val names: Set[String] = scores.keySet
  val scoreValues: Iterable[Int] = scores.values
  val pairs: List[(String, Int)] = scores.toList

  // Grouping list to map
  case class Student(name: String, grade: Int)
  val students = List(
    Student("Alice", 10),
    Student("Bob", 10),
    Student("Carol", 11)
  )
  val byGrade: Map[Int, List[Student]] = students.groupBy(_.grade)
}

// Set operations
object SetOperations {
  val evens: Set[Int] = Set(2, 4, 6, 8, 10)
  val primes: Set[Int] = Set(2, 3, 5, 7, 11)

  // Set operations
  val union: Set[Int] = evens | primes  // or: evens union primes
  val intersection: Set[Int] = evens & primes  // or: evens intersect primes
  val difference: Set[Int] = evens &~ primes  // or: evens diff primes

  // Membership
  val contains6: Boolean = evens.contains(6)
  val isSubset: Boolean = Set(2, 4) subsetOf evens

  // Adding/removing
  val withElem: Set[Int] = evens + 12
  val withoutElem: Set[Int] = evens - 2
}

// Vector and performance
object VectorOperations {
  // Vector for efficient random access and updates
  val vec: Vector[Int] = Vector(1, 2, 3, 4, 5)

  val updated: Vector[Int] = vec.updated(2, 100)
  val appended: Vector[Int] = vec :+ 6
  val prepended: Vector[Int] = 0 +: vec

  // Pattern matching (like List)
  def describe(v: Vector[Int]): String = v match {
    case Vector() => "empty"
    case Vector(x) => s"single: $x"
    case x +: _ => s"starts with $x"
  }
}

// Lazy collections
object LazyCollections {
  // Stream/LazyList for infinite sequences
  val naturals: LazyList[Int] = LazyList.from(1)
  val first10: List[Int] = naturals.take(10).toList

  // Fibonacci sequence
  val fibs: LazyList[BigInt] = {
    def loop(a: BigInt, b: BigInt): LazyList[BigInt] =
      a #:: loop(b, a + b)
    loop(0, 1)
  }

  val fib10: List[BigInt] = fibs.take(10).toList

  // View for lazy transformations
  val largeList: List[Int] = (1 to 1000000).toList
  val processed: List[Int] = largeList.view
    .filter(_ % 2 == 0)
    .map(_ * 2)
    .take(10)
    .toList
}

// Collection builders
object CollectionBuilders {
  // Using builder pattern
  val listBuilder = List.newBuilder[Int]
  listBuilder += 1
  listBuilder += 2
  listBuilder ++= List(3, 4, 5)
  val result: List[Int] = listBuilder.result()

  // StringBuilder
  val sb = new StringBuilder
  sb.append("Hello")
  sb.append(" ")
  sb.append("World")
  val str: String = sb.result()

  // MapBuilder
  val mapBuilder = Map.newBuilder[String, Int]
  mapBuilder += ("a" -> 1)
  mapBuilder += ("b" -> 2)
  val map: Map[String, Int] = mapBuilder.result()
}

// Parallel collections
object ParallelCollections {
  val numbers = (1 to 10000).toList

  // Parallel operations
  val parallelSum: Int = numbers.par.map(_ * 2).sum
  val parallelFiltered: List[Int] = numbers.par.filter(_ % 2 == 0).toList

  // Note: Order may not be preserved
  val parallelProcessed: Vector[Int] = numbers.par
    .map(_ * 2)
    .filter(_ > 1000)
    .toVector
}

// Collection conversions
object CollectionConversions {
  val list: List[Int] = List(1, 2, 3, 2, 1)

  // Between types
  val set: Set[Int] = list.toSet
  val vector: Vector[Int] = list.toVector
  val array: Array[Int] = list.toArray

  // To Map
  val indexed: Map[Int, Int] = list.zipWithIndex.toMap
  val pairs: List[(String, Int)] = List("a" -> 1, "b" -> 2)
  val map: Map[String, Int] = pairs.toMap

  // From Java
  import scala.jdk.CollectionConverters._
  val javaList: java.util.List[Int] = list.asJava
  val scalaList: List[Int] = javaList.asScala.toList
}
