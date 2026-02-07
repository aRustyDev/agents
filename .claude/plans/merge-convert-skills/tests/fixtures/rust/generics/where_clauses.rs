// Where clause fixture

use std::fmt::Debug;

pub fn process<T, U>(a: T, b: U)
where
    T: Debug + Clone,
    U: Default,
{
    println!("{:?}", a.clone());
    let _default: U = U::default();
}

pub struct Handler<T, E>
where
    E: std::error::Error,
{
    value: T,
    _error: std::marker::PhantomData<E>,
}

impl<T, E> Handler<T, E>
where
    T: Clone,
    E: std::error::Error + Default,
{
    pub fn new(value: T) -> Self {
        Handler {
            value,
            _error: std::marker::PhantomData,
        }
    }

    pub fn get_clone(&self) -> T {
        self.value.clone()
    }
}

pub trait Transformer<T>
where
    T: Clone,
{
    fn transform(&self, value: T) -> T;
}

pub fn apply_transform<T, U>(value: T, transformer: &U) -> T
where
    T: Clone + Default,
    U: Transformer<T>,
{
    transformer.transform(value)
}
