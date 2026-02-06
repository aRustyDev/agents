/// Test fixture: Enums
/// Tests various enum definitions.

/// C-style enum
pub enum Status {
    Pending = 0,
    Running = 1,
    Complete = 2,
    Failed = 3,
}

/// Unit variants
pub enum Direction {
    North,
    South,
    East,
    West,
}

/// Tuple variants
pub enum Event {
    Click(i32, i32),
    KeyPress(char),
    Scroll(f32),
}

/// Struct variants
pub enum Shape {
    Circle { radius: f64 },
    Rectangle { width: f64, height: f64 },
    Triangle { a: f64, b: f64, c: f64 },
}

impl Shape {
    pub fn area(&self) -> f64 {
        match self {
            Shape::Circle { radius } => std::f64::consts::PI * radius * radius,
            Shape::Rectangle { width, height } => width * height,
            Shape::Triangle { a, b, c } => {
                let s = (a + b + c) / 2.0;
                (s * (s - a) * (s - b) * (s - c)).sqrt()
            }
        }
    }
}

/// Generic enum
pub enum Tree<T> {
    Leaf(T),
    Node {
        value: T,
        left: Box<Tree<T>>,
        right: Box<Tree<T>>,
    },
}

/// Result-like enum
pub enum MyResult<T, E> {
    Ok(T),
    Err(E),
}

/// Option-like enum
pub enum Maybe<T> {
    Just(T),
    Nothing,
}

impl<T> Maybe<T> {
    pub fn unwrap(self) -> T {
        match self {
            Maybe::Just(v) => v,
            Maybe::Nothing => panic!("called unwrap on Nothing"),
        }
    }

    pub fn map<U, F: FnOnce(T) -> U>(self, f: F) -> Maybe<U> {
        match self {
            Maybe::Just(v) => Maybe::Just(f(v)),
            Maybe::Nothing => Maybe::Nothing,
        }
    }
}

/// Enum with methods using match
pub enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
    ChangeColor(u8, u8, u8),
}

impl Message {
    pub fn process(&self) {
        match self {
            Message::Quit => println!("Quit"),
            Message::Move { x, y } => println!("Move to ({}, {})", x, y),
            Message::Write(s) => println!("Write: {}", s),
            Message::ChangeColor(r, g, b) => println!("Color: ({}, {}, {})", r, g, b),
        }
    }
}
