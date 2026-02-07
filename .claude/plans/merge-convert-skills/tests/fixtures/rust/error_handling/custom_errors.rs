// Custom error types fixture

use std::error::Error;
use std::fmt;

#[derive(Debug)]
pub enum ParseError {
    InvalidInput(String),
    OutOfRange { value: i32, min: i32, max: i32 },
    EmptyInput,
}

impl fmt::Display for ParseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ParseError::InvalidInput(msg) => write!(f, "Invalid input: {}", msg),
            ParseError::OutOfRange { value, min, max } => {
                write!(f, "Value {} out of range [{}, {}]", value, min, max)
            }
            ParseError::EmptyInput => write!(f, "Input is empty"),
        }
    }
}

impl Error for ParseError {}

pub fn parse_positive(input: &str) -> Result<i32, ParseError> {
    if input.is_empty() {
        return Err(ParseError::EmptyInput);
    }

    let value: i32 = input
        .parse()
        .map_err(|_| ParseError::InvalidInput(input.to_string()))?;

    if value <= 0 {
        return Err(ParseError::OutOfRange {
            value,
            min: 1,
            max: i32::MAX,
        });
    }

    Ok(value)
}

#[derive(Debug)]
pub struct AppError {
    message: String,
    source: Option<Box<dyn Error + Send + Sync>>,
}

impl AppError {
    pub fn new(message: impl Into<String>) -> Self {
        AppError {
            message: message.into(),
            source: None,
        }
    }

    pub fn with_source(message: impl Into<String>, source: impl Error + Send + Sync + 'static) -> Self {
        AppError {
            message: message.into(),
            source: Some(Box::new(source)),
        }
    }
}

impl fmt::Display for AppError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.message)
    }
}

impl Error for AppError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        self.source.as_ref().map(|e| e.as_ref() as &(dyn Error + 'static))
    }
}

pub fn process_data(data: &str) -> Result<i32, AppError> {
    parse_positive(data).map_err(|e| AppError::with_source("Failed to process data", e))
}
