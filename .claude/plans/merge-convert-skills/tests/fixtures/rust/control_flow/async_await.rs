/// Test fixture: Async/Await
/// Tests async functions and futures.

use std::future::Future;

/// Simple async function
async fn fetch_data() -> String {
    // Simulate async work
    String::from("data")
}

/// Async with parameters
async fn fetch_url(url: &str) -> Result<String, String> {
    if url.starts_with("http") {
        Ok(format!("Content from {}", url))
    } else {
        Err("Invalid URL".to_string())
    }
}

/// Async with .await
async fn process_urls(urls: Vec<&str>) -> Vec<String> {
    let mut results = Vec::new();
    for url in urls {
        if let Ok(content) = fetch_url(url).await {
            results.push(content);
        }
    }
    results
}

/// Async method
struct Client {
    base_url: String,
}

impl Client {
    async fn get(&self, path: &str) -> String {
        format!("{}/{}", self.base_url, path)
    }

    async fn post(&self, path: &str, body: &str) -> Result<String, String> {
        Ok(format!("Posted {} to {}/{}", body, self.base_url, path))
    }
}

/// Returning impl Future
fn make_future() -> impl Future<Output = i32> {
    async { 42 }
}

/// Async closure (requires nightly or async_closure feature)
// let closure = async |x: i32| -> i32 { x * 2 };

/// Async trait (using async_trait crate pattern)
// #[async_trait]
pub trait AsyncReader {
    // async fn read(&mut self) -> Vec<u8>;
    fn read(&mut self) -> impl Future<Output = Vec<u8>>;
}

/// Async with error handling
async fn fallible_async() -> Result<i32, &'static str> {
    let result = async_compute().await?;
    Ok(result * 2)
}

async fn async_compute() -> Result<i32, &'static str> {
    Ok(21)
}

/// Parallel async (conceptual - needs tokio/async-std)
async fn parallel_tasks() {
    let task1 = fetch_data();
    let task2 = fetch_data();

    // In practice, use join! or similar
    let r1 = task1.await;
    let r2 = task2.await;

    println!("{} {}", r1, r2);
}

/// Async with timeout (conceptual)
async fn with_timeout<T, F: Future<Output = T>>(future: F, _duration: u64) -> Option<T> {
    // In practice, use tokio::time::timeout or similar
    Some(future.await)
}

/// Async stream pattern (conceptual)
struct AsyncIter {
    count: i32,
}

impl AsyncIter {
    async fn next(&mut self) -> Option<i32> {
        if self.count < 10 {
            self.count += 1;
            Some(self.count)
        } else {
            None
        }
    }
}
