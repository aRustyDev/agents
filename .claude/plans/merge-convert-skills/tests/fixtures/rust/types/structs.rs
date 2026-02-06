/// Test fixture: Structs
/// Tests various struct definitions.

/// Simple struct
pub struct Point {
    pub x: f64,
    pub y: f64,
}

/// Tuple struct
pub struct Color(pub u8, pub u8, pub u8);

/// Unit struct
pub struct Marker;

/// Generic struct
pub struct Container<T> {
    value: T,
    count: usize,
}

impl<T> Container<T> {
    pub fn new(value: T) -> Self {
        Container { value, count: 0 }
    }

    pub fn get(&self) -> &T {
        &self.value
    }

    pub fn increment(&mut self) {
        self.count += 1;
    }
}

/// Struct with bounds
pub struct Ordered<T: Ord> {
    items: Vec<T>,
}

impl<T: Ord> Ordered<T> {
    pub fn new() -> Self {
        Ordered { items: Vec::new() }
    }

    pub fn insert(&mut self, item: T) {
        let pos = self.items.binary_search(&item).unwrap_or_else(|e| e);
        self.items.insert(pos, item);
    }
}

/// Struct with lifetimes
pub struct Slice<'a, T> {
    data: &'a [T],
    start: usize,
    end: usize,
}

impl<'a, T> Slice<'a, T> {
    pub fn new(data: &'a [T]) -> Self {
        Slice {
            data,
            start: 0,
            end: data.len(),
        }
    }
}

/// Struct with where clause
pub struct Cache<K, V>
where
    K: std::hash::Hash + Eq,
{
    data: std::collections::HashMap<K, V>,
}

/// Private fields with public constructor
pub struct Config {
    timeout: u64,
    retries: u32,
    name: String,
}

impl Config {
    pub fn new(name: &str) -> Self {
        Config {
            timeout: 30,
            retries: 3,
            name: name.to_string(),
        }
    }

    pub fn with_timeout(mut self, timeout: u64) -> Self {
        self.timeout = timeout;
        self
    }
}
