// Box smart pointer fixture

pub struct Node {
    value: i32,
    next: Option<Box<Node>>,
}

impl Node {
    pub fn new(value: i32) -> Self {
        Node { value, next: None }
    }

    pub fn with_next(value: i32, next: Node) -> Self {
        Node {
            value,
            next: Some(Box::new(next)),
        }
    }

    pub fn value(&self) -> i32 {
        self.value
    }

    pub fn next(&self) -> Option<&Node> {
        self.next.as_ref().map(|n| n.as_ref())
    }
}

pub enum BinaryTree<T> {
    Empty,
    Node {
        value: T,
        left: Box<BinaryTree<T>>,
        right: Box<BinaryTree<T>>,
    },
}

impl<T> BinaryTree<T> {
    pub fn leaf(value: T) -> Self {
        BinaryTree::Node {
            value,
            left: Box::new(BinaryTree::Empty),
            right: Box::new(BinaryTree::Empty),
        }
    }

    pub fn is_empty(&self) -> bool {
        matches!(self, BinaryTree::Empty)
    }
}

pub fn boxed_value<T>(value: T) -> Box<T> {
    Box::new(value)
}

pub fn unbox<T>(boxed: Box<T>) -> T {
    *boxed
}
