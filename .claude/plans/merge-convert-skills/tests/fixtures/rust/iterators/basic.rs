// Basic iterators fixture

pub fn sum_iter(items: &[i32]) -> i32 {
    items.iter().sum()
}

pub fn double_values(items: Vec<i32>) -> Vec<i32> {
    items.into_iter().map(|x| x * 2).collect()
}

pub fn filter_positive(items: Vec<i32>) -> Vec<i32> {
    items.into_iter().filter(|&x| x > 0).collect()
}

pub fn find_first_even(items: &[i32]) -> Option<i32> {
    items.iter().find(|&&x| x % 2 == 0).copied()
}

pub fn count_matches<T, P>(items: &[T], predicate: P) -> usize
where
    P: Fn(&T) -> bool,
{
    items.iter().filter(|x| predicate(*x)).count()
}

pub struct Range {
    current: i32,
    end: i32,
}

impl Range {
    pub fn new(start: i32, end: i32) -> Self {
        Range { current: start, end }
    }
}

impl Iterator for Range {
    type Item = i32;

    fn next(&mut self) -> Option<Self::Item> {
        if self.current < self.end {
            let value = self.current;
            self.current += 1;
            Some(value)
        } else {
            None
        }
    }
}

pub fn chain_iterators<T>(a: Vec<T>, b: Vec<T>) -> Vec<T> {
    a.into_iter().chain(b.into_iter()).collect()
}

pub fn zip_and_sum(a: Vec<i32>, b: Vec<i32>) -> Vec<i32> {
    a.into_iter().zip(b.into_iter()).map(|(x, y)| x + y).collect()
}
