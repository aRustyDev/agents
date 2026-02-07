// Type Classes in Scala
//
// Demonstrates the type class pattern with implicits.

package examples.implicits

// Type class definition
trait Show[A] {
  def show(a: A): String
}

object Show {
  def apply[A](implicit sh: Show[A]): Show[A] = sh

  // Summoner
  def show[A: Show](a: A): String = Show[A].show(a)

  // Instance constructors
  def instance[A](f: A => String): Show[A] = (a: A) => f(a)

  // Primitive instances
  implicit val intShow: Show[Int] = instance(_.toString)
  implicit val stringShow: Show[String] = instance(identity)
  implicit val booleanShow: Show[Boolean] = instance(if (_) "true" else "false")
  implicit val doubleShow: Show[Double] = instance(_.toString)

  // Derived instances
  implicit def optionShow[A](implicit sa: Show[A]): Show[Option[A]] =
    instance {
      case Some(a) => s"Some(${sa.show(a)})"
      case None => "None"
    }

  implicit def listShow[A](implicit sa: Show[A]): Show[List[A]] =
    instance { list =>
      list.map(sa.show).mkString("List(", ", ", ")")
    }

  implicit def tupleShow[A, B](implicit sa: Show[A], sb: Show[B]): Show[(A, B)] =
    instance { case (a, b) => s"(${sa.show(a)}, ${sb.show(b)})" }
}

// Eq type class
trait Eq[A] {
  def eqv(x: A, y: A): Boolean
  def neqv(x: A, y: A): Boolean = !eqv(x, y)
}

object Eq {
  def apply[A](implicit eq: Eq[A]): Eq[A] = eq

  def instance[A](f: (A, A) => Boolean): Eq[A] = (x: A, y: A) => f(x, y)

  implicit val intEq: Eq[Int] = instance(_ == _)
  implicit val stringEq: Eq[String] = instance(_ == _)

  implicit def optionEq[A](implicit ea: Eq[A]): Eq[Option[A]] =
    instance {
      case (Some(a), Some(b)) => ea.eqv(a, b)
      case (None, None) => true
      case _ => false
    }
}

// Ord type class
trait Ord[A] extends Eq[A] {
  def compare(x: A, y: A): Int

  def eqv(x: A, y: A): Boolean = compare(x, y) == 0
  def lt(x: A, y: A): Boolean = compare(x, y) < 0
  def lte(x: A, y: A): Boolean = compare(x, y) <= 0
  def gt(x: A, y: A): Boolean = compare(x, y) > 0
  def gte(x: A, y: A): Boolean = compare(x, y) >= 0
  def max(x: A, y: A): A = if (gte(x, y)) x else y
  def min(x: A, y: A): A = if (lte(x, y)) x else y
}

object Ord {
  def apply[A](implicit ord: Ord[A]): Ord[A] = ord

  def instance[A](f: (A, A) => Int): Ord[A] = (x: A, y: A) => f(x, y)

  implicit val intOrd: Ord[Int] = instance(_ - _)
  implicit val stringOrd: Ord[String] = instance(_.compareTo(_))
  implicit val doubleOrd: Ord[Double] = instance((x, y) => x.compareTo(y))
}

// Monoid type class
trait Monoid[A] {
  def empty: A
  def combine(x: A, y: A): A
}

object Monoid {
  def apply[A](implicit m: Monoid[A]): Monoid[A] = m

  def instance[A](z: A)(f: (A, A) => A): Monoid[A] = new Monoid[A] {
    def empty: A = z
    def combine(x: A, y: A): A = f(x, y)
  }

  implicit val intAddMonoid: Monoid[Int] = instance(0)(_ + _)
  implicit val stringMonoid: Monoid[String] = instance("")(_ + _)
  implicit def listMonoid[A]: Monoid[List[A]] = instance(List.empty[A])(_ ++ _)

  // Product monoid
  implicit def tupleMonoid[A, B](implicit ma: Monoid[A], mb: Monoid[B]): Monoid[(A, B)] =
    instance((ma.empty, mb.empty)) { case ((a1, b1), (a2, b2)) =>
      (ma.combine(a1, a2), mb.combine(b1, b2))
    }
}

// Syntax extensions via implicit class
object syntax {
  implicit class ShowOps[A](val a: A) extends AnyVal {
    def show(implicit sh: Show[A]): String = sh.show(a)
  }

  implicit class EqOps[A](val x: A) extends AnyVal {
    def ===(y: A)(implicit eq: Eq[A]): Boolean = eq.eqv(x, y)
    def =!=(y: A)(implicit eq: Eq[A]): Boolean = eq.neqv(x, y)
  }

  implicit class OrdOps[A](val x: A) extends AnyVal {
    def <(y: A)(implicit ord: Ord[A]): Boolean = ord.lt(x, y)
    def <=(y: A)(implicit ord: Ord[A]): Boolean = ord.lte(x, y)
    def >(y: A)(implicit ord: Ord[A]): Boolean = ord.gt(x, y)
    def >=(y: A)(implicit ord: Ord[A]): Boolean = ord.gte(x, y)
  }

  implicit class MonoidOps[A](val x: A) extends AnyVal {
    def |+|(y: A)(implicit m: Monoid[A]): A = m.combine(x, y)
  }
}

// Usage examples
object TypeClassExamples {
  import syntax._

  def combine[A: Monoid](items: List[A]): A =
    items.foldLeft(Monoid[A].empty)(Monoid[A].combine)

  def sortWith[A: Ord](list: List[A]): List[A] =
    list.sortWith(Ord[A].lt)

  def prettyPrint[A: Show](a: A): Unit =
    println(a.show)
}
