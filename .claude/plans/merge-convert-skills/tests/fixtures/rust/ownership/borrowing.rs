/// Test fixture: Borrowing
/// Tests shared and mutable borrows.

/// Shared borrow - reads but doesn't modify
fn view(data: &[i32]) -> i32 {
    data.iter().sum()
}

/// Mutable borrow - can modify
fn modify(data: &mut Vec<i32>) {
    data.push(42);
}

/// Multiple shared borrows are allowed
fn multiple_reads(a: &str, b: &str) -> String {
    format!("{}{}", a, b)
}

/// Only one mutable borrow at a time
fn exclusive_write(data: &mut Vec<i32>, value: i32) {
    data.push(value);
    data.sort();
}

/// Reborrowing
fn reborrow(data: &mut Vec<i32>) {
    // Reborrow as immutable
    let len = data.len();
    println!("Length: {}", len);

    // Reborrow as mutable
    data.push(len as i32);
}

/// Borrow in struct
struct BorrowedData<'a> {
    data: &'a [i32],
    name: &'a str,
}

impl<'a> BorrowedData<'a> {
    fn new(data: &'a [i32], name: &'a str) -> Self {
        BorrowedData { data, name }
    }

    fn sum(&self) -> i32 {
        self.data.iter().sum()
    }

    fn len(&self) -> usize {
        self.data.len()
    }
}

/// Temporary borrow
fn temporary_borrow(data: Vec<i32>) -> i32 {
    view(&data)  // Borrow for this call only
}

/// Method chaining with borrows
fn chain_borrows(data: &[i32]) -> Vec<i32> {
    data.iter()
        .filter(|x| **x > 0)
        .map(|x| x * 2)
        .collect()
}
