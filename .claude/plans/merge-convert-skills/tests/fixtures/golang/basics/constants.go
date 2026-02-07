// Test fixtures for Go constant definitions.
package basics

import "time"

// Simple constants
const Pi = 3.14159
const E = 2.71828

// Typed constants
const MaxSize int = 1024
const DefaultName string = "unknown"

// Constant block
const (
	StatusPending   = "pending"
	StatusActive    = "active"
	StatusCompleted = "completed"
)

// Iota constants
const (
	Sunday = iota
	Monday
	Tuesday
	Wednesday
	Thursday
	Friday
	Saturday
)

// Iota with expressions
const (
	_  = iota             // skip first value
	KB = 1 << (10 * iota) // 1 << 10 = 1024
	MB                    // 1 << 20
	GB                    // 1 << 30
	TB                    // 1 << 40
)

// Iota bit flags
const (
	FlagRead = 1 << iota // 1
	FlagWrite            // 2
	FlagExec             // 4
)

// Multiple iota in same const block
const (
	A, B = iota, iota + 10 // 0, 10
	C, D                   // 1, 11
	E, F                   // 2, 12
)

// Duration constants
const (
	Second = time.Second
	Minute = 60 * Second
	Hour   = 60 * Minute
)

// Private constants
const (
	maxRetries = 3
	timeout    = 30 * time.Second
)
