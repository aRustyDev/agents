// Test fixtures for Go interface definitions.
package interfaces

import (
	"fmt"
	"io"
)

// Simple interface
type Greeter interface {
	Greet() string
}

// Interface with multiple methods
type Animal interface {
	Speak() string
	Move() string
	Name() string
}

// Empty interface (any)
type Any interface{}

// Interface with embedded interfaces
type ReadWriter interface {
	io.Reader
	io.Writer
}

// Interface with embedded and own methods
type ReadWriteCloser interface {
	io.Reader
	io.Writer
	Close() error
}

// Interface used for type constraint
type Comparable interface {
	Compare(other Comparable) int
}

// Interface with error return
type Repository interface {
	Find(id string) (interface{}, error)
	Save(entity interface{}) error
	Delete(id string) error
}

// Private interface
type validator interface {
	validate() error
}

// Implementation of Greeter
type Person struct {
	name string
}

func (p Person) Greet() string {
	return fmt.Sprintf("Hello, I'm %s", p.name)
}

// Implementation of Animal
type Dog struct {
	name string
}

func (d Dog) Speak() string {
	return "Woof!"
}

func (d Dog) Move() string {
	return "Running on four legs"
}

func (d Dog) Name() string {
	return d.name
}

// Type assertion
func GreetIfPossible(v interface{}) string {
	if g, ok := v.(Greeter); ok {
		return g.Greet()
	}
	return "Cannot greet"
}

// Type switch
func Describe(v interface{}) string {
	switch t := v.(type) {
	case string:
		return fmt.Sprintf("String: %s", t)
	case int:
		return fmt.Sprintf("Integer: %d", t)
	case Greeter:
		return fmt.Sprintf("Greeter: %s", t.Greet())
	default:
		return fmt.Sprintf("Unknown type: %T", t)
	}
}

// Interface as function parameter
func MakeGreeting(g Greeter) string {
	return g.Greet()
}

// Interface as return type
func NewGreeter(name string) Greeter {
	return Person{name: name}
}

// Slice of interfaces
func GreetAll(greeters []Greeter) []string {
	result := make([]string, len(greeters))
	for i, g := range greeters {
		result[i] = g.Greet()
	}
	return result
}
