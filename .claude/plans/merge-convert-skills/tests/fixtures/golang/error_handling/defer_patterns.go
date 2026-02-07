// Test fixtures for Go defer patterns.
package error_handling

import (
	"database/sql"
	"fmt"
	"os"
	"sync"
)

// Basic defer for cleanup
func ReadFileContent(path string) (string, error) {
	f, err := os.Open(path)
	if err != nil {
		return "", err
	}
	defer f.Close()

	// Read file content
	info, err := f.Stat()
	if err != nil {
		return "", err
	}

	data := make([]byte, info.Size())
	_, err = f.Read(data)
	if err != nil {
		return "", err
	}

	return string(data), nil
}

// Multiple defers (LIFO order)
func MultipleDefers() {
	defer fmt.Println("First")
	defer fmt.Println("Second")
	defer fmt.Println("Third")
	// Output: Third, Second, First
}

// Defer with mutex unlock
func SafeIncrement(mu *sync.Mutex, counter *int) {
	mu.Lock()
	defer mu.Unlock()
	*counter++
}

// Defer in loop (be careful!)
func ProcessFiles(paths []string) error {
	var files []*os.File
	defer func() {
		for _, f := range files {
			f.Close()
		}
	}()

	for _, path := range paths {
		f, err := os.Open(path)
		if err != nil {
			return err
		}
		files = append(files, f)
	}

	// Process files...
	return nil
}

// Defer with named return values
func OpenFile(path string) (f *os.File, err error) {
	f, err = os.Open(path)
	if err != nil {
		return nil, err
	}

	defer func() {
		if err != nil {
			f.Close()
		}
	}()

	// More operations that might fail
	info, err := f.Stat()
	if err != nil {
		return nil, err
	}

	if !info.Mode().IsRegular() {
		err = fmt.Errorf("not a regular file")
		return nil, err
	}

	return f, nil
}

// Defer for database transaction
func WithTransaction(db *sql.DB, fn func(*sql.Tx) error) error {
	tx, err := db.Begin()
	if err != nil {
		return err
	}

	defer func() {
		if p := recover(); p != nil {
			tx.Rollback()
			panic(p)
		}
	}()

	if err := fn(tx); err != nil {
		tx.Rollback()
		return err
	}

	return tx.Commit()
}

// Defer for timing
func TimedOperation(name string) func() {
	start := now()
	return func() {
		elapsed := now() - start
		fmt.Printf("%s took %d ms\n", name, elapsed)
	}
}

func now() int64 {
	// Simplified for example
	return 0
}

func SomeOperation() {
	defer TimedOperation("SomeOperation")()
	// Do work...
}

// Defer for resource pool
type Pool struct {
	resources chan interface{}
}

func (p *Pool) Acquire() interface{} {
	return <-p.resources
}

func (p *Pool) Release(r interface{}) {
	p.resources <- r
}

func UsePooledResource(pool *Pool) error {
	resource := pool.Acquire()
	defer pool.Release(resource)

	// Use resource...
	return nil
}

// Defer with closure capturing loop variable
func PrintNumbers(nums []int) {
	for _, n := range nums {
		n := n // Capture loop variable
		defer func() {
			fmt.Println(n)
		}()
	}
}

// Defer for cleanup with error handling
type Resource struct {
	name string
}

func (r *Resource) Close() error {
	fmt.Printf("Closing %s\n", r.name)
	return nil
}

func WithResource(name string, fn func(*Resource) error) (err error) {
	r := &Resource{name: name}
	defer func() {
		if closeErr := r.Close(); closeErr != nil && err == nil {
			err = closeErr
		}
	}()

	return fn(r)
}
