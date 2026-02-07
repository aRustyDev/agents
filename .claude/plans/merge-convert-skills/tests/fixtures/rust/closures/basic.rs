// Basic closures fixture

pub fn apply<F, T>(f: F, value: T) -> T
where
    F: Fn(T) -> T,
{
    f(value)
}

pub fn apply_mut<F, T>(mut f: F, value: T) -> T
where
    F: FnMut(T) -> T,
{
    f(value)
}

pub fn apply_once<F, T>(f: F, value: T) -> T
where
    F: FnOnce(T) -> T,
{
    f(value)
}

pub fn make_adder(x: i32) -> impl Fn(i32) -> i32 {
    move |y| x + y
}

pub fn make_counter() -> impl FnMut() -> i32 {
    let mut count = 0;
    move || {
        count += 1;
        count
    }
}

pub fn compose<F, G, A, B, C>(f: F, g: G) -> impl Fn(A) -> C
where
    F: Fn(A) -> B,
    G: Fn(B) -> C,
{
    move |x| g(f(x))
}

pub fn filter_map<T, U, F>(items: Vec<T>, f: F) -> Vec<U>
where
    F: Fn(T) -> Option<U>,
{
    items.into_iter().filter_map(f).collect()
}
