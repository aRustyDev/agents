/// Test fixture: Move semantics
/// Tests ownership transfer and move operations.

/// Takes ownership of a Vec and returns a new Vec
fn process_owned(data: Vec<i32>) -> Vec<i32> {
    data.into_iter().map(|x| x * 2).collect()
}

/// Takes ownership and consumes the value
fn consume(s: String) {
    println!("{}", s);
}

/// Demonstrates move semantics with structs
struct UniqueResource {
    id: u64,
    name: String,
}

impl UniqueResource {
    fn new(id: u64, name: String) -> Self {
        UniqueResource { id, name }
    }

    /// Takes ownership of self
    fn into_name(self) -> String {
        self.name
    }
}

/// Move in function call
fn example_move() {
    let resource = UniqueResource::new(1, "test".to_string());
    let name = resource.into_name();
    // resource is now invalid
    println!("{}", name);
}

/// Move in match patterns
fn match_move(opt: Option<String>) -> String {
    match opt {
        Some(s) => s,  // s is moved out
        None => String::new(),
    }
}

/// Move in closure
fn closure_move() {
    let data = vec![1, 2, 3];
    let closure = move || {
        println!("{:?}", data);
    };
    closure();
    // data is no longer available
}
