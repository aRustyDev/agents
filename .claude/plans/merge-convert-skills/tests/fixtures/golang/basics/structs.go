// Test fixtures for Go struct definitions.
package basics

import "time"

// Simple struct
type User struct {
	ID        int
	Name      string
	Email     string
	CreatedAt time.Time
}

// Struct with tags
type JSONUser struct {
	ID        int       `json:"id"`
	Name      string    `json:"name"`
	Email     string    `json:"email,omitempty"`
	CreatedAt time.Time `json:"created_at"`
}

// Struct with embedded types
type Base struct {
	ID        int
	CreatedAt time.Time
	UpdatedAt time.Time
}

type Article struct {
	Base
	Title   string
	Content string
	Author  *User
}

// Struct with private fields
type counter struct {
	value int
	max   int
}

// Struct with pointer fields
type Node struct {
	Value int
	Left  *Node
	Right *Node
}

// Struct with slice and map fields
type Config struct {
	Name     string
	Enabled  bool
	Tags     []string
	Settings map[string]string
}

// Struct with function field
type Handler struct {
	Name    string
	Process func(data []byte) error
}

// Struct method with value receiver
func (u User) FullName() string {
	return u.Name
}

// Struct method with pointer receiver
func (c *counter) Increment() int {
	if c.value < c.max {
		c.value++
	}
	return c.value
}

// Struct method with multiple returns
func (c *counter) IncrementBy(n int) (int, error) {
	if c.value+n > c.max {
		return c.value, ErrMaxExceeded
	}
	c.value += n
	return c.value, nil
}

var ErrMaxExceeded = Error("max exceeded")

type Error string

func (e Error) Error() string {
	return string(e)
}
