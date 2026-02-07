// Type bounds fixture

use std::fmt::{Debug, Display};

pub fn print_debug<T: Debug>(value: T) {
    println!("{:?}", value);
}

pub fn print_display<T: Display>(value: T) {
    println!("{}", value);
}

pub fn print_both<T: Debug + Display>(value: T) {
    println!("{:?}", value);
    println!("{}", value);
}

pub struct Wrapper<T: Clone> {
    inner: T,
}

impl<T: Clone> Wrapper<T> {
    pub fn new(inner: T) -> Self {
        Wrapper { inner }
    }

    pub fn clone_inner(&self) -> T {
        self.inner.clone()
    }
}

pub trait Printable {
    fn to_string(&self) -> String;
}

pub fn print_value<T: Printable>(value: &T) {
    println!("{}", value.to_string());
}

pub struct Comparable<T: Ord> {
    value: T,
}

impl<T: Ord> Comparable<T> {
    pub fn max<'a>(&'a self, other: &'a Self) -> &'a T {
        if self.value >= other.value {
            &self.value
        } else {
            &other.value
        }
    }
}
