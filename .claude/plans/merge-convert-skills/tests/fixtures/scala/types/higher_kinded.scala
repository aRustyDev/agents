// Higher-Kinded Types in Scala
//
// Demonstrates F[_] type parameters and type constructors.

package examples.types

// Functor type class
trait Functor[F[_]] {
  def map[A, B](fa: F[A])(f: A => B): F[B]
}

object Functor {
  def apply[F[_]](implicit F: Functor[F]): Functor[F] = F

  implicit val listFunctor: Functor[List] = new Functor[List] {
    def map[A, B](fa: List[A])(f: A => B): List[B] = fa.map(f)
  }

  implicit val optionFunctor: Functor[Option] = new Functor[Option] {
    def map[A, B](fa: Option[A])(f: A => B): Option[B] = fa.map(f)
  }
}

// Applicative type class
trait Applicative[F[_]] extends Functor[F] {
  def pure[A](a: A): F[A]
  def ap[A, B](ff: F[A => B])(fa: F[A]): F[B]

  // Derived operations
  def map2[A, B, C](fa: F[A], fb: F[B])(f: (A, B) => C): F[C] =
    ap(map(fa)(a => (b: B) => f(a, b)))(fb)

  override def map[A, B](fa: F[A])(f: A => B): F[B] =
    ap(pure(f))(fa)
}

object Applicative {
  def apply[F[_]](implicit F: Applicative[F]): Applicative[F] = F

  implicit val optionApplicative: Applicative[Option] = new Applicative[Option] {
    def pure[A](a: A): Option[A] = Some(a)
    def ap[A, B](ff: Option[A => B])(fa: Option[A]): Option[B] =
      for {
        f <- ff
        a <- fa
      } yield f(a)
  }

  implicit val listApplicative: Applicative[List] = new Applicative[List] {
    def pure[A](a: A): List[A] = List(a)
    def ap[A, B](ff: List[A => B])(fa: List[A]): List[B] =
      for {
        f <- ff
        a <- fa
      } yield f(a)
  }
}

// Monad type class
trait Monad[F[_]] extends Applicative[F] {
  def flatMap[A, B](fa: F[A])(f: A => F[B]): F[B]

  override def ap[A, B](ff: F[A => B])(fa: F[A]): F[B] =
    flatMap(ff)(f => map(fa)(f))
}

object Monad {
  def apply[F[_]](implicit F: Monad[F]): Monad[F] = F

  implicit val optionMonad: Monad[Option] = new Monad[Option] {
    def pure[A](a: A): Option[A] = Some(a)
    def flatMap[A, B](fa: Option[A])(f: A => Option[B]): Option[B] = fa.flatMap(f)
  }

  implicit val listMonad: Monad[List] = new Monad[List] {
    def pure[A](a: A): List[A] = List(a)
    def flatMap[A, B](fa: List[A])(f: A => List[B]): List[B] = fa.flatMap(f)
  }
}

// Foldable type class
trait Foldable[F[_]] {
  def foldLeft[A, B](fa: F[A], b: B)(f: (B, A) => B): B
  def foldRight[A, B](fa: F[A], b: B)(f: (A, B) => B): B

  def toList[A](fa: F[A]): List[A] =
    foldRight(fa, List.empty[A])(_ :: _)
}

object Foldable {
  implicit val listFoldable: Foldable[List] = new Foldable[List] {
    def foldLeft[A, B](fa: List[A], b: B)(f: (B, A) => B): B = fa.foldLeft(b)(f)
    def foldRight[A, B](fa: List[A], b: B)(f: (A, B) => B): B = fa.foldRight(b)(f)
  }
}

// Traverse type class
trait Traverse[F[_]] extends Functor[F] with Foldable[F] {
  def traverse[G[_]: Applicative, A, B](fa: F[A])(f: A => G[B]): G[F[B]]

  def sequence[G[_]: Applicative, A](fga: F[G[A]]): G[F[A]] =
    traverse(fga)(identity)
}

// Natural transformation
trait ~>[F[_], G[_]] {
  def apply[A](fa: F[A]): G[A]
}

object NaturalTransformations {
  val optionToList: Option ~> List = new ~>[Option, List] {
    def apply[A](fa: Option[A]): List[A] = fa.toList
  }

  val listHeadOption: List ~> Option = new ~>[List, Option] {
    def apply[A](fa: List[A]): Option[A] = fa.headOption
  }
}

// Higher-kinded type with multiple parameters
trait Bifunctor[F[_, _]] {
  def bimap[A, B, C, D](fab: F[A, B])(f: A => C)(g: B => D): F[C, D]

  def leftMap[A, B, C](fab: F[A, B])(f: A => C): F[C, B] =
    bimap(fab)(f)(identity)

  def rightMap[A, B, D](fab: F[A, B])(g: B => D): F[A, D] =
    bimap(fab)(identity)(g)
}

object Bifunctor {
  implicit val eitherBifunctor: Bifunctor[Either] = new Bifunctor[Either] {
    def bimap[A, B, C, D](fab: Either[A, B])(f: A => C)(g: B => D): Either[C, D] =
      fab match {
        case Left(a) => Left(f(a))
        case Right(b) => Right(g(b))
      }
  }

  implicit val tupleBifunctor: Bifunctor[Tuple2] = new Bifunctor[Tuple2] {
    def bimap[A, B, C, D](fab: (A, B))(f: A => C)(g: B => D): (C, D) =
      (f(fab._1), g(fab._2))
  }
}
