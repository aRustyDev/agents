// Test fixtures for Go error handling patterns.
package error_handling

import (
	"errors"
	"fmt"
	"io"
	"os"
)

// Standard error checking pattern
func ReadFile(path string) ([]byte, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	return io.ReadAll(f)
}

// Error wrapping with context
func ProcessFile(path string) error {
	data, err := ReadFile(path)
	if err != nil {
		return fmt.Errorf("failed to read file %s: %w", path, err)
	}

	if err := processData(data); err != nil {
		return fmt.Errorf("failed to process file %s: %w", path, err)
	}

	return nil
}

func processData(data []byte) error {
	if len(data) == 0 {
		return errors.New("empty data")
	}
	return nil
}

// Custom error type
type ValidationError struct {
	Field   string
	Message string
}

func (e *ValidationError) Error() string {
	return fmt.Sprintf("validation error on %s: %s", e.Field, e.Message)
}

// Error type checking
func IsValidationError(err error) bool {
	var ve *ValidationError
	return errors.As(err, &ve)
}

// Sentinel errors
var (
	ErrNotFound     = errors.New("not found")
	ErrUnauthorized = errors.New("unauthorized")
	ErrInvalidInput = errors.New("invalid input")
)

// Error checking with sentinel
func FindUser(id string) (*User, error) {
	if id == "" {
		return nil, ErrInvalidInput
	}

	user, exists := userDB[id]
	if !exists {
		return nil, ErrNotFound
	}

	return user, nil
}

type User struct {
	ID   string
	Name string
}

var userDB = map[string]*User{}

// Multiple error returns
func ValidateAndProcess(data []byte) (result []byte, warnings []string, err error) {
	if len(data) == 0 {
		return nil, nil, ErrInvalidInput
	}

	// Process and collect warnings
	result = data
	if len(data) < 10 {
		warnings = append(warnings, "data is very short")
	}

	return result, warnings, nil
}

// Error interface implementation
type HTTPError struct {
	StatusCode int
	Message    string
}

func (e *HTTPError) Error() string {
	return fmt.Sprintf("HTTP %d: %s", e.StatusCode, e.Message)
}

func (e *HTTPError) Is(target error) bool {
	t, ok := target.(*HTTPError)
	if !ok {
		return false
	}
	return e.StatusCode == t.StatusCode
}

// Panic and recover
func SafeExecute(fn func()) (err error) {
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("panic recovered: %v", r)
		}
	}()

	fn()
	return nil
}

// Error aggregation
type MultiError struct {
	Errors []error
}

func (m *MultiError) Error() string {
	if len(m.Errors) == 0 {
		return "no errors"
	}
	if len(m.Errors) == 1 {
		return m.Errors[0].Error()
	}
	return fmt.Sprintf("%d errors occurred", len(m.Errors))
}

func (m *MultiError) Add(err error) {
	if err != nil {
		m.Errors = append(m.Errors, err)
	}
}

func (m *MultiError) HasErrors() bool {
	return len(m.Errors) > 0
}

// Unwrap for error chains
func (m *MultiError) Unwrap() []error {
	return m.Errors
}
