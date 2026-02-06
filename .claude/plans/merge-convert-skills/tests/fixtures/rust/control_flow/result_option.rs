/// Test fixture: Result and Option handling
/// Tests error handling patterns.

use std::fs::File;
use std::io::{self, Read};

/// Function returning Result
fn read_file(path: &str) -> Result<String, io::Error> {
    let mut file = File::open(path)?;
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    Ok(contents)
}

/// Function returning Option
fn find_item<T: PartialEq>(items: &[T], target: &T) -> Option<usize> {
    items.iter().position(|x| x == target)
}

/// Chaining with map and and_then
fn parse_and_double(s: &str) -> Option<i32> {
    s.parse::<i32>()
        .ok()
        .map(|n| n * 2)
}

/// Using ? operator
fn process_data(data: Option<&str>) -> Option<i32> {
    let text = data?;
    let num: i32 = text.parse().ok()?;
    Some(num * 2)
}

/// Converting between Result and Option
fn safe_divide(a: i32, b: i32) -> Option<i32> {
    if b == 0 {
        None
    } else {
        Some(a / b)
    }
}

fn divide_or_error(a: i32, b: i32) -> Result<i32, &'static str> {
    safe_divide(a, b).ok_or("division by zero")
}

/// Pattern matching on Result
fn handle_result<T, E: std::fmt::Display>(result: Result<T, E>) -> T
where
    T: Default,
{
    match result {
        Ok(value) => value,
        Err(e) => {
            eprintln!("Error: {}", e);
            T::default()
        }
    }
}

/// Pattern matching on Option
fn describe_option<T: std::fmt::Debug>(opt: Option<T>) -> String {
    match opt {
        Some(v) => format!("Has value: {:?}", v),
        None => "Empty".to_string(),
    }
}

/// unwrap_or and unwrap_or_else
fn with_defaults(opt: Option<String>) -> String {
    opt.unwrap_or_else(|| "default".to_string())
}

/// Multiple Results with try blocks (nightly)
fn complex_operation() -> Result<i32, Box<dyn std::error::Error>> {
    let a: i32 = "42".parse()?;
    let b: i32 = "10".parse()?;
    let result = a.checked_add(b).ok_or("overflow")?;
    Ok(result)
}

/// Result combinators
fn chain_operations(input: &str) -> Result<String, String> {
    input
        .parse::<i32>()
        .map_err(|e| e.to_string())
        .and_then(|n| {
            if n > 0 {
                Ok(n)
            } else {
                Err("must be positive".to_string())
            }
        })
        .map(|n| n.to_string())
}
