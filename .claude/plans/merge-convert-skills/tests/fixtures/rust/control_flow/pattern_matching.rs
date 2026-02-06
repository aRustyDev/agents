/// Test fixture: Pattern Matching
/// Tests match expressions and patterns.

/// Basic match
fn describe_number(n: i32) -> &'static str {
    match n {
        0 => "zero",
        1 => "one",
        2 => "two",
        _ => "many",
    }
}

/// Match with guards
fn categorize(n: i32) -> &'static str {
    match n {
        x if x < 0 => "negative",
        0 => "zero",
        x if x < 10 => "small",
        x if x < 100 => "medium",
        _ => "large",
    }
}

/// Destructuring tuples
fn process_pair(pair: (i32, i32)) -> i32 {
    match pair {
        (0, y) => y,
        (x, 0) => x,
        (x, y) if x == y => x * 2,
        (x, y) => x + y,
    }
}

/// Destructuring structs
struct Point {
    x: i32,
    y: i32,
}

fn describe_point(p: Point) -> String {
    match p {
        Point { x: 0, y: 0 } => "origin".to_string(),
        Point { x, y: 0 } => format!("on x-axis at {}", x),
        Point { x: 0, y } => format!("on y-axis at {}", y),
        Point { x, y } => format!("at ({}, {})", x, y),
    }
}

/// Destructuring enums
enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
    Color(u8, u8, u8),
}

fn handle_message(msg: Message) -> String {
    match msg {
        Message::Quit => "Quitting".to_string(),
        Message::Move { x, y } => format!("Moving to ({}, {})", x, y),
        Message::Write(text) => format!("Writing: {}", text),
        Message::Color(r, g, b) => format!("Color: #{:02x}{:02x}{:02x}", r, g, b),
    }
}

/// Binding with @
fn range_category(n: u32) -> String {
    match n {
        id @ 1..=5 => format!("Small: {}", id),
        id @ 6..=10 => format!("Medium: {}", id),
        id => format!("Large: {}", id),
    }
}

/// if let
fn process_optional(opt: Option<i32>) {
    if let Some(value) = opt {
        println!("Got value: {}", value);
    }
}

/// while let
fn drain_iterator(mut iter: impl Iterator<Item = i32>) {
    while let Some(value) = iter.next() {
        println!("Value: {}", value);
    }
}

/// let else (Rust 1.65+)
fn parse_or_return(s: &str) -> i32 {
    let Ok(n) = s.parse::<i32>() else {
        return 0;
    };
    n
}

/// Nested patterns
fn nested_match(data: Option<Result<i32, &str>>) -> i32 {
    match data {
        Some(Ok(n)) => n,
        Some(Err(_)) => -1,
        None => 0,
    }
}

/// Or patterns
fn is_vowel(c: char) -> bool {
    matches!(c, 'a' | 'e' | 'i' | 'o' | 'u' | 'A' | 'E' | 'I' | 'O' | 'U')
}

/// Slice patterns
fn describe_slice(slice: &[i32]) -> String {
    match slice {
        [] => "empty".to_string(),
        [x] => format!("one element: {}", x),
        [x, y] => format!("pair: ({}, {})", x, y),
        [first, .., last] => format!("from {} to {}", first, last),
    }
}
