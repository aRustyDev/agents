// Test fixtures for Go goroutine patterns.
package concurrency

import (
	"fmt"
	"sync"
	"time"
)

// Simple goroutine
func SimpleGoroutine() {
	go func() {
		fmt.Println("Hello from goroutine")
	}()
}

// Goroutine with WaitGroup
func WaitForGoroutines() {
	var wg sync.WaitGroup

	for i := 0; i < 5; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			fmt.Printf("Worker %d done\n", id)
		}(i)
	}

	wg.Wait()
}

// Goroutine with closure
func ClosureGoroutine() {
	message := "Hello"

	go func() {
		fmt.Println(message)
	}()
}

// Multiple goroutines with sync
func ParallelProcessing(items []int) []int {
	var wg sync.WaitGroup
	var mu sync.Mutex
	results := make([]int, 0, len(items))

	for _, item := range items {
		wg.Add(1)
		go func(n int) {
			defer wg.Done()
			result := n * 2

			mu.Lock()
			results = append(results, result)
			mu.Unlock()
		}(item)
	}

	wg.Wait()
	return results
}

// Worker pool pattern
type Job struct {
	ID      int
	Payload string
}

type Result struct {
	JobID  int
	Output string
}

func WorkerPool(numWorkers int, jobs <-chan Job) <-chan Result {
	results := make(chan Result, len(jobs))
	var wg sync.WaitGroup

	for i := 0; i < numWorkers; i++ {
		wg.Add(1)
		go func(workerID int) {
			defer wg.Done()
			for job := range jobs {
				result := Result{
					JobID:  job.ID,
					Output: fmt.Sprintf("Worker %d processed: %s", workerID, job.Payload),
				}
				results <- result
			}
		}(i)
	}

	go func() {
		wg.Wait()
		close(results)
	}()

	return results
}

// Fan-out pattern
func FanOut(input <-chan int, numWorkers int) []<-chan int {
	outputs := make([]<-chan int, numWorkers)

	for i := 0; i < numWorkers; i++ {
		output := make(chan int)
		outputs[i] = output

		go func(out chan<- int) {
			for n := range input {
				out <- n * 2
			}
			close(out)
		}(output)
	}

	return outputs
}

// Fan-in pattern
func FanIn(inputs ...<-chan int) <-chan int {
	output := make(chan int)
	var wg sync.WaitGroup

	for _, input := range inputs {
		wg.Add(1)
		go func(in <-chan int) {
			defer wg.Done()
			for n := range in {
				output <- n
			}
		}(input)
	}

	go func() {
		wg.Wait()
		close(output)
	}()

	return output
}

// Rate limiting with goroutines
func RateLimitedProcessing(items []string, rateLimit time.Duration) {
	ticker := time.NewTicker(rateLimit)
	defer ticker.Stop()

	for _, item := range items {
		<-ticker.C
		go process(item)
	}
}

func process(item string) {
	fmt.Printf("Processing: %s\n", item)
}

// Goroutine with timeout
func WithTimeout(timeout time.Duration, fn func()) bool {
	done := make(chan struct{})

	go func() {
		fn()
		close(done)
	}()

	select {
	case <-done:
		return true
	case <-time.After(timeout):
		return false
	}
}

// Singleton with sync.Once
var instance *Singleton
var once sync.Once

type Singleton struct {
	value int
}

func GetInstance() *Singleton {
	once.Do(func() {
		instance = &Singleton{value: 42}
	})
	return instance
}

// Goroutine leak prevention
func SafeGoroutine(ctx <-chan struct{}) {
	go func() {
		for {
			select {
			case <-ctx:
				fmt.Println("Goroutine cancelled")
				return
			default:
				// Do work
				time.Sleep(100 * time.Millisecond)
			}
		}
	}()
}
