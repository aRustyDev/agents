/// Test fixture: Visibility
/// Tests pub, pub(crate), pub(super), and private visibility.

/// Public struct with mixed visibility fields
pub struct Config {
    /// Public field
    pub name: String,
    /// Private field (default)
    secret_key: String,
    /// Crate-visible field
    pub(crate) cache_size: usize,
}

impl Config {
    /// Public constructor
    pub fn new(name: &str) -> Self {
        Config {
            name: name.to_string(),
            secret_key: "default".to_string(),
            cache_size: 1024,
        }
    }

    /// Private method
    fn validate(&self) -> bool {
        !self.secret_key.is_empty()
    }

    /// Crate-visible method
    pub(crate) fn reset_cache(&mut self) {
        self.cache_size = 0;
    }
}

/// Private module
mod internal {
    pub struct InternalData {
        pub value: i32,
    }

    impl InternalData {
        pub fn new(value: i32) -> Self {
            InternalData { value }
        }
    }
}

/// Public module
pub mod api {
    /// Re-export from internal
    pub use super::Config;

    /// Public function
    pub fn create_config(name: &str) -> Config {
        Config::new(name)
    }

    /// Private helper
    fn helper() {}
}

/// pub(super) visibility
mod parent {
    pub mod child {
        /// Visible to parent module
        pub(super) fn child_helper() -> i32 {
            42
        }

        /// Private to child
        fn private_child() {}
    }

    pub fn use_child() -> i32 {
        child::child_helper()
    }
}

/// pub(in path) visibility
mod outer {
    pub mod inner {
        pub mod deep {
            /// Visible to outer module
            pub(in crate::outer) fn deep_fn() -> &'static str {
                "deep"
            }
        }
    }

    pub fn access_deep() -> &'static str {
        inner::deep::deep_fn()
    }
}

/// Trait visibility
pub trait PublicTrait {
    fn public_method(&self);
}

trait PrivateTrait {
    fn private_method(&self);
}

/// Re-exports
pub use api::create_config;
