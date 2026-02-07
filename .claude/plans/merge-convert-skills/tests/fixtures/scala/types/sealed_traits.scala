// Sealed Traits in Scala
//
// Demonstrates sum types via sealed trait hierarchies.

package examples.types

// Simple sealed trait (enum-like)
sealed trait Color
case object Red extends Color
case object Green extends Color
case object Blue extends Color

// Sealed trait with data
sealed trait Option[+A]
case class Some[+A](value: A) extends Option[A]
case object None extends Option[Nothing]

// Result type (like Rust's Result)
sealed trait Result[+E, +A]
case class Ok[+A](value: A) extends Result[Nothing, A]
case class Err[+E](error: E) extends Result[E, Nothing]

// Sealed trait with methods
sealed trait Tree[+A] {
  def map[B](f: A => B): Tree[B] = this match {
    case Empty => Empty
    case Node(value, left, right) => Node(f(value), left.map(f), right.map(f))
  }

  def size: Int = this match {
    case Empty => 0
    case Node(_, left, right) => 1 + left.size + right.size
  }
}
case object Empty extends Tree[Nothing]
case class Node[+A](value: A, left: Tree[A], right: Tree[A]) extends Tree[A]

// List implementation
sealed trait MyList[+A] {
  def head: A
  def tail: MyList[A]
  def isEmpty: Boolean

  def map[B](f: A => B): MyList[B] = this match {
    case MyNil => MyNil
    case MyCons(h, t) => MyCons(f(h), t.map(f))
  }

  def flatMap[B](f: A => MyList[B]): MyList[B] = this match {
    case MyNil => MyNil
    case MyCons(h, t) => f(h) ++ t.flatMap(f)
  }

  def ++[B >: A](other: MyList[B]): MyList[B] = this match {
    case MyNil => other
    case MyCons(h, t) => MyCons(h, t ++ other)
  }
}

case object MyNil extends MyList[Nothing] {
  def head: Nothing = throw new NoSuchElementException("head of empty list")
  def tail: MyList[Nothing] = throw new NoSuchElementException("tail of empty list")
  def isEmpty: Boolean = true
}

case class MyCons[+A](head: A, tail: MyList[A]) extends MyList[A] {
  def isEmpty: Boolean = false
}

// Either type
sealed trait Either[+E, +A] {
  def map[B](f: A => B): Either[E, B] = this match {
    case Left(e) => Left(e)
    case Right(a) => Right(f(a))
  }

  def flatMap[EE >: E, B](f: A => Either[EE, B]): Either[EE, B] = this match {
    case Left(e) => Left(e)
    case Right(a) => f(a)
  }
}
case class Left[+E](value: E) extends Either[E, Nothing]
case class Right[+A](value: A) extends Either[Nothing, A]

// Expression AST
sealed trait Expr
case class Num(value: Double) extends Expr
case class Var(name: String) extends Expr
case class Add(left: Expr, right: Expr) extends Expr
case class Mul(left: Expr, right: Expr) extends Expr
case class Let(name: String, value: Expr, body: Expr) extends Expr

object ExprEvaluator {
  def eval(expr: Expr, env: Map[String, Double]): Double = expr match {
    case Num(v) => v
    case Var(n) => env(n)
    case Add(l, r) => eval(l, env) + eval(r, env)
    case Mul(l, r) => eval(l, env) * eval(r, env)
    case Let(n, v, b) => eval(b, env + (n -> eval(v, env)))
  }
}

// Validated type
sealed trait Validated[+E, +A]
case class Valid[+A](value: A) extends Validated[Nothing, A]
case class Invalid[+E](errors: List[E]) extends Validated[E, Nothing]
