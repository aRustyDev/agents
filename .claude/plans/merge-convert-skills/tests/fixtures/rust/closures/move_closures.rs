// Move closures fixture

pub fn capture_by_move(value: String) -> impl Fn() -> String {
    move || value.clone()
}

pub fn capture_and_consume(values: Vec<i32>) -> impl FnOnce() -> i32 {
    move || values.into_iter().sum()
}

pub fn spawn_task(data: String) -> std::thread::JoinHandle<String> {
    std::thread::spawn(move || {
        format!("Processed: {}", data)
    })
}

pub struct Handler {
    callback: Box<dyn Fn(i32) -> i32>,
}

impl Handler {
    pub fn new<F>(f: F) -> Self
    where
        F: Fn(i32) -> i32 + 'static,
    {
        Handler { callback: Box::new(f) }
    }

    pub fn handle(&self, value: i32) -> i32 {
        (self.callback)(value)
    }
}

pub fn create_handlers() -> Vec<Box<dyn Fn(i32) -> i32>> {
    let mut handlers: Vec<Box<dyn Fn(i32) -> i32>> = Vec::new();

    for i in 0..3 {
        handlers.push(Box::new(move |x| x + i));
    }

    handlers
}

pub fn async_callback<F>(callback: F)
where
    F: FnOnce(Result<i32, String>) + Send + 'static,
{
    std::thread::spawn(move || {
        callback(Ok(42));
    });
}
