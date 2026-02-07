// RefCell interior mutability fixture

use std::cell::{Cell, RefCell};
use std::rc::Rc;

pub struct Counter {
    count: Cell<i32>,
}

impl Counter {
    pub fn new() -> Self {
        Counter { count: Cell::new(0) }
    }

    pub fn increment(&self) {
        self.count.set(self.count.get() + 1);
    }

    pub fn get(&self) -> i32 {
        self.count.get()
    }
}

pub struct MutableVec {
    data: RefCell<Vec<i32>>,
}

impl MutableVec {
    pub fn new() -> Self {
        MutableVec {
            data: RefCell::new(Vec::new()),
        }
    }

    pub fn push(&self, value: i32) {
        self.data.borrow_mut().push(value);
    }

    pub fn get(&self, index: usize) -> Option<i32> {
        self.data.borrow().get(index).copied()
    }

    pub fn len(&self) -> usize {
        self.data.borrow().len()
    }
}

pub struct SharedMutable {
    inner: Rc<RefCell<String>>,
}

impl SharedMutable {
    pub fn new(value: String) -> Self {
        SharedMutable {
            inner: Rc::new(RefCell::new(value)),
        }
    }

    pub fn append(&self, suffix: &str) {
        self.inner.borrow_mut().push_str(suffix);
    }

    pub fn get(&self) -> String {
        self.inner.borrow().clone()
    }

    pub fn clone_handle(&self) -> Self {
        SharedMutable {
            inner: Rc::clone(&self.inner),
        }
    }
}
