// Test fixtures for Go select patterns.
package concurrency

import (
	"context"
	"fmt"
	"time"
)

// Basic select
func BasicSelect(ch1, ch2 <-chan string) string {
	select {
	case msg1 := <-ch1:
		return fmt.Sprintf("Received from ch1: %s", msg1)
	case msg2 := <-ch2:
		return fmt.Sprintf("Received from ch2: %s", msg2)
	}
}

// Select with send and receive
func SelectSendReceive(sendCh chan<- int, recvCh <-chan int) {
	select {
	case sendCh <- 42:
		fmt.Println("Sent value")
	case v := <-recvCh:
		fmt.Printf("Received: %d\n", v)
	}
}

// Select with default for polling
func Poll(ch <-chan int) (int, bool) {
	select {
	case v := <-ch:
		return v, true
	default:
		return 0, false
	}
}

// Select in a loop
func SelectLoop(ctx context.Context, dataCh <-chan int) {
	for {
		select {
		case <-ctx.Done():
			fmt.Println("Context cancelled")
			return
		case data := <-dataCh:
			fmt.Printf("Received: %d\n", data)
		}
	}
}

// Select with timer reset
func SelectWithTimerReset(ch <-chan int, timeout time.Duration) {
	timer := time.NewTimer(timeout)
	defer timer.Stop()

	for {
		select {
		case v := <-ch:
			fmt.Printf("Received: %d\n", v)
			if !timer.Stop() {
				<-timer.C
			}
			timer.Reset(timeout)
		case <-timer.C:
			fmt.Println("Timeout - no activity")
			return
		}
	}
}

// Select with ticker
func SelectWithTicker(ctx context.Context, interval time.Duration) {
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case t := <-ticker.C:
			fmt.Printf("Tick at %v\n", t)
		}
	}
}

// Priority select (check high priority first)
func PrioritySelect(highPriority, lowPriority <-chan int) int {
	// First, try high priority (non-blocking)
	select {
	case v := <-highPriority:
		return v
	default:
	}

	// Then, wait for either
	select {
	case v := <-highPriority:
		return v
	case v := <-lowPriority:
		return v
	}
}

// Select with channel closure detection
func SelectWithClosure(ch <-chan int) {
	for {
		select {
		case v, ok := <-ch:
			if !ok {
				fmt.Println("Channel closed")
				return
			}
			fmt.Printf("Received: %d\n", v)
		}
	}
}

// Multiplexer using select
func Multiplex(inputs ...<-chan int) <-chan int {
	output := make(chan int)

	go func() {
		defer close(output)

		// Keep track of active channels
		active := make([]<-chan int, len(inputs))
		copy(active, inputs)

		for len(active) > 0 {
			// Build select cases dynamically
			// Note: This is a simplified version
			for i, ch := range active {
				if ch == nil {
					continue
				}
				select {
				case v, ok := <-ch:
					if !ok {
						active[i] = nil
					} else {
						output <- v
					}
				default:
				}
			}
		}
	}()

	return output
}

// Rate limiter using select
type RateLimiter struct {
	ticker *time.Ticker
	tokens chan struct{}
}

func NewRateLimiter(rate time.Duration, burst int) *RateLimiter {
	rl := &RateLimiter{
		ticker: time.NewTicker(rate),
		tokens: make(chan struct{}, burst),
	}

	// Fill initial burst
	for i := 0; i < burst; i++ {
		rl.tokens <- struct{}{}
	}

	// Refill tokens
	go func() {
		for range rl.ticker.C {
			select {
			case rl.tokens <- struct{}{}:
			default:
			}
		}
	}()

	return rl
}

func (rl *RateLimiter) Wait(ctx context.Context) error {
	select {
	case <-rl.tokens:
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}

// Graceful shutdown with select
func GracefulShutdown(ctx context.Context, server interface{ Shutdown(context.Context) error }) error {
	shutdownCh := make(chan error, 1)

	go func() {
		shutdownCh <- server.Shutdown(ctx)
	}()

	select {
	case err := <-shutdownCh:
		return err
	case <-ctx.Done():
		return ctx.Err()
	}
}
