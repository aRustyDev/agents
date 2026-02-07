// Test fixtures for Go channel patterns.
package concurrency

import (
	"context"
	"fmt"
	"time"
)

// Unbuffered channel
func UnbufferedChannel() {
	ch := make(chan int)

	go func() {
		ch <- 42
	}()

	value := <-ch
	fmt.Println(value)
}

// Buffered channel
func BufferedChannel() {
	ch := make(chan int, 3)

	ch <- 1
	ch <- 2
	ch <- 3

	fmt.Println(<-ch)
	fmt.Println(<-ch)
	fmt.Println(<-ch)
}

// Channel directions
func SendOnly(ch chan<- int) {
	ch <- 42
}

func ReceiveOnly(ch <-chan int) int {
	return <-ch
}

// Range over channel
func RangeChannel(ch <-chan int) []int {
	var results []int
	for v := range ch {
		results = append(results, v)
	}
	return results
}

// Select statement
func SelectPattern(ch1, ch2 <-chan int) int {
	select {
	case v := <-ch1:
		return v
	case v := <-ch2:
		return v
	}
}

// Select with default (non-blocking)
func NonBlockingReceive(ch <-chan int) (int, bool) {
	select {
	case v := <-ch:
		return v, true
	default:
		return 0, false
	}
}

// Select with timeout
func ReceiveWithTimeout(ch <-chan int, timeout time.Duration) (int, error) {
	select {
	case v := <-ch:
		return v, nil
	case <-time.After(timeout):
		return 0, fmt.Errorf("timeout after %v", timeout)
	}
}

// Select with context cancellation
func ReceiveWithContext(ctx context.Context, ch <-chan int) (int, error) {
	select {
	case v := <-ch:
		return v, nil
	case <-ctx.Done():
		return 0, ctx.Err()
	}
}

// Pipeline stage
func Square(input <-chan int) <-chan int {
	output := make(chan int)
	go func() {
		for n := range input {
			output <- n * n
		}
		close(output)
	}()
	return output
}

// Pipeline with multiple stages
func Pipeline(nums []int) <-chan int {
	// Generator
	gen := func(nums ...int) <-chan int {
		out := make(chan int)
		go func() {
			for _, n := range nums {
				out <- n
			}
			close(out)
		}()
		return out
	}

	// Chain stages
	c := gen(nums...)
	c = Square(c)
	c = Square(c)

	return c
}

// Broadcast pattern
func Broadcast(input <-chan int, numOutputs int) []<-chan int {
	outputs := make([]chan int, numOutputs)
	for i := range outputs {
		outputs[i] = make(chan int)
	}

	go func() {
		for v := range input {
			for _, out := range outputs {
				out <- v
			}
		}
		for _, out := range outputs {
			close(out)
		}
	}()

	// Convert to receive-only
	result := make([]<-chan int, numOutputs)
	for i, out := range outputs {
		result[i] = out
	}
	return result
}

// Semaphore using buffered channel
type Semaphore chan struct{}

func NewSemaphore(n int) Semaphore {
	return make(Semaphore, n)
}

func (s Semaphore) Acquire() {
	s <- struct{}{}
}

func (s Semaphore) Release() {
	<-s
}

// Channel of channels
func ChannelOfChannels() <-chan (<-chan int) {
	out := make(chan (<-chan int))

	go func() {
		for i := 0; i < 3; i++ {
			ch := make(chan int)
			out <- ch

			go func(id int) {
				ch <- id
				close(ch)
			}(i)
		}
		close(out)
	}()

	return out
}

// Done channel pattern
func DoWork(done <-chan struct{}) <-chan int {
	result := make(chan int)

	go func() {
		defer close(result)
		for i := 0; ; i++ {
			select {
			case <-done:
				return
			case result <- i:
			}
		}
	}()

	return result
}

// Nil channel for disabling select cases
func SelectWithNil(ch1, ch2 <-chan int, disable1 bool) int {
	var c1, c2 <-chan int
	if !disable1 {
		c1 = ch1
	}
	c2 = ch2

	select {
	case v := <-c1:
		return v
	case v := <-c2:
		return v
	}
}
