/// Test fixture: Traits
/// Tests trait definitions and implementations.

/// Basic trait
pub trait Drawable {
    fn draw(&self);
}

/// Trait with default implementation
pub trait Greet {
    fn name(&self) -> &str;

    fn greet(&self) {
        println!("Hello, {}!", self.name());
    }
}

/// Trait with associated type
pub trait Iterator {
    type Item;

    fn next(&mut self) -> Option<Self::Item>;
}

/// Trait with associated constant
pub trait Sized {
    const SIZE: usize;

    fn size(&self) -> usize {
        Self::SIZE
    }
}

/// Generic trait
pub trait Convert<T> {
    fn convert(&self) -> T;
}

/// Trait with generic method
pub trait Container {
    fn get<T: Clone>(&self, key: &str) -> Option<T>;
    fn set<T>(&mut self, key: &str, value: T);
}

/// Trait bounds on trait
pub trait Sortable: Ord + Clone {
    fn sort_self(&mut self);
}

/// Unsafe trait
pub unsafe trait Send {
    // Marker trait
}

/// Trait object safe
pub trait Animal {
    fn speak(&self) -> String;
    fn legs(&self) -> u8;
}

// Implementations

struct Dog {
    name: String,
}

impl Animal for Dog {
    fn speak(&self) -> String {
        format!("{} says woof!", self.name)
    }

    fn legs(&self) -> u8 {
        4
    }
}

impl Greet for Dog {
    fn name(&self) -> &str {
        &self.name
    }
}

/// Generic impl
struct Wrapper<T>(T);

impl<T: Clone> Convert<T> for Wrapper<T> {
    fn convert(&self) -> T {
        self.0.clone()
    }
}

/// Blanket implementation
impl<T: std::fmt::Display> Drawable for T {
    fn draw(&self) {
        println!("{}", self);
    }
}

/// Trait with where clause
pub trait ComplexBounds<T, U>
where
    T: Clone + std::fmt::Debug,
    U: Default,
{
    fn combine(&self, t: T) -> U;
}

/// Supertraits
pub trait ReadWrite: std::io::Read + std::io::Write {
    fn flush_and_read(&mut self, buf: &mut [u8]) -> std::io::Result<usize>;
}
