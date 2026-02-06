/// Test fixture: Lifetimes
/// Tests explicit and elided lifetimes.

/// Explicit lifetime parameter
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}

/// Multiple lifetimes
fn pick_first<'a, 'b>(x: &'a str, _y: &'b str) -> &'a str {
    x
}

/// Lifetime elision - single input reference
fn first_word(s: &str) -> &str {
    s.split_whitespace().next().unwrap_or("")
}

/// Lifetime elision - &self method
struct Parser<'a> {
    input: &'a str,
    position: usize,
}

impl<'a> Parser<'a> {
    fn new(input: &'a str) -> Parser<'a> {
        Parser { input, position: 0 }
    }

    /// Elided: returns &'a str because of &self
    fn peek(&self) -> &str {
        &self.input[self.position..]
    }

    fn advance(&mut self, n: usize) {
        self.position += n;
    }
}

/// Static lifetime
fn static_ref() -> &'static str {
    "This lives forever"
}

/// Lifetime bound
fn announce<'a, T>(x: &'a T) -> &'a str
where
    T: std::fmt::Display + 'a,
{
    println!("{}", x);
    "announced"
}

/// Lifetime in return type
struct Wrapper<'a> {
    data: &'a [u8],
}

impl<'a> Wrapper<'a> {
    fn slice(&self, start: usize, end: usize) -> &'a [u8] {
        &self.data[start..end]
    }
}

/// Lifetime outlives
fn outlives<'a, 'b>(x: &'a str, y: &'b str) -> &'a str
where
    'b: 'a,  // 'b outlives 'a
{
    if x.len() > y.len() { x } else { y }
}

/// HRTB (Higher-Ranked Trait Bound)
fn apply_to_str<F>(f: F) -> String
where
    F: for<'a> Fn(&'a str) -> &'a str,
{
    let s = String::from("hello");
    f(&s).to_string()
}
