// Rc and Arc fixture

use std::rc::Rc;
use std::sync::Arc;

pub struct SharedData {
    value: i32,
}

impl SharedData {
    pub fn new(value: i32) -> Rc<Self> {
        Rc::new(SharedData { value })
    }

    pub fn get(&self) -> i32 {
        self.value
    }
}

pub fn share_data(data: Rc<SharedData>) -> (Rc<SharedData>, Rc<SharedData>) {
    let clone1 = Rc::clone(&data);
    let clone2 = Rc::clone(&data);
    (clone1, clone2)
}

pub struct ThreadSafeData {
    value: String,
}

impl ThreadSafeData {
    pub fn new(value: String) -> Arc<Self> {
        Arc::new(ThreadSafeData { value })
    }

    pub fn get(&self) -> &str {
        &self.value
    }
}

pub fn share_across_threads(data: Arc<ThreadSafeData>) -> Vec<Arc<ThreadSafeData>> {
    (0..4).map(|_| Arc::clone(&data)).collect()
}

pub fn rc_count<T>(rc: &Rc<T>) -> usize {
    Rc::strong_count(rc)
}

pub fn arc_count<T>(arc: &Arc<T>) -> usize {
    Arc::strong_count(arc)
}
