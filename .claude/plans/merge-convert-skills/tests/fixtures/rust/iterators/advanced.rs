// Advanced iterators fixture

use std::collections::HashMap;

pub fn group_by<T, K, F>(items: Vec<T>, key_fn: F) -> HashMap<K, Vec<T>>
where
    K: std::hash::Hash + Eq,
    F: Fn(&T) -> K,
{
    let mut groups: HashMap<K, Vec<T>> = HashMap::new();
    for item in items {
        let key = key_fn(&item);
        groups.entry(key).or_default().push(item);
    }
    groups
}

pub fn take_while_sum(items: &[i32], max: i32) -> Vec<i32> {
    let mut sum = 0;
    items
        .iter()
        .take_while(|&&x| {
            sum += x;
            sum <= max
        })
        .copied()
        .collect()
}

pub fn sliding_window(items: &[i32], size: usize) -> Vec<Vec<i32>> {
    items.windows(size).map(|w| w.to_vec()).collect()
}

pub fn enumerate_filter<T, P>(items: Vec<T>, predicate: P) -> Vec<(usize, T)>
where
    P: Fn(&T) -> bool,
{
    items
        .into_iter()
        .enumerate()
        .filter(|(_, item)| predicate(item))
        .collect()
}

pub fn flatten_nested(nested: Vec<Vec<i32>>) -> Vec<i32> {
    nested.into_iter().flatten().collect()
}

pub fn partition_result<T, E>(results: Vec<Result<T, E>>) -> (Vec<T>, Vec<E>) {
    let mut oks = Vec::new();
    let mut errs = Vec::new();

    for result in results {
        match result {
            Ok(val) => oks.push(val),
            Err(err) => errs.push(err),
        }
    }

    (oks, errs)
}

pub fn fold_with_index<T, U, F>(items: Vec<T>, init: U, f: F) -> U
where
    F: Fn(U, usize, T) -> U,
{
    items.into_iter().enumerate().fold(init, |acc, (i, item)| f(acc, i, item))
}

pub struct Fibonacci {
    curr: u64,
    next: u64,
}

impl Fibonacci {
    pub fn new() -> Self {
        Fibonacci { curr: 0, next: 1 }
    }
}

impl Iterator for Fibonacci {
    type Item = u64;

    fn next(&mut self) -> Option<Self::Item> {
        let new_next = self.curr.checked_add(self.next)?;
        self.curr = self.next;
        self.next = new_next;
        Some(self.curr)
    }
}

pub fn take_fibonacci(n: usize) -> Vec<u64> {
    Fibonacci::new().take(n).collect()
}
